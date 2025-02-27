import tkinter as tk
import random
import json
from tkinter import messagebox
from PIL import Image, ImageTk
from typing import Optional

def bot_ai_decision(
    bot_cards: list[int],
    dealer_upcard: Optional[int],
    deck_state: list[str],
    dealer_cards: list[int],
    player_cards: list[int],
    bot_name: str
) -> bool:
    """
    A simplified 'Basic Strategy' decision logic for Blackjack (Hit or Stand).
    We only handle 'hard totals' (no special 'soft hand' logic).

    Parameters:
      - bot_cards: current list of integer values for the bot's cards (already with Aces possibly converted to 1 if needed)
      - dealer_upcard: integer value of the dealer's first card (None if not available)
      - deck_state: current list of remaining cards in the deck (string filenames)
      - dealer_cards: dealer's full hand (integer list)
      - player_cards: player's full hand (integer list)
      - bot_name: "Bot1" or "Bot2"

    Returns:
      True => the bot decides to 'Hit'
      False => the bot decides to 'Stand'
    """

    # If the dealer's upcard is unknown for some reason, treat it as 10
    if dealer_upcard is None:
        dealer_upcard = 10

    bot_total = sum(bot_cards)

    # 1) If bot's total < 12 => always Hit
    if bot_total < 12:
        return True

    # 2) If exactly 12 => Stand only if dealer's upcard is 4..6, otherwise Hit
    if bot_total == 12:
        if 4 <= dealer_upcard <= 6:
            return False  # Stand
        else:
            return True   # Hit

    # 3) If total in [13..16] => Stand if dealer_upcard in [2..6], else Hit
    if 13 <= bot_total <= 16:
        if 2 <= dealer_upcard <= 6:
            return False  # Stand
        else:
            return True   # Hit

    # 4) If total >= 17 => Stand
    if bot_total >= 17:
        return False

    # Default fallback (should never reach here in normal conditions):
    return False


class Player:
    """
    Represents a single participant (player, bot, dealer).
    """
    def __init__(self, name: str, is_bot=False, is_dealer=False):
        self.name = name
        self.is_bot = is_bot
        self.is_dealer = is_dealer

        self.cards_values = []       # list of integers (2..11)
        self.spot = 0                # next index for a new card
        self.card_labels = []        # Label widgets in Tkinter UI
        self.real_card_images = [None]*5  # store real images for "face-down" logic

    def reset(self):
        """Reset the player's state for a new round."""
        self.cards_values.clear()
        self.spot = 0
        self.real_card_images = [None]*5

    def add_card_value(self, value: int) -> bool:
        """Adds a card value if there's space (max 5)."""
        if self.spot >= 5:
            return False
        self.cards_values.append(value)
        self.spot += 1
        return True

    def calculate_total(self) -> int:
        """Sum of the card values (without re-checking Aces)."""
        return sum(self.cards_values)

    def convert_aces_if_needed(self):
        """If total > 21 and we have Aces=11, convert them to 1 until bust is gone or no more Aces."""
        while self.calculate_total() > 21 and 11 in self.cards_values:
            idx = self.cards_values.index(11)
            self.cards_values[idx] = 1

    def is_bust(self) -> bool:
        """True if total > 21."""
        return self.calculate_total() > 21


class Game:
    """
    Main Blackjack logic + Tkinter UI (OOP style).
    """

    def __init__(self):
        # Global stats
        self.player_wins = 0
        self.dealer_wins = 0
        self.ties = 0

        # Tkinter
        self.root = tk.Tk()
        self.root.title("Casino Blackjack (OOP + Basic Strategy Bot)")
        self.root.configure(bg="#0B3B0B")
        self.root.geometry("1120x630")

        self.deck = []
        self.dealer_hidden_card_img = None

        # Participants
        self.dealer = Player("Dealer", is_dealer=True)
        self.player = Player("Player")
        self.bot1 = Player("Bot1", is_bot=True)
        self.bot2 = Player("Bot2", is_bot=True)
        self.players = [self.dealer, self.bot1, self.player, self.bot2]

        self.blackjack_status = {"dealer": "no", "player": "no"}

        # Load back image
        self.back_img = self.resize_card("images/cards/back.png", (126,182))

        # Build UI
        self.setup_ui()

        # Deal initial cards
        self.shuffle_deck()

    def add_player(self, player: Player):
        self.players.append(player)

    def save_game(self, filename: str):
        """
        Example: save global scores + each player's cards to JSON.
        """
        state = {
            "player_wins": self.player_wins,
            "dealer_wins": self.dealer_wins,
            "ties": self.ties,
            "players": []
        }
        for p in self.players:
            data_p = {
                "name": p.name,
                "is_bot": p.is_bot,
                "is_dealer": p.is_dealer,
                "cards_values": p.cards_values
            }
            state["players"].append(data_p)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)

    @classmethod
    def load_game(cls, filename: str) -> 'Game':
        with open(filename, "r", encoding="utf-8") as f:
            state = json.load(f)

        new_game = cls()
        new_game.player_wins = state["player_wins"]
        new_game.dealer_wins = state["dealer_wins"]
        new_game.ties = state["ties"]

        for i, pdata in enumerate(state["players"]):
            new_game.players[i].cards_values = pdata["cards_values"]

        return new_game

    def finish_game(self):
        self.root.quit()

    def win_condition(self):
        pass

    def lose_condition(self):
        pass

    def step(self):
        pass

    def get_current_state(self):
        return {
            "player_wins": self.player_wins,
            "dealer_wins": self.dealer_wins,
            "ties": self.ties,
            "dealer_cards": self.dealer.cards_values,
            "player_cards": self.player.cards_values,
            "bot1_cards": self.bot1.cards_values,
            "bot2_cards": self.bot2.cards_values
        }

    def run(self):
        self.root.mainloop()

    # ------------------- UI Setup ----------------------
    def setup_ui(self):
        dealer_frame = tk.LabelFrame(
            self.root,
            text="Dealer",
            bg="#0B3B0B",
            fg="white",
            bd=2,
            font=("Verdana", 17, "bold"),
            labelanchor="n"
        )
        dealer_frame.pack(pady=14)

        for i in range(5):
            lbl = tk.Label(dealer_frame, text="", bg="#0B3B0B")
            lbl.grid(row=0, column=i, padx=7, pady=7)
            self.dealer.card_labels.append(lbl)

        middle_frame = tk.Frame(self.root, bg="#0B3B0B")
        middle_frame.pack()

        bot1_frame = tk.LabelFrame(
            middle_frame,
            text="Bot1",
            bg="#0B3B0B",
            fg="white",
            bd=2,
            font=("Verdana", 17, "bold"),
            labelanchor="n"
        )
        bot1_frame.grid(row=0, column=0, padx=28, pady=14)

        for i in range(5):
            lbl = tk.Label(bot1_frame, text="", bg="#0B3B0B")
            lbl.grid(row=0, column=i, padx=7, pady=7)
            self.bot1.card_labels.append(lbl)

        player_frame = tk.LabelFrame(
            middle_frame,
            text="Player",
            bg="#0B3B0B",
            fg="white",
            bd=2,
            font=("Verdana", 17, "bold"),
            labelanchor="n"
        )
        player_frame.grid(row=0, column=1, padx=28, pady=14)

        for i in range(5):
            lbl = tk.Label(player_frame, text="", bg="#0B3B0B")
            lbl.grid(row=0, column=i, padx=7, pady=7)
            self.player.card_labels.append(lbl)

        global player_score_label
        player_score_label = tk.Label(
            player_frame,
            text="Player Score: 0",
            bg="#0B3B0B",
            fg="white",
            font=("Verdana", 14, "bold")
        )
        player_score_label.grid(row=1, column=0, columnspan=5, pady=7)

        bot2_frame = tk.LabelFrame(
            middle_frame,
            text="Bot2",
            bg="#0B3B0B",
            fg="white",
            bd=2,
            font=("Verdana", 17, "bold"),
            labelanchor="n"
        )
        bot2_frame.grid(row=0, column=2, padx=28, pady=14)

        for i in range(5):
            lbl = tk.Label(bot2_frame, text="", bg="#0B3B0B")
            lbl.grid(row=0, column=i, padx=7, pady=7)
            self.bot2.card_labels.append(lbl)

        button_frame = tk.Frame(self.root, bg="#0B3B0B")
        button_frame.pack(pady=14)

        global card_button, stand_button
        shuffle_button = tk.Button(
            button_frame,
            text="Shuffle Deck",
            font=("Helvetica", 14),
            bg="white",
            fg="black",
            command=self.shuffle_deck
        )
        shuffle_button.grid(row=0, column=0, padx=14)

        card_button = tk.Button(
            button_frame,
            text="Hit Me!",
            font=("Helvetica", 14),
            bg="white",
            fg="black",
            command=self.player_hit
        )
        card_button.grid(row=0, column=1, padx=14)

        stand_button = tk.Button(
            button_frame,
            text="Stand!",
            font=("Helvetica", 14),
            bg="white",
            fg="black",
            command=self.stand
        )
        stand_button.grid(row=0, column=2, padx=14)

        global scoreboard_label
        scoreboard_label = tk.Label(
            self.root,
            text="Wins: 0  Losses: 0  Ties: 0",
            bg="#0B3B0B",
            fg="white",
            font=("Verdana", 14, "bold")
        )
        scoreboard_label.place(relx=0.98, rely=0.02, anchor="ne")
        self.update_scoreboard_label()

    # ------------------- Core game logic ----------------------
    def resize_card(self, card_path, size=(126,182)):
        img = Image.open(card_path)
        img = img.resize(size)
        return ImageTk.PhotoImage(img)

    def update_player_score_label(self):
        """Update player's visible score."""
        player_score_label.config(text=f"Player Score: {self.player.calculate_total()}")

    def shuffle_deck(self):
        suits = ["diamonds", "clubs", "hearts", "spades"]
        values = range(2, 15)  # 14 -> Ace
        self.deck = [f"{v}_of_{s}" for s in suits for v in values]
        random.shuffle(self.deck)

        self.dealer.reset()
        self.player.reset()
        self.bot1.reset()
        self.bot2.reset()
        self.blackjack_status = {"dealer": "no", "player": "no"}
        self.dealer_hidden_card_img = None

        for p in self.players:
            for lbl in p.card_labels:
                lbl.config(image="", text="")

        player_score_label.config(text="Player Score: 0")

        # Deal initial
        self.deal_card_to(self.dealer)
        self.deal_card_to(self.dealer)
        self.deal_card_to(self.player)
        self.deal_card_to(self.player)
        self.deal_card_to(self.bot1)
        self.deal_card_to(self.bot1)
        self.deal_card_to(self.bot2)
        self.deal_card_to(self.bot2)

        card_button.config(state="normal")
        stand_button.config(state="normal")

        self.root.title(f"Cards left: {len(self.deck)}")

    def deal_card_to(self, person: Player):
        """Deal one card to the 'person'."""
        if len(self.deck) == 0:
            self.root.title("No more cards in the deck!")
            return

        card_name = random.choice(self.deck)
        self.deck.remove(card_name)
        card_val = self.get_card_value(card_name)

        if not person.add_card_value(card_val):
            return

        real_card_img = self.resize_card(f"images/cards/{card_name}.png", (126,182))
        idx = person.spot - 1
        person.real_card_images[idx] = real_card_img

        # Dealer's 2nd card is face-down
        if person.is_dealer and person.spot == 2:
            self.dealer_hidden_card_img = real_card_img
            lbl = person.card_labels[1]
            lbl.config(image=self.back_img)
            lbl.image = self.back_img
        # Bots' cards are always hidden
        elif person.is_bot:
            lbl = person.card_labels[idx]
            lbl.config(image=self.back_img)
            lbl.image = self.back_img
        else:
            # Player or dealer's other cards
            lbl = person.card_labels[idx]
            lbl.config(image=real_card_img)
            lbl.image = real_card_img

        # Check player's or dealer's 21/bust
        if person == self.player:
            self.check_blackjack_or_bust("player")
            self.update_player_score_label()
        elif person.is_dealer:
            self.check_blackjack_or_bust("dealer")

        self.root.title(f"Cards left: {len(self.deck)}")

    def get_card_value(self, card_name: str) -> int:
        value = int(card_name.split("_", 1)[0])
        if value == 14:
            return 11  # Ace
        elif value in [11, 12, 13]:
            return 10  # J, Q, K
        else:
            return value

    def check_blackjack_or_bust(self, player_type: str):
        if player_type == "player":
            self.player.convert_aces_if_needed()
            total = self.player.calculate_total()
            if total == 21:
                self.blackjack_status["player"] = "yes"
            elif total > 21:
                self.blackjack_status["player"] = "bust"
            self.check_immediate_outcomes()
        elif player_type == "dealer":
            self.dealer.convert_aces_if_needed()
            total = self.dealer.calculate_total()
            if total == 21:
                self.blackjack_status["dealer"] = "yes"
            elif total > 21:
                self.blackjack_status["dealer"] = "bust"
            self.check_immediate_outcomes()

    def check_immediate_outcomes(self):
        p_status = self.blackjack_status["player"]
        d_status = self.blackjack_status["dealer"]
        p_total = self.player.calculate_total()
        d_total = self.dealer.calculate_total()

        if d_status == "yes" and p_status == "yes":
            self.show_result_and_disable_buttons(
                "Push!",
                "It's a tie! Both have 21.",
                outcome="tie"
            )
        elif d_status == "yes":
            self.show_result_and_disable_buttons(
                "Dealer Wins!",
                "Dealer got 21!",
                outcome="dealer"
            )
        elif p_status == "yes":
            self.show_result_and_disable_buttons(
                "Player Wins!",
                "Player got 21!",
                outcome="player"
            )
        elif p_status == "bust":
            self.show_result_and_disable_buttons(
                "Player Bust!",
                f"Player is over 21! Total: {p_total}",
                outcome="dealer"
            )

    def player_hit(self):
        self.deal_card_to(self.player)

    def stand(self):
        card_button.config(state="disabled")
        stand_button.config(state="disabled")

        if self.blackjack_status["player"] in ["bust", "yes"]:
            return
        if self.blackjack_status["dealer"] == "yes":
            return

        # Let both bots play using the "bot_ai_decision" function
        self.play_for_bot(self.bot1)
        self.play_for_bot(self.bot2)

        # Dealer draws up to 17
        while True:
            self.dealer.convert_aces_if_needed()
            if self.dealer.calculate_total() < 17 and self.dealer.spot < 5:
                self.deal_card_to(self.dealer)
            else:
                break

        self.final_comparison()

    def play_for_bot(self, bot: Player):
        """
        Bot loop: calls our 'bot_ai_decision' for each step (Hit/Stand).
        Repeat until the bot stands, busts, or has 5 cards.
        """
        from functools import partial

        while True:
            bot.convert_aces_if_needed()
            if bot.is_bust() or len(bot.cards_values) >= 5:
                break

            # Dealer's upcard is the first card if available
            dealer_upcard = self.dealer.cards_values[0] if len(self.dealer.cards_values) > 0 else None

            # Call the Basic Strategy logic
            want_hit = bot_ai_decision(
                bot_cards=bot.cards_values,
                dealer_upcard=dealer_upcard,
                deck_state=self.deck,
                dealer_cards=self.dealer.cards_values,
                player_cards=self.player.cards_values,
                bot_name=bot.name
            )

            if want_hit:
                self.deal_card_to(bot)
            else:
                break

    def final_comparison(self):
        """
        Compare player's & dealer's totals, and compare each bot to the dealer.
        Then reveal all hidden cards (bots + dealer's second card).
        """
        # Reveal bots
        self.reveal_bot_cards(self.bot1)
        self.reveal_bot_cards(self.bot2)

        self.dealer.convert_aces_if_needed()
        d_total = self.dealer.calculate_total()
        dealer_bust = (d_total > 21)

        self.player.convert_aces_if_needed()
        p_total = self.player.calculate_total()
        player_bust = (p_total > 21)

        bot1_result = self.compare_with_dealer(self.bot1)
        bot2_result = self.compare_with_dealer(self.bot2)

        if dealer_bust:
            self.show_aggregate_result(
                dealer_total=d_total,
                player_total=p_total,
                player_outcome="Win (Dealer Bust)",
                bot1_result="Win (Dealer Bust)",
                bot2_result="Win (Dealer Bust)"
            )
            self.show_result_and_disable_buttons(
                "Player Wins!",
                f"Dealer busted! Player total: {p_total}",
                outcome="player"
            )
        else:
            if player_bust:
                player_outcome = "Bust"
                outcome_for_stats = "dealer"
            else:
                if p_total > d_total:
                    player_outcome = "Win"
                    outcome_for_stats = "player"
                elif p_total < d_total:
                    player_outcome = "Lose"
                    outcome_for_stats = "dealer"
                else:
                    player_outcome = "Tie"
                    outcome_for_stats = "tie"

            self.show_aggregate_result(
                dealer_total=d_total,
                player_total=p_total,
                player_outcome=player_outcome,
                bot1_result=bot1_result,
                bot2_result=bot2_result
            )

            if outcome_for_stats == "player":
                self.show_result_and_disable_buttons(
                    "Player Wins!",
                    f"Player: {p_total}, Dealer: {d_total}",
                    outcome="player"
                )
            elif outcome_for_stats == "dealer":
                self.show_result_and_disable_buttons(
                    "Dealer Wins!",
                    f"Dealer: {d_total}, Player: {p_total}",
                    outcome="dealer"
                )
            else:
                self.show_result_and_disable_buttons(
                    "Push!",
                    f"Tie! Dealer: {d_total}, Player: {p_total}",
                    outcome="tie"
                )

    def reveal_bot_cards(self, bot: Player):
        """Flip all bot's cards face-up at the end."""
        if not bot.is_bot:
            return
        for i in range(bot.spot):
            lbl = bot.card_labels[i]
            real_img = bot.real_card_images[i]
            if real_img is not None:
                lbl.config(image=real_img)
                lbl.image = real_img

    def compare_with_dealer(self, bot: Player) -> str:
        bot.convert_aces_if_needed()
        b_total = bot.calculate_total()
        if b_total > 21:
            return "Bust"

        self.dealer.convert_aces_if_needed()
        d_total = self.dealer.calculate_total()
        if d_total > 21:
            return "Win (Dealer Bust)"

        if b_total > d_total:
            return "Win"
        elif b_total < d_total:
            return "Lose"
        else:
            return "Tie"

    def show_aggregate_result(self, dealer_total, player_total, player_outcome, bot1_result, bot2_result):
        self.reveal_dealer_hidden_card()
        msg = (
            f"Dealer total: {dealer_total}\n"
            f"Player total: {player_total} -> {player_outcome}\n"
            f"Bot1 -> {bot1_result}\n"
            f"Bot2 -> {bot2_result}\n"
        )
        messagebox.showinfo("Round Results", msg)

    def reveal_dealer_hidden_card(self):
        if self.dealer.spot > 1 and self.dealer_hidden_card_img is not None:
            self.dealer.card_labels[1].config(image=self.dealer_hidden_card_img)

    def update_scoreboard_label(self):
        scoreboard_label.config(
            text=f"Wins: {self.player_wins}  Losses: {self.dealer_wins}  Ties: {self.ties}"
        )

    def show_result_and_disable_buttons(self, title, text, outcome=None):
        if outcome == "player":
            self.player_wins += 1
        elif outcome == "dealer":
            self.dealer_wins += 1
        elif outcome == "tie":
            self.ties += 1

        self.reveal_dealer_hidden_card()
        self.update_scoreboard_label()

        messagebox.showinfo(title, text)
        card_button.config(state="disabled")
        stand_button.config(state="disabled")


if __name__ == '__main__':
    game = Game()
    game.run()
