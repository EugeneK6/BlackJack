import tkinter as tk
import random
import json
from tkinter import messagebox
from PIL import Image, ImageTk
from typing import Optional


class Player:
    """
    Represents a single participant in the game (including bots and dealer).
    Stores name, card values, and references to Label widgets for the UI.
    """
    def __init__(self, name: str, is_bot=False, is_dealer=False):
        self.name = name
        self.is_bot = is_bot
        self.is_dealer = is_dealer

        # List of integer card values, e.g. [10, 11, 4]
        self.cards_values = []
        # Index (0..4) of the next card slot
        self.spot = 0

        # Tkinter Label widgets that display the card images
        self.card_labels = []

        # Real card images (for later "reveal"), especially for bots
        self.real_card_images = [None]*5

    def reset(self):
        """Resets the player's state (called at the start of a new round)."""
        self.cards_values.clear()
        self.spot = 0
        self.real_card_images = [None]*5

    def add_card_value(self, value: int) -> bool:
        """
        Adds 'value' (the card's point value) to the player's card list.
        Returns True if the card was successfully added, or False if there's no space.
        """
        if self.spot >= 5:
            return False
        self.cards_values.append(value)
        self.spot += 1
        return True

    def calculate_total(self) -> int:
        """Returns the sum of the card values (without converting Aces to 1)."""
        return sum(self.cards_values)

    def convert_aces_if_needed(self):
        """
        If the player is bust (> 21) and has Aces counted as 11,
        convert them to 1 until there's no bust or no more Aces.
        """
        while self.calculate_total() > 21 and 11 in self.cards_values:
            idx = self.cards_values.index(11)
            self.cards_values[idx] = 1

    def is_bust(self) -> bool:
        """Returns True if the player's total exceeds 21 (bust)."""
        return self.calculate_total() > 21

    def bot_decision(self, dealer_upcard: Optional[int]) -> bool:
        """
        Bot AI logic:
          1) If total < 12, always hit.
          2) If total >= 19, stand.
          3) For totals in [12..18], hit with a certain probability:
             if dealer_upcard <= 6 => 30% chance; else => 60%.
        Returns True if the bot wants to hit, False if it stands.
        """
        self.convert_aces_if_needed()
        total = self.calculate_total()

        if len(self.cards_values) >= 5 or self.is_bust():
            return False

        # If the dealer upcard is unknown, assume 7
        if dealer_upcard is None:
            dealer_upcard = 7

        if total < 12:
            return True
        elif total >= 19:
            return False
        else:
            # total in [12..18]
            if dealer_upcard <= 6:
                chance_to_hit = 0.3
            else:
                chance_to_hit = 0.6
            return (random.random() < chance_to_hit)


class Game:
    """
    Manages the Blackjack game logic and Tkinter UI in an OOP style.
    """

    def __init__(self):
        # Global scores
        self.player_wins = 0
        self.dealer_wins = 0
        self.ties = 0

        # Tkinter window
        self.root = tk.Tk()
        self.root.title("Casino Blackjack (OOP Version)")
        self.root.configure(bg="#0B3B0B")
        self.root.geometry("1120x630")

        # Deck and hidden images
        self.deck = []
        self.dealer_hidden_card_img = None

        # Create participants
        self.dealer = Player("Dealer", is_dealer=True)
        self.player = Player("Player")
        self.bot1 = Player("Bot1", is_bot=True)
        self.bot2 = Player("Bot2", is_bot=True)

        self.players = [self.dealer, self.bot1, self.player, self.bot2]

        # Track blackjack/bust status for dealer/player only
        self.blackjack_status = {"dealer": "no", "player": "no"}

        # Image for the back of a card
        self.back_img = self.resize_card("images/cards/back.png", (126,182))

        # Build the UI
        self.setup_ui()

        # Deal initial cards
        self.shuffle_deck()

    # ------------------------------------------------------------------
    # Template-like methods (save_game, load_game, etc.)
    # ------------------------------------------------------------------
    def add_player(self, player: Player):
        self.players.append(player)

    def save_game(self, filename: str):
        """
        Minimal JSON save example. It serializes global scores and each player's cards.
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
        """Close the app if needed."""
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

    # ---------------------- UI and game logic ----------------------
    def setup_ui(self):
        """
        Sets up all the Tk widgets: frames for dealer, bots, player, buttons, scoreboard, etc.
        """
        # Dealer frame
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

        # Middle area: Bot1, Player, Bot2
        middle_frame = tk.Frame(self.root, bg="#0B3B0B")
        middle_frame.pack()

        # Bot1
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

        # Player
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

        # Bot2
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

        # Buttons
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

        # Scoreboard
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

    def resize_card(self, card_path, size=(126,182)):
        img = Image.open(card_path)
        img = img.resize(size)
        return ImageTk.PhotoImage(img)

    def update_player_score_label(self):
        """Updates the player's score label with the current total."""
        player_score_label.config(text=f"Player Score: {self.player.calculate_total()}")

    def shuffle_deck(self):
        """
        Creates and shuffles a new deck, resets all players, and deals initial cards.
        """
        suits = ["diamonds", "clubs", "hearts", "spades"]
        values = range(2, 15)
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
        """Deals one card to the given 'person' (dealer/bot/player)."""
        if len(self.deck) == 0:
            self.root.title("No more cards in the deck!")
            return

        card_name = random.choice(self.deck)
        self.deck.remove(card_name)
        card_val = self.get_card_value(card_name)

        if not person.add_card_value(card_val):
            return

        real_card_img = self.resize_card(f"images/cards/{card_name}.png", (126,182))

        # Store the real image in case we want to reveal it later
        idx = person.spot - 1
        person.real_card_images[idx] = real_card_img

        # --- Dealer logic ---
        if person.is_dealer and person.spot == 2:
            # Hide dealer's second card
            self.dealer_hidden_card_img = real_card_img
            lbl = person.card_labels[1]
            lbl.config(image=self.back_img)
            lbl.image = self.back_img

        # --- Bots: all cards are hidden until the end ---
        elif person.is_bot:
            lbl = person.card_labels[idx]
            lbl.config(image=self.back_img)
            lbl.image = self.back_img

        else:
            # Player (or dealer's other cards)
            lbl = person.card_labels[idx]
            lbl.config(image=real_card_img)
            lbl.image = real_card_img

        # If it's the player, check for 21/bust and update the score label
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
        """
        Checks whether 'player' or 'dealer' reached 21 or bust,
        then calls check_immediate_outcomes() if needed.
        """
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
        """Button 'Hit Me!' => give a card to the player."""
        self.deal_card_to(self.player)

    def stand(self):
        """
        When the player clicks 'Stand':
          - Disable 'Hit' and 'Stand'
          - Bots take their turns
          - Dealer takes cards until total >= 17
          - Compare results and show the outcome
        """
        card_button.config(state="disabled")
        stand_button.config(state="disabled")

        if self.blackjack_status["player"] in ["bust", "yes"]:
            return
        if self.blackjack_status["dealer"] == "yes":
            return

        self.play_for_bot(self.bot1)
        self.play_for_bot(self.bot2)

        while True:
            self.dealer.convert_aces_if_needed()
            if self.dealer.calculate_total() < 17 and self.dealer.spot < 5:
                self.deal_card_to(self.dealer)
            else:
                break

        self.final_comparison()

    def play_for_bot(self, bot: Player):
        """Bot's logic: repeat while the bot decides to hit."""
        while True:
            bot.convert_aces_if_needed()
            if bot.is_bust() or len(bot.cards_values) >= 5:
                break
            dealer_upcard = None
            if len(self.dealer.cards_values) > 0:
                dealer_upcard = self.dealer.cards_values[0]

            if bot.bot_decision(dealer_upcard):
                self.deal_card_to(bot)
            else:
                break

    def final_comparison(self):
        """
        Compare player's and dealer's totals, also compare each bot to the dealer.
        Then reveal all hidden cards from bots (and dealer's second card).
        """
        # Reveal bots' cards
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
        """
        Flip all the bot's cards, replacing the back image with the real ones.
        Called during final comparison so the user can see the bots' actual cards.
        """
        if not bot.is_bot:
            return

        for i in range(bot.spot):
            lbl = bot.card_labels[i]
            real_img = bot.real_card_images[i]
            if real_img is not None:
                lbl.config(image=real_img)
                lbl.image = real_img

    def compare_with_dealer(self, bot: Player) -> str:
        """
        Returns the result for a bot: 'Bust', 'Win', 'Lose', or 'Tie'.
        """
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
        """
        Shows a messagebox with final results for dealer, player, and both bots.
        """
        self.reveal_dealer_hidden_card()
        msg = (
            f"Dealer total: {dealer_total}\n"
            f"Player total: {player_total} -> {player_outcome}\n"
            f"Bot1 -> {bot1_result}\n"
            f"Bot2 -> {bot2_result}\n"
        )
        messagebox.showinfo("Round Results", msg)

    def reveal_dealer_hidden_card(self):
        """
        Shows the dealer's second card if it was previously hidden.
        """
        if self.dealer.spot > 1 and self.dealer_hidden_card_img is not None:
            self.dealer.card_labels[1].config(image=self.dealer_hidden_card_img)

    def update_scoreboard_label(self):
        scoreboard_label.config(
            text=f"Wins: {self.player_wins}  Losses: {self.dealer_wins}  Ties: {self.ties}"
        )

    def show_result_and_disable_buttons(self, title, text, outcome=None):
        """
        Ends the round: displays a message, updates global stats if needed,
        and disables Hit/Stand buttons.
        """
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
