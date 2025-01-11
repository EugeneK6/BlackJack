
1. **`Player` class**  
   - Represents a player (which can be a human or the dealer).  
   - Stores the player's name, a list of dealt cards (as strings), and a list of their numerical values (the `score` list).  
   - Provides simple methods such as `reset()` (to clear the cards and scores), `add_card()` (to add a new card value), and `get_total()` (to return the sum of the current score).

2. **`BlackjackGame` class**  
   - Manages the entire Blackjack game session, including the **Tkinter interface** (UI elements), the **deck**, the **players** (player and dealer), and game **logic**.  
   - Maintains **global counters** (`player_wins`, `dealer_wins`, `ties`), which track the number of wins, losses, and ties.  
   - Organizes all major methods:  
     - **`setup_ui()`** creates and arranges the main window, frames, labels, and buttons.  
     - **`shuffle_deck()`** creates and shuffles the card deck, then distributes the initial two cards to both the player and the dealer.  
     - **`deal_card_to()`** deals a card either to the dealer or the player. The dealer’s second card is displayed as a “back” image until the round ends.  
     - **`stand()`, `player_hit()`, `dealer_hit()`** respond to corresponding button clicks.  
     - **`show_result_and_disable_buttons()`** displays a message for the game result, updates the scoreboard, and disables buttons once the round ends.  
     - **`save_game()`, `load_game()`** provide basic saving/loading of the current game state in JSON format.  
     - **`run()`** starts the Tkinter event loop so the application remains interactive.  
     - **`get_current_state()`** returns a small dictionary of the current game’s state for debugging or saving.

3. **Hidden Dealer Card**  
   - The dealer’s second card is initially shown face-down (using `back_img`), but the game logic still counts its real value for calculating totals and bust conditions.  
   - Once a round ends (when the player stands, busts, or 21 is detected), the **`reveal_dealer_hidden_card()`** method is called from **`show_result_and_disable_buttons()`** to show the actual dealer card image.

4. **Program Entry Point**  
   - In the `if __name__ == '__main__':` block, a new `BlackjackGame` instance is created.  
   - **`game.run()`** is called to start the Tkinter main loop, making the application run until the user closes the window.  
