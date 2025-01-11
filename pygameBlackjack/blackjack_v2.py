import pygame
import random
import copy
from tkinter import *

pygame.init()

root = Tk()
root.geometry("1200x800")
root.configure(background="green")

# ---------------------- CARD & DECK SETTINGS ----------------------
# We have 4 suits and 13 ranks
suits = ['hearts', 'diamonds', 'clubs', 'spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']

# Build a single deck of 52 unique cards: ['2_of_hearts', '3_of_hearts', ... , 'A_of_spades']
base_deck = []
for s in suits:
    for r in ranks:
        base_deck.append(f'{r}_of_{s}')

# Number of decks
decks = 4
# Create our full deck by multiplying
# e.g. if decks=4 => 208 cards in total
# We'll deep-copy it into game_deck when starting a new hand.
# base_deck itself remains as reference
# (You can also shuffle it if you want initially, but below we pick random cards anyway.)
# ---------------------------------------------------------------

# ---------------------- PYGAME WINDOW SETTINGS ----------------------
WIDTH, HEIGHT = 600, 900
# Use RESIZABLE so the user can change the window size
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Pygame Blackjack (Resizable Window)')

fps = 60
clock = pygame.time.Clock()

# ---------------------- FONTS ----------------------
font = pygame.font.Font('freesansbold.ttf', 44)
smaller_font = pygame.font.Font('freesansbold.ttf', 36)

# ---------------------- GAME STATE VARIABLES ----------------------
active = False           # Indicates whether the round is active
records = [0, 0, 0]      # [wins, losses, draws]
player_score = 0
dealer_score = 0
initial_deal = False     # First deal: 2 cards to player, 2 to dealer
my_hand = []
dealer_hand = []
outcome = 0              # 0 => no outcome yet, 1..4 => see results
reveal_dealer = False    # If True, dealer's first card is shown
hand_active = False      # If True, player can still "HIT"
add_score = False        # If True, we record the outcome to records

results = [
    '',                       # index 0 => no result
    'PLAYER BUSTED o_O',      # index 1 => bust
    'Player WINS! :)',        # index 2
    'DEALER WINS :(',         # index 3
    'TIE GAME...'             # index 4 => push
]

# ---------------------- LOAD CARD IMAGES ----------------------
# We assume you have files like '2_of_hearts.png', '2_of_diamonds.png', etc. in images/cards/
# We'll store them in a dict images[card_name] => pygame.Surface
# Example of card_name: '2_of_hearts', 'K_of_spades', etc.

# Load each card image
images = {}
for suit in suits:
    for rank in ranks:
        card_name = f'{rank}_of_{suit}'  # e.g. '2_of_spades'
        path = f'images/cards/{card_name}.png'
        try:
            img = pygame.image.load(path).convert_alpha()
            images[card_name] = img
        except:
            print(f"Warning: Could not load {path}. Please check if the file exists.")

# We'll also load the card back image (for hidden dealer card)
try:
    back_img = pygame.image.load('images/cards/back.png').convert_alpha()
except:
    print("Warning: Could not load images/cards/back.png.")
    back_img = None

# Optionally scale images if they're too large
def scale_image(img, width=100, height=140):
    return pygame.transform.smoothscale(img, (width, height))

for key, surf in images.items():
    images[key] = scale_image(surf, 100, 140)

if back_img:
    back_img = scale_image(back_img, 100, 140)

# ---------------------- BLACKJACK FUNCTIONS ----------------------
def deal_cards(current_hand, current_deck):
    """
    Randomly picks a card from current_deck, appends to current_hand,
    and removes that card from current_deck.
    """
    index = random.randint(0, len(current_deck) - 1)
    card = current_deck[index]
    current_hand.append(card)
    current_deck.pop(index)
    return current_hand, current_deck


def calculate_score(hand):
    """
    Calculates the best possible blackjack score for a given hand,
    treating Aces as 1 or 11.
    """
    score = 0
    aces_count = 0

    for card in hand:
        # card is something like 'K_of_hearts', '10_of_spades', 'A_of_diamonds', ...
        rank = card.split('_of_')[0]  # e.g. 'K', '10', 'A'
        if rank.isdigit():
            # For '2'..'9'
            score += int(rank)
        elif rank in ['10', 'J', 'Q', 'K']:
            score += 10
        elif rank == 'A':
            score += 11
            aces_count += 1

    # If we are over 21 and have Aces, reduce by 10 for each Ace if needed
    while score > 21 and aces_count > 0:
        score -= 10
        aces_count -= 1

    return score


def draw_cards(player, dealer, reveal):
    """
    Draw the player's and dealer's cards on the screen:
    - Player: all cards face-up.
    - Dealer: if reveal == False, the first card is the back image.
    """
    # Player's cards
    for i, card in enumerate(player):
        x = 70 + (70 * i)
        y = 460 + (5 * i)
        if card in images:
            screen.blit(images[card], (x, y))
        else:
            # If missing image, just draw a fallback rect
            pygame.draw.rect(screen, 'white', [x, y, 100, 140], 0, 5)
            screen.blit(font.render(card, True, 'black'), (x + 5, y + 5))

    # Dealer's cards
    for i, card in enumerate(dealer):
        x = 70 + (70 * i)
        y = 160 + (5 * i)
        if i == 0 and not reveal:
            # Draw back if it's the first card and not revealed
            if back_img:
                screen.blit(back_img, (x, y))
            else:
                # If there's no back image
                pygame.draw.rect(screen, 'blue', [x, y, 100, 140], 0, 5)
        else:
            if card in images:
                screen.blit(images[card], (x, y))
            else:
                pygame.draw.rect(screen, 'white', [x, y, 100, 140], 0, 5)
                screen.blit(font.render(card, True, 'black'), (x + 5, y + 5))


def draw_scores(player_val, dealer_val):
    """
    Draws the player's score always;
    draws the dealer's score only if reveal_dealer == True.
    """
    # Player's score
    p_text = font.render(f'Score[{player_val}]', True, 'white')
    screen.blit(p_text, (350, 400))

    # Dealer's score if revealed
    if reveal_dealer:
        d_text = font.render(f'Score[{dealer_val}]', True, 'white')
        screen.blit(d_text, (350, 100))


def draw_game_ui(act, record, result):
    """
    Draws buttons (DEAL HAND, HIT, STAND, NEW HAND) depending on the game state.
    Also shows the record of wins/losses/draws.
    Returns a list of button rects for event handling.
    """
    button_list = []

    if not act:
        # Show DEAL HAND button if game is not active
        deal_btn = pygame.draw.rect(screen, 'white', [150, 20, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [150, 20, 300, 100], 3, 5)
        deal_text = font.render('DEAL HAND', True, 'black')
        screen.blit(deal_text, (165, 50))
        button_list.append(deal_btn)
    else:
        # If game is active, show HIT and STAND
        hit_btn = pygame.draw.rect(screen, 'white', [0, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [0, 700, 300, 100], 3, 5)
        hit_text = font.render('HIT ME', True, 'black')
        screen.blit(hit_text, (55, 735))
        button_list.append(hit_btn)

        stand_btn = pygame.draw.rect(screen, 'white', [300, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [300, 700, 300, 100], 3, 5)
        stand_text = font.render('STAND', True, 'black')
        screen.blit(stand_text, (355, 735))
        button_list.append(stand_btn)

        # Draw scoreboard at the bottom
        score_text = smaller_font.render(
            f'Wins: {record[0]}   Losses: {record[1]}   Draws: {record[2]}', True, 'white'
        )
        screen.blit(score_text, (15, 840))

    # If we have an outcome, show result message and NEW HAND button
    if result != 0:
        res_text = font.render(results[result], True, 'white')
        screen.blit(res_text, (15, 25))

        new_hand_btn = pygame.draw.rect(screen, 'white', [150, 220, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [150, 220, 300, 100], 3, 5)
        pygame.draw.rect(screen, 'black', [153, 223, 294, 94], 3, 5)

        nh_text = font.render('NEW HAND', True, 'black')
        screen.blit(nh_text, (165, 250))

        button_list.append(new_hand_btn)

    return button_list


def check_endgame(hand_act, d_score, p_score, result, totals, add):
    """
    Once the player is done (hand_act=False) and dealer >= 17,
    we check final conditions:
      - 1 => player bust
      - 2 => player wins
      - 3 => dealer wins
      - 4 => tie
    We update 'totals' if 'add' is True and we haven't recorded the result yet.
    """
    if not hand_act and d_score >= 17:
        if p_score > 21:
            result = 1  # bust
        elif d_score < p_score <= 21 or d_score > 21:
            result = 2  # player wins
        elif p_score < d_score <= 21:
            result = 3  # dealer wins
        else:
            result = 4  # tie

        if add:
            if result == 1 or result == 3:
                totals[1] += 1  # loss
            elif result == 2:
                totals[0] += 1  # win
            else:
                totals[2] += 1  # draw
            add = False

    return result, totals, add


# ---------------------- MAIN GAME LOOP ----------------------
run = True
game_deck = []

while run:
    clock.tick(fps)
    # Fill background
    screen.fill('black')

    # If we need an initial deal => give 2 cards to player and 2 to dealer
    if initial_deal:
        for _ in range(2):
            my_hand, game_deck = deal_cards(my_hand, game_deck)
            dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        initial_deal = False

    # If active => draw & update
    if active:
        player_score = calculate_score(my_hand)
        draw_cards(my_hand, dealer_hand, reveal_dealer)

        if reveal_dealer:
            dealer_score = calculate_score(dealer_hand)
            # Dealer draws until 17+
            if dealer_score < 17:
                dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)

        draw_scores(player_score, dealer_score)

    # Draw UI (buttons, etc.)
    buttons = draw_game_ui(active, records, outcome)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # If window is resized
        if event.type == pygame.VIDEORESIZE:
            # Update new WIDTH, HEIGHT
            WIDTH, HEIGHT = event.w, event.h
            # Recreate the display surface
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            # If you want to recalc positions or scale images, do it here.

        if event.type == pygame.MOUSEBUTTONUP:
            if not active:
                # If the game is not active => the only button is DEAL HAND
                if len(buttons) > 0 and buttons[0].collidepoint(event.pos):
                    # Start a new round
                    active = True
                    initial_deal = True
                    # Generate a fresh deck
                    game_deck = copy.deepcopy(base_deck * decks)
                    my_hand = []
                    dealer_hand = []
                    outcome = 0
                    hand_active = True
                    reveal_dealer = False
                    add_score = True
            else:
                # If the game is active
                # buttons[0] => HIT
                # buttons[1] => STAND
                # buttons[2] => NEW HAND (only appears if outcome != 0)
                if len(buttons) > 0 and buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                    # HIT
                    my_hand, game_deck = deal_cards(my_hand, game_deck)

                elif len(buttons) > 1 and buttons[1].collidepoint(event.pos) and not reveal_dealer:
                    # STAND
                    reveal_dealer = True
                    hand_active = False

                # If we have a 3rd button => NEW HAND
                if len(buttons) == 3 and buttons[2].collidepoint(event.pos):
                    active = True
                    initial_deal = True
                    game_deck = copy.deepcopy(base_deck * decks)
                    my_hand = []
                    dealer_hand = []
                    outcome = 0
                    hand_active = True
                    reveal_dealer = False
                    add_score = True
                    dealer_score = 0
                    player_score = 0

    # If player is still hitting and goes >= 21 => stop
    if hand_active and player_score >= 21:
        hand_active = False
        reveal_dealer = True

    # Check if the dealer is done => see who won
    outcome, records, add_score = check_endgame(hand_active, dealer_score, player_score, outcome, records, add_score)

    pygame.display.flip()

pygame.quit()
