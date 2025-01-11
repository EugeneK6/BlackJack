import tkinter as tk
import random
import json
from PIL import Image, ImageTk
from tkinter import messagebox


class Player:
    """
    Represents a player in the Blackjack game (could be a human player or the dealer).
    """

    def __init__(self, name: str):
        self.name = name
        self.cards = []  # Stores card names (e.g., "14_of_spades")
        self.score = []  # Stores numeric values of each card (e.g., [11, 10, 5])

    def reset(self):
        """
        Clears the player's cards and score for a new round.
        """
        self.cards.clear()
        self.score.clear()

    def add_card(self, card_value: int):
        """
        Adds a card value to the player's score list.
        """
        self.score.append(card_value)

    def get_total(self) -> int:
        """
        Returns the total value of the player's current hand.
        """
        return sum(self.score)


class BlackjackGame:
    """
    OOP-based Blackjack game with a Tkinter interface.
    Features:
    - One hidden card for the dealer
    - Scoreboard for wins, losses, and ties
    - Player score tracking
    """

    def __init__(self):
        """
        Creates a new game session.
        Initializes players, scoreboard counters, and the UI.
        """
        # -- Global counters for wins, losses, and ties --
        self.player_wins = 0
        self.dealer_wins = 0
        self.ties = 0

        # -- Create the player and the dealer --
        self.player = Player(name="Player")
        self.dealer = Player(name="Dealer")

        # -- Blackjack status dictionary to track 'player' / 'dealer': 'no' or 'yes' or 'bust' --
        self.blackjack_status = {"dealer": "no", "player": "no"}

        # -- Deck-related variables --
        self.deck = []
        self.dealer_spot = 0
        self.player_spot = 0

        # -- Will store the real image of the dealer's hidden card (second card) here --
        self.dealer_hidden_card_img = None

        # -- Initialize the Tkinter window --
        self.root = tk.Tk()
        self.root.title("Casino Blackjack")
        self.root.configure(bg="#0B3B0B")
        self.root.geometry("1200x800")

        # Prepare the card back image for the dealer's hidden card
        self.back_img = self.resize_card("images/cards/back.png")

        # -- Build the UI --
        self.setup_ui()

        # Shuffle and deal cards on startup
        self.shuffle_deck()

    # -------------------------------------------------------------------------
    #  Methods that mirror the structure of a generic "Game" class
    # -------------------------------------------------------------------------
    def add_player(self, player: Player):
        """
        Adds a Player object to the current game session (not necessarily needed
        for a single-player vs. dealer game, but could be extended for multiplayer).
        """
        pass  # For a basic single-player Blackjack, we don't really need this.

    def save_game(self, filename: str):
        """
        Saves the current game state to a file in JSON format.
        For demo purposes, we save the scoreboard and the remaining deck.
        """
        data = {
            "player_wins": self.player_wins,
            "dealer_wins": self.dealer_wins,
            "ties": self.ties,
            "deck": self.deck,
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_game(cls, filename: str) -> 'BlackjackGame':
        """
        Loads the game state from a JSON file and returns a new BlackjackGame instance.
        """
        with open(filename, 'r') as f:
            data = json.load(f)

        new_game = cls()
        new_game.player_wins = data["player_wins"]
        new_game.dealer_wins = data["dealer_wins"]
        new_game.ties = data["ties"]
        new_game.deck = data["deck"]

        # Optionally, update the scoreboard label if the UI is already initialized
        new_game.update_scoreboard_label()
        return new_game

    def finish_game(self):
        """
        Called when the game session ends. Closes the Tkinter window or performs other cleanup.
        """
        self.root.destroy()

    def win_condition(self):
        """
        Could be used to determine if a player has reached a winning condition.
        In this example, we handle it in check_blackjack_or_bust().
        """
        pass

    def lose_condition(self):
        """
        Could be used to determine if a player has lost the game.
        In this example, we handle it in check_blackjack_or_bust() and stand().
        """
        pass

    def step(self):
        """
        For a turn-based game, you could define one turn (step) here.
        In this Blackjack example, everything is event-driven by button clicks.
        """
        pass

    def get_current_state(self):
        """
        Returns the current state of the game session for debugging or saving/loading.
        """
        state = {
            "player_wins": self.player_wins,
            "dealer_wins": self.dealer_wins,
            "ties": self.ties,
            "deck_size": len(self.deck),
            "player_score": sum(self.player.score),
            "dealer_score": sum(self.dealer.score),
        }
        return state

    def run(self):
        """
        Starts the Tkinter main loop. The game will run until the window is closed.
        """
        self.root.mainloop()

    # -------------------------------------------------------------------------
    #  HELPER / LOGIC METHODS
    # -------------------------------------------------------------------------
    def setup_ui(self):
        """
        Initializes all Tkinter UI elements: frames, labels, buttons, etc.
        """
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="#0B3B0B")
        self.main_frame.pack(pady=20)

        # Dealer frame
        self.dealer_frame = tk.LabelFrame(
            self.main_frame,
            text="Dealer",
            bg="#0B3B0B",
            fg="white",
            bd=2,
            font=("Verdana", 16, "bold"),
            labelanchor="n"
        )
        self.dealer_frame.pack(padx=20, ipadx=20)

        # Player frame
        self.player_frame = tk.LabelFrame(
            self.main_frame,
            text="Player",
            bg="#0B3B0B",
            fg="white",
            bd=2,
            font=("Verdana", 16, "bold"),
            labelanchor="n"
        )
        self.player_frame.pack(ipadx=20, pady=10)

        # Arrays to store references to dealer and player card Label widgets
        self.dealer_cards_labels = []
        self.player_cards_labels = []

        # Create 5 labels for the dealer
        for i in range(5):
            lbl = tk.Label(self.dealer_frame, text="", bg="#0B3B0B")
            lbl.grid(row=0, column=i, padx=10, pady=10)
            self.dealer_cards_labels.append(lbl)

        # Create 5 labels for the player
        for i in range(5):
            lbl = tk.Label(self.player_frame, text="", bg="#0B3B0B")
            lbl.grid(row=1, column=i, padx=10, pady=10)
            self.player_cards_labels.append(lbl)

        # Player score label
        self.player_score_label = tk.Label(
            self.player_frame,
            text="Player Score: 0",
            bg="#0B3B0B",
            fg="white",
            font=("Verdana", 12, "bold")
        )
        self.player_score_label.grid(row=2, column=0, padx=10, pady=10, columnspan=5)

        # Frame for buttons
        self.button_frame = tk.Frame(self.root, bg="#0B3B0B")
        self.button_frame.pack(pady=20)

        # Shuffle deck button
        self.shuffle_button = tk.Button(
            self.button_frame,
            text="Shuffle Deck",
            font=("Helvetica", 14),
            bg="white",
            fg="black",
            command=self.shuffle_deck
        )
        self.shuffle_button.grid(row=0, column=0)

        # Player hit button
        self.card_button = tk.Button(
            self.button_frame,
            text="Hit Me!",
            font=("Helvetica", 14),
            bg="white",
            fg="black",
            command=self.player_hit
        )
        self.card_button.grid(row=0, column=1, padx=10)

        # Stand button
        self.stand_button = tk.Button(
            self.button_frame,
            text="Stand!",
            font=("Helvetica", 14),
            bg="white",
            fg="black",
            command=self.stand
        )
        self.stand_button.grid(row=0, column=2)

        # Scoreboard in the top-right corner
        self.scoreboard_label = tk.Label(
            self.root,
            text="Wins: 0  Losses: 0  Ties: 0",
            bg="#0B3B0B",
            fg="white",
            font=("Verdana", 12, "bold")
        )
        self.scoreboard_label.place(relx=0.98, rely=0.03, anchor="ne")

        self.update_scoreboard_label()

    def resize_card(self, card_path, size=(150, 218)):
        """
        Opens the image, resizes it, and returns a PhotoImage object.
        """
        from PIL import Image
        img = Image.open(card_path)
        img = img.resize(size)
        return ImageTk.PhotoImage(img)

    def update_scoreboard_label(self):
        """
        Updates the scoreboard label using the current global counters.
        """
        self.scoreboard_label.config(
            text=f"Wins: {self.player_wins}  Losses: {self.dealer_wins}  Ties: {self.ties}"
        )

    def reveal_dealer_hidden_card(self):
        """
        Reveals the dealer's second card if it was hidden.
        """
        if self.dealer_spot > 1 and self.dealer_hidden_card_img is not None:
            self.dealer_cards_labels[1].config(image=self.dealer_hidden_card_img)

    def show_result_and_disable_buttons(self, title, text, outcome=None):
        """
        Displays a messagebox with the result, increments the respective global counter,
        updates the scoreboard, and disables Hit/Stand buttons.

        outcome can be "player", "dealer", or "tie".
        """
        # Reveal the second dealer card
        self.reveal_dealer_hidden_card()

        if outcome == "player":
            self.player_wins += 1
        elif outcome == "dealer":
            self.dealer_wins += 1
        elif outcome == "tie":
            self.ties += 1

        self.update_scoreboard_label()

        messagebox.showinfo(title, text)
        self.card_button.config(state="disabled")
        self.stand_button.config(state="disabled")

    def update_player_score_label(self):
        """
        Updates the player's score label to show the current total.
        """
        total = sum(self.player.score)
        self.player_score_label.config(text=f"Player Score: {total}")

    def check_blackjack_or_bust(self, who: str):
        """
        Checks if 'player' or 'dealer' has Blackjack (21) or a bust (>21).
        Uses self.blackjack_status to track outcomes and can end the round early.
        """
        if who == "player":
            self.convert_aces_if_needed(self.player.score)
            self.update_player_score_label()
            total = sum(self.player.score)

            if total == 21:
                self.blackjack_status["player"] = "yes"
            elif total > 21:
                self.blackjack_status["player"] = "bust"

        elif who == "dealer":
            self.convert_aces_if_needed(self.dealer.score)
            total = sum(self.dealer.score)

            if total == 21:
                self.blackjack_status["dealer"] = "yes"
            # Bust is typically checked after the player stands.

        player_total = sum(self.player.score)
        dealer_total = sum(self.dealer.score)

        # Both have 21 -> tie
        if self.blackjack_status["dealer"] == "yes" and self.blackjack_status["player"] == "yes":
            self.show_result_and_disable_buttons(
                "Push!",
                "It's a tie! Both have 21.",
                outcome="tie"
            )
        # Dealer has 21
        elif self.blackjack_status["dealer"] == "yes":
            self.show_result_and_disable_buttons(
                "Dealer Wins!",
                "Dealer got 21!",
                outcome="dealer"
            )
        # Player has 21
        elif self.blackjack_status["player"] == "yes":
            self.show_result_and_disable_buttons(
                "Player Wins!",
                "Player got 21!",
                outcome="player"
            )
        # Player bust
        elif self.blackjack_status["player"] == "bust":
            self.show_result_and_disable_buttons(
                "Player Bust!",
                f"Player is over 21! Total: {player_total}",
                outcome="dealer"
            )

    def convert_aces_if_needed(self, score_list):
        """
        If the total is over 21, tries to convert Aces (value 11) to 1.
        """
        while sum(score_list) > 21 and 11 in score_list:
            ace_index = score_list.index(11)
            score_list[ace_index] = 1

    def get_card_value(self, card_name: str) -> int:
        """
        Returns the numeric value of a card, based on its filename
        (e.g., "11_of_hearts" -> 10 if face card, "14_of_spades" -> 11 if Ace, etc.).
        """
        value = int(card_name.split("_", 1)[0])
        if value == 14:
            return 11  # Ace
        elif value in [11, 12, 13]:
            return 10  # Jack, Queen, King
        else:
            return value

    def deal_card_to(self, who: str):
        """
        Deals a card to 'player' or 'dealer'.
        Shows the back of the card for the dealer's second card until the round ends.
        """
        if len(self.deck) == 0:
            self.root.title("No more cards in the deck!")
            return

        card_name = random.choice(self.deck)
        self.deck.remove(card_name)
        card_val = self.get_card_value(card_name)
        real_card_img = self.resize_card(f"images/cards/{card_name}.png")

        if who == "dealer":
            if self.dealer_spot >= 5:
                return

            self.dealer.cards.append(card_name)
            self.dealer.score.append(card_val)

            # If it's the second dealer card, display the back image
            if self.dealer_spot == 1:
                self.dealer_hidden_card_img = real_card_img
                self.dealer_cards_labels[self.dealer_spot].config(image=self.back_img)
                self.dealer_cards_labels[self.dealer_spot].image = self.back_img
            else:
                self.dealer_cards_labels[self.dealer_spot].config(image=real_card_img)
                self.dealer_cards_labels[self.dealer_spot].image = real_card_img

            self.dealer_spot += 1
            # Check if the dealer has 21
            self.check_blackjack_or_bust("dealer")

        elif who == "player":
            if self.player_spot >= 5:
                return

            self.player.cards.append(card_name)
            self.player.score.append(card_val)
            self.player_cards_labels[self.player_spot].config(image=real_card_img)
            self.player_cards_labels[self.player_spot].image = real_card_img

            self.player_spot += 1

            # Update player's score and check for blackjack or bust
            self.update_player_score_label()
            self.check_blackjack_or_bust("player")

        self.root.title(f"Cards left: {len(self.deck)}")

    def dealer_hit(self):
        """
        Dealer draws another card.
        """
        self.deal_card_to("dealer")

    def player_hit(self):
        """
        Player draws another card.
        """
        self.deal_card_to("player")

    def stand(self):
        """
        When the player stands:
        - Disable 'Hit' and 'Stand'
        - Dealer draws until reaching at least 17 or until out of spots
        - Compare totals and show the result
        """
        self.card_button.config(state="disabled")
        self.stand_button.config(state="disabled")

        # Dealer draws while total < 17 and spots < 5
        while sum(self.dealer.score) < 17 and self.dealer_spot < 5:
            self.dealer_hit()

        # Re-check totals
        player_total = sum(self.player.score)
        self.convert_aces_if_needed(self.dealer.score)
        dealer_total = sum(self.dealer.score)

        if dealer_total > 21:
            self.show_result_and_disable_buttons(
                "Player Wins!",
                f"Dealer busted! Player total: {player_total}",
                outcome="player"
            )
        elif dealer_total > player_total:
            self.show_result_and_disable_buttons(
                "Dealer Wins!",
                f"Dealer: {dealer_total}, Player: {player_total}",
                outcome="dealer"
            )
        elif dealer_total < player_total:
            self.show_result_and_disable_buttons(
                "Player Wins!",
                f"Player: {player_total}, Dealer: {dealer_total}",
                outcome="player"
            )
        else:
            self.show_result_and_disable_buttons(
                "Push!",
                f"Tie! Both have {player_total}.",
                outcome="tie"
            )

    def shuffle_deck(self):
        """
        Creates a new deck, shuffles it, resets everything, and deals two cards to each player.
        """
        self.card_button.config(state="normal")
        self.stand_button.config(state="normal")

        suits = ["diamonds", "clubs", "hearts", "spades"]
        values = range(2, 15)  # 11->Jack, 12->Queen, 13->King, 14->Ace
        self.deck = [f"{v}_of_{s}" for s in suits for v in values]
        random.shuffle(self.deck)

        # Reset player and dealer states
        self.player.reset()
        self.dealer.reset()
        self.blackjack_status = {"dealer": "no", "player": "no"}

        # Reset spots
        self.dealer_spot = 0
        self.player_spot = 0

        # Clear card labels
        for lbl in self.dealer_cards_labels:
            lbl.config(image="", text="")
        for lbl in self.player_cards_labels:
            lbl.config(image="", text="")

        # Reset the player's score label
        self.player_score_label.config(text="Player Score: 0")

        # Reset the dealer's hidden card
        self.dealer_hidden_card_img = None

        # Deal two cards to each
        self.deal_card_to("dealer")
        self.deal_card_to("dealer")
        self.deal_card_to("player")
        self.deal_card_to("player")

        self.root.title(f"Cards left: {len(self.deck)}")


if __name__ == '__main__':
    """
    Example usage/testing of the OOP-based BlackjackGame.
    """
    # 1) Create a game object
    game = BlackjackGame()
    # 2) Run the game (Tkinter mainloop)
    game.run()

