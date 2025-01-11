import tkinter as tk
import random
from PIL import Image, ImageTk
from tkinter import messagebox


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


def show_result_and_disable_buttons(title, text):
    """
    Shows a messagebox with the result and disables Hit/Stand buttons.
    """
    messagebox.showinfo(title, text)
    card_button.config(state="disabled")
    stand_button.config(state="disabled")


# ------------------ MAIN BLACKJACK LOGIC ------------------ #
def check_blackjack_or_bust(player_type):
    """
    Checks if there is a Blackjack (21) or bust for the specified player_type.
    """
    global blackjack_status

    if player_type == "player":
        # First, try to convert Aces if there is a bust
        updated_score, is_bust = convert_aces_if_needed(player_score)
        player_score[:] = updated_score  # Update the global list in place

        total = calculate_total(player_score)
        if total == 21:
            blackjack_status["player"] = "yes"
        elif is_bust:
            blackjack_status["player"] = "bust"

    elif player_type == "dealer":
        # Same logic for dealer if needed
        updated_score, is_bust = convert_aces_if_needed(dealer_score)
        dealer_score[:] = updated_score

        total = calculate_total(dealer_score)
        if total == 21:
            blackjack_status["dealer"] = "yes"
        # Typically, the dealer logic for bust is handled later,
        # but you can set "bust" here if desired.

    # After updating, check for outcomes
    player_total = calculate_total(player_score)
    dealer_total = calculate_total(dealer_score)

    # 1) Both have 21 -> Push
    if blackjack_status["dealer"] == "yes" and blackjack_status["player"] == "yes":
        show_result_and_disable_buttons("Push!", "It's a tie! Both have 21.")
    # 2) Dealer has 21
    elif blackjack_status["dealer"] == "yes":
        show_result_and_disable_buttons("Dealer Wins!", "Dealer got 21!")
    # 3) Player has 21
    elif blackjack_status["player"] == "yes":
        show_result_and_disable_buttons("Player Wins!", "Player got 21!")
    # 4) Player bust
    elif blackjack_status["player"] == "bust":
        show_result_and_disable_buttons("Player Bust!", f"Player is over 21! Total: {player_total}")


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
    """
    global deck, dealer_spot, player_spot

    if len(deck) == 0:
        root.title("No more cards in the deck!")
        return

    # Pick a random card from the deck
    card_name = random.choice(deck)
    deck.remove(card_name)
    card_val = get_card_value(card_name)
    card_img = resize_card(f"images/cards/{card_name}.png")

    if player_type == "dealer":
        if dealer_spot >= 5:
            return
        dealer_score.append(card_val)
        dealer_cards_labels[dealer_spot].config(image=card_img)
        # Keep a reference to avoid garbage collection
        dealer_cards_labels[dealer_spot].image = card_img
        dealer_spot += 1

        # Check if the dealer has 21
        check_blackjack_or_bust("dealer")

    elif player_type == "player":
        if player_spot >= 5:
            return
        player_score.append(card_val)
        player_cards_labels[player_spot].config(image=card_img)
        player_cards_labels[player_spot].image = card_img
        player_spot += 1

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
        show_result_and_disable_buttons("Player Wins!", f"Dealer busted! Player total: {player_total}")
        return

    if dealer_total > 21:
        show_result_and_disable_buttons("Player Wins!", f"Dealer busted! Player total: {player_total}")
    elif dealer_total > player_total:
        show_result_and_disable_buttons("Dealer Wins!", f"Dealer: {dealer_total}, Player: {player_total}")
    elif dealer_total < player_total:
        show_result_and_disable_buttons("Player Wins!", f"Player: {player_total}, Dealer: {dealer_total}")
    else:
        show_result_and_disable_buttons("Push!", f"Tie! Both have {player_total}.")


def shuffle_deck():
    """
    Creates a new deck, shuffles it, resets scores and labels,
    and deals the initial two cards for both Dealer and Player.
    """
    global deck, dealer_score, player_score
    global dealer_spot, player_spot, blackjack_status

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

    # Deal two cards to each
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
    labelanchor="n"  # put title on the top center
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

# ------------------ GLOBAL VARIABLES ------------------ #
deck = []
dealer_score = []
player_score = []
dealer_spot = 0
player_spot = 0
blackjack_status = {"dealer": "no", "player": "no"}

# Initial deck shuffle/deal
shuffle_deck()

root.mainloop()
