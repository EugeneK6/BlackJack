import tkinter as tk
import random
from PIL import Image, ImageTk
from tkinter import messagebox

# ------------------ GLOBAL SCORE COUNTERS ------------------ #
player_wins = 0
dealer_wins = 0
ties = 0


# ------------------ HELPER FUNCTIONS ------------------ #
def resize_card(card_path, size=(150, 218)):
    """
    Opens the image, resizes it, and returns a PhotoImage object.
    """
    img = Image.open(card_path)
    img = img.resize(size)
    return ImageTk.PhotoImage(img)


def calculate_total(score_list):
    """
    Sums up all card values in the score_list.
    """
    return sum(score_list)


def convert_aces_if_needed(score_list):
    """
    If the total is over 21, tries to convert Aces (value 11) to 1.
    Returns the updated list and a boolean indicating if the total is still over 21.
    """
    while calculate_total(score_list) > 21 and 11 in score_list:
        ace_index = score_list.index(11)
        score_list[ace_index] = 1
    return score_list, (calculate_total(score_list) > 21)


def update_scoreboard_label():
    """
    Updates the scoreboard label with the current global counters.
    """
    scoreboard_label.config(
        text=f"Wins: {player_wins}  Losses: {dealer_wins}  Ties: {ties}"
    )


def reveal_dealer_hidden_card():
    """
    Reveals the dealer's hidden second card if it exists.
    """
    global dealer_hidden_card_img
    # If the dealer has at least 2 cards dealt (i.e. dealer_spot > 1),
    # we show the real image instead of the back.
    if dealer_spot > 1 and dealer_hidden_card_img is not None:
        dealer_cards_labels[1].config(image=dealer_hidden_card_img)


def show_result_and_disable_buttons(title, text, outcome=None):
    """
    Shows a messagebox with the result, increments the global counters
    based on 'outcome', updates scoreboard, and disables Hit/Stand buttons.

    outcome can be "player", "dealer", or "tie".
    """
    global player_wins, dealer_wins, ties

    # Reveal the hidden card (if any) because the round is over
    reveal_dealer_hidden_card()

    if outcome == "player":
        player_wins += 1
    elif outcome == "dealer":
        dealer_wins += 1
    elif outcome == "tie":
        ties += 1

    # Update scoreboard on every result
    update_scoreboard_label()

    # Show the result popup
    messagebox.showinfo(title, text)
    card_button.config(state="disabled")
    stand_button.config(state="disabled")


# ------------------ MAIN BLACKJACK LOGIC ------------------ #
def update_player_score_label():
    """Updates the player's score label with the current total."""
    total = calculate_total(player_score)
    player_score_label.config(text=f"Player Score: {total}")


def check_blackjack_or_bust(player_type):
    """
    Checks if there is a Blackjack (21) or bust for the specified player_type.
    """
    global blackjack_status

    if player_type == "player":
        updated_score, is_bust = convert_aces_if_needed(player_score)
        player_score[:] = updated_score
        update_player_score_label()

        total = calculate_total(player_score)
        if total == 21:
            blackjack_status["player"] = "yes"
        elif is_bust:
            blackjack_status["player"] = "bust"

    elif player_type == "dealer":
        updated_score, is_bust = convert_aces_if_needed(dealer_score)
        dealer_score[:] = updated_score

        total = calculate_total(dealer_score)
        if total == 21:
            blackjack_status["dealer"] = "yes"
        # Typically, bust is handled after the player stands.

    # After updating, check for immediate outcomes
    player_total = calculate_total(player_score)
    dealer_total = calculate_total(dealer_score)

    # 1) Both have 21 -> tie
    if blackjack_status["dealer"] == "yes" and blackjack_status["player"] == "yes":
        show_result_and_disable_buttons(
            "Push!",
            "It's a tie! Both have 21.",
            outcome="tie"
        )
    # 2) Dealer has 21
    elif blackjack_status["dealer"] == "yes":
        show_result_and_disable_buttons(
            "Dealer Wins!",
            "Dealer got 21!",
            outcome="dealer"
        )
    # 3) Player has 21
    elif blackjack_status["player"] == "yes":
        show_result_and_disable_buttons(
            "Player Wins!",
            "Player got 21!",
            outcome="player"
        )
    # 4) Player bust
    elif blackjack_status["player"] == "bust":
        show_result_and_disable_buttons(
            "Player Bust!",
            f"Player is over 21! Total: {player_total}",
            outcome="dealer"
        )


def get_card_value(card_name):
    """
    Extracts the card value from its file name.
    Example: '14_of_spades.png' -> 14 means Ace, 11/12/13 -> face cards (10), etc.
    """
    value = int(card_name.split("_", 1)[0])
    if value == 14:
        return 11  # Ace
    elif value in [11, 12, 13]:
        return 10  # Jack, Queen, King
    else:
        return value


def deal_card_to(player_type):
    """
    Deals a card to the specified player (player_type = 'player' or 'dealer').
    The second dealer card is visually hidden until the round ends.
    """
    global deck, dealer_spot, player_spot
    global dealer_hidden_card_img  # we'll store the real card image for the hidden card

    if len(deck) == 0:
        root.title("No more cards in the deck!")
        return

    # Pick a random card from the deck
    card_name = random.choice(deck)
    deck.remove(card_name)
    card_val = get_card_value(card_name)
    real_card_img = resize_card(f"images/cards/{card_name}.png")

    if player_type == "dealer":
        if dealer_spot >= 5:
            return
        dealer_score.append(card_val)

        # If it's the second card of the dealer (dealer_spot == 1), show the back image
        # but store the actual image for later reveal.
        if dealer_spot == 1:
            dealer_hidden_card_img = real_card_img
            dealer_cards_labels[dealer_spot].config(image=back_img)  # show back
            dealer_cards_labels[dealer_spot].image = back_img  # store reference
        else:
            # For other dealer cards (first, third, etc.), show them normally
            dealer_cards_labels[dealer_spot].config(image=real_card_img)
            dealer_cards_labels[dealer_spot].image = real_card_img

        dealer_spot += 1

        # Check if the dealer has 21 (though normally you don't reveal it yet)
        check_blackjack_or_bust("dealer")

    elif player_type == "player":
        if player_spot >= 5:
            return
        player_score.append(card_val)
        player_cards_labels[player_spot].config(image=real_card_img)
        player_cards_labels[player_spot].image = real_card_img
        player_spot += 1

        # Update player's score label each time they get a card
        update_player_score_label()

        # Check if the player has 21 or bust
        check_blackjack_or_bust("player")

    root.title(f"Cards left: {len(deck)}")


def dealer_hit():
    """
    Command for the dealer to draw another card.
    """
    deal_card_to("dealer")


def player_hit():
    """
    Command for the player to draw another card.
    """
    deal_card_to("player")


def stand():
    """
    When the player stands:
    - Disable 'Hit' and 'Stand'
    - Dealer draws until reaching at least 17 or runs out of spots.
    - Compare totals and show the result.
    """
    global player_score, dealer_score
    card_button.config(state="disabled")
    stand_button.config(state="disabled")

    # Dealer draws while total < 17 and less than 5 cards
    while calculate_total(dealer_score) < 17 and dealer_spot < 5:
        dealer_hit()

    # Re-check totals
    player_total = calculate_total(player_score)
    dealer_score[:], dealer_bust = convert_aces_if_needed(dealer_score)
    dealer_total = calculate_total(dealer_score)

    if dealer_bust:
        show_result_and_disable_buttons(
            "Player Wins!",
            f"Dealer busted! Player total: {player_total}",
            outcome="player"
        )
        return

    if dealer_total > 21:
        show_result_and_disable_buttons(
            "Player Wins!",
            f"Dealer busted! Player total: {player_total}",
            outcome="player"
        )
    elif dealer_total > player_total:
        show_result_and_disable_buttons(
            "Dealer Wins!",
            f"Dealer: {dealer_total}, Player: {player_total}",
            outcome="dealer"
        )
    elif dealer_total < player_total:
        show_result_and_disable_buttons(
            "Player Wins!",
            f"Player: {player_total}, Dealer: {dealer_total}",
            outcome="player"
        )
    else:
        show_result_and_disable_buttons(
            "Push!",
            f"Tie! Both have {player_total}.",
            outcome="tie"
        )


def shuffle_deck():
    """
    Creates a new deck, shuffles it, resets scores and labels,
    and deals the initial two cards for both Dealer and Player.
    """
    global deck, dealer_score, player_score
    global dealer_spot, player_spot, blackjack_status
    global dealer_hidden_card_img

    card_button.config(state="normal")
    stand_button.config(state="normal")

    # Create and shuffle the deck
    suits = ["diamonds", "clubs", "hearts", "spades"]
    values = range(2, 15)  # 11->Jack, 12->Queen, 13->King, 14->Ace
    deck = [f"{v}_of_{s}" for s in suits for v in values]
    random.shuffle(deck)

    # Reset global variables
    dealer_score = []
    player_score = []
    dealer_spot = 0
    player_spot = 0
    blackjack_status = {"dealer": "no", "player": "no"}

    # Clear labels on the screen
    for lbl in dealer_cards_labels:
        lbl.config(image="", text="")
    for lbl in player_cards_labels:
        lbl.config(image="", text="")

    # Reset the player's score label
    player_score_label.config(text="Player Score: 0")

    # Reset hidden card
    dealer_hidden_card_img = None

    # Deal two cards to each
    # (the second dealer card will be displayed as back_img)
    deal_card_to("dealer")
    deal_card_to("dealer")
    deal_card_to("player")
    deal_card_to("player")

    root.title(f"Cards left: {len(deck)}")


# ------------------ TKINTER SETUP ------------------ #
root = tk.Tk()
root.title("Casino Blackjack")
# Use a darker green for a classic casino look
root.configure(bg="#0B3B0B")
root.geometry("1200x800")

# Prepare the back image for the dealer's hidden card
back_img = resize_card("images/cards/back.png")

# Main frame
main_frame = tk.Frame(root, bg="#0B3B0B")
main_frame.pack(pady=20)

# Dealer frame
dealer_frame = tk.LabelFrame(
    main_frame,
    text="Dealer",
    bg="#0B3B0B",
    fg="white",
    bd=2,
    font=("Verdana", 16, "bold"),
    labelanchor="n"
)
dealer_frame.pack(padx=20, ipadx=20)

# Player frame
player_frame = tk.LabelFrame(
    main_frame,
    text="Player",
    bg="#0B3B0B",
    fg="white",
    bd=2,
    font=("Verdana", 16, "bold"),
    labelanchor="n"
)
player_frame.pack(ipadx=20, pady=10)

# Arrays to store references to card Label widgets
dealer_cards_labels = []
player_cards_labels = []

# Create 5 labels for the dealer
for i in range(5):
    lbl = tk.Label(dealer_frame, text="", bg="#0B3B0B")
    lbl.grid(row=0, column=i, padx=10, pady=10)
    dealer_cards_labels.append(lbl)

# Create 5 labels for the player
for i in range(5):
    lbl = tk.Label(player_frame, text="", bg="#0B3B0B")
    lbl.grid(row=1, column=i, padx=10, pady=10)
    player_cards_labels.append(lbl)

# -- Player score label --
player_score_label = tk.Label(
    player_frame,
    text="Player Score: 0",
    bg="#0B3B0B",
    fg="white",
    font=("Verdana", 12, "bold")
)
player_score_label.grid(row=2, column=0, padx=10, pady=10, columnspan=5)

# Frame for buttons
button_frame = tk.Frame(root, bg="#0B3B0B")
button_frame.pack(pady=20)

# Shuffle deck button
shuffle_button = tk.Button(
    button_frame,
    text="Shuffle Deck",
    font=("Helvetica", 14),
    bg="white",
    fg="black",
    command=shuffle_deck
)
shuffle_button.grid(row=0, column=0)

# Player hit button
card_button = tk.Button(
    button_frame,
    text="Hit Me!",
    font=("Helvetica", 14),
    bg="white",
    fg="black",
    command=player_hit
)
card_button.grid(row=0, column=1, padx=10)

# Stand button
stand_button = tk.Button(
    button_frame,
    text="Stand!",
    font=("Helvetica", 14),
    bg="white",
    fg="black",
    command=stand
)
stand_button.grid(row=0, column=2)

# -- Scoreboard in the top-right corner --
scoreboard_label = tk.Label(
    root,
    text="Wins: 0  Losses: 0  Ties: 0",
    bg="#0B3B0B",
    fg="white",
    font=("Verdana", 12, "bold")
)
scoreboard_label.place(relx=0.98, rely=0.03, anchor="ne")

# Immediately update scoreboard (to ensure consistency on startup)
update_scoreboard_label()

# ------------------ GLOBAL VARIABLES ------------------ #
deck = []
dealer_score = []
player_score = []
dealer_spot = 0
player_spot = 0
blackjack_status = {"dealer": "no", "player": "no"}

# We'll store the real second card's image here for later reveal
dealer_hidden_card_img = None

# Initial deck shuffle/deal
shuffle_deck()

root.mainloop()
