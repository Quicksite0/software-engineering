import random
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

class HuntTheWumpus:
    """
    Core game logic for Hunt the Wumpus.
    Manages the cave map, element placement, and game state.
    """
    def __init__(self, initial_arrows=5):
        self.num_caves = 20
        self.cave_map = self._generate_cave_map()
        self.wumpus_location = -1
        self.pit_locations = []
        self.bat_locations = []
        self.player_location = -1
        self.num_arrows = initial_arrows
        self.game_over = False
        self.message = ""

        # Place the Wumpus, pits, bats, and player at the start
        self._place_game_elements()

    def _generate_cave_map(self):
        """
        Generates a cave map based on a 4x5 grid layout.
        Each cave is connected to its immediate neighbors (up, down, left, right).
        """
        cave_map = {}
        rows, cols = 4, 5
        for i in range(1, self.num_caves + 1):
            connections = []
            
            # Calculate grid position (row, col) from cave number
            row = (i - 1) // cols
            col = (i - 1) % cols
            
            # Add neighbor above
            if row > 0:
                connections.append(i - cols)
            # Add neighbor below
            if row < rows - 1:
                connections.append(i + cols)
            # Add neighbor to the left
            if col > 0:
                connections.append(i - 1)
            # Add neighbor to the right
            if col < cols - 1:
                connections.append(i + 1)
                
            cave_map[i] = connections
        
        return cave_map

    # --- MODIFIED CODE START ---
    def _place_game_elements(self):
        """Randomly places the Wumpus, pits, bats, and player in unique caves."""
        all_locations = list(range(1, self.num_caves + 1))
        
        # Shuffle the list of all caves to ensure truly random placement
        random.shuffle(all_locations)
        
        # Pop locations from the shuffled list to guarantee uniqueness
        self.wumpus_location = all_locations.pop()
        
        for _ in range(2):
            self.pit_locations.append(all_locations.pop())
            
        for _ in range(2):
            self.bat_locations.append(all_locations.pop())
            
        self.player_location = all_locations.pop()
    # --- MODIFIED CODE END ---

    def _get_neighbors(self, cave):
        """Returns a list of caves connected to the given cave."""
        return self.cave_map.get(cave, [])

    def _get_perceptions(self):
        """Checks for hazards in neighboring caves and returns corresponding messages."""
        perceptions = []
        neighbors = self._get_neighbors(self.player_location)

        for neighbor in neighbors:
            if neighbor == self.wumpus_location:
                perceptions.append("I smell a Wumpus!")
            if neighbor in self.pit_locations:
                perceptions.append("I feel a breeze.")
            if neighbor in self.bat_locations:
                perceptions.append("I hear bats.")
        return perceptions

    def _check_hazards(self, has_planks, has_bat_taxi):
        """Checks if the player's current location has a hazard and updates game state."""
        if self.player_location == self.wumpus_location:
            self.message = "The Wumpus got you! Game Over."
            self.game_over = True
            return True
        elif self.player_location in self.pit_locations:
            if has_planks:
                self.message = "You fell into a pit but used your wooden planks to escape!"
                return "planks"
            else:
                self.message = "You fell into a bottomless pit! Game Over."
                self.game_over = True
                return True
        elif self.player_location in self.bat_locations:
            if has_bat_taxi:
                self.message = "Giant bats snatch you! You can now choose your destination."
                return "bat_taxi"
            else:
                self.message = "Giant bats snatch you and drop you in a random cave!"
                possible_locations = set(range(1, self.num_caves + 1))
                possible_locations.difference_update(
                    [self.wumpus_location] + self.pit_locations + self.bat_locations
                )
                possible_locations.discard(self.player_location)
                if possible_locations:
                    self.player_location = random.choice(list(possible_locations))
                else:
                    self.player_location = random.choice(
                        [c for c in range(1, self.num_caves + 1) if c != self.player_location]
                    )
                return False
        return False

    def move_player(self, destination, has_planks, has_bat_taxi):
        """Moves the player to a new cave if the move is valid."""
        if self.game_over:
            self.message = "The game is over. Start a new game."
            return

        if destination not in self._get_neighbors(self.player_location):
            self.message = "That's not a connected cave! Try again."
            return False

        self.player_location = destination
        self.message = f"You are now in cave {self.player_location}."
        return self._check_hazards(has_planks, has_bat_taxi)
        
    def shoot_arrow(self, target_path):
        """Fires an arrow along a given path and checks for hits."""
        if self.game_over:
            self.message = "The game is over. Start a new game."
            return

        if self.num_arrows <= 0:
            self.message = "You are out of arrows! Game Over."
            self.game_over = True
            return

        self.num_arrows -= 1

        if not target_path or not isinstance(target_path, list):
            self.message = "Invalid arrow path. Please provide a list of cave numbers."
            return

        current_arrow_location = self.player_location
        valid_shot = True

        for i, target_cave in enumerate(target_path):
            if i >= 5:
                self.message = "Arrow ran out of range!"
                break

            if target_cave not in self._get_neighbors(current_arrow_location) and target_cave != current_arrow_location:
                self.message = "Arrow veered off course! It hit nothing."
                valid_shot = False
                break

            current_arrow_location = target_cave

            if current_arrow_location == self.wumpus_location:
                self.message = "You shot the Wumpus! You win!"
                self.game_over = True
                return

            if current_arrow_location == self.player_location:
                self.message = "You shot yourself! Game Over."
                self.game_over = True
                return

        if not self.game_over and valid_shot:
            if random.random() < 0.2:
                self.message = "Your shot woke the Wumpus! He moved!"
                original_wumpus_location = self.wumpus_location
                available_caves = [
                    c for c in range(1, self.num_caves + 1)
                    if c != self.player_location and c != original_wumpus_location
                ]
                if available_caves:
                    self.wumpus_location = random.choice(available_caves)
                else:
                    self.wumpus_location = random.choice(
                        [c for c in range(1, self.num_caves + 1) if c != self.player_location]
                    )
            else:
                self.message = "Arrow missed."

            if self.num_arrows == 0 and not self.game_over:
                self.message += "\nYou are out of arrows! Game Over."
                self.game_over = True
                
class WumpusGUI(ctk.CTk):
    """
    The Graphical User Interface for the Hunt the Wumpus game.
    Uses customtkinter for a modern, dark-themed design.
    """
    def __init__(self):
        super().__init__()
        
        # Configure the main window
        self.title("Hunt the Wumpus")
        self.geometry("600x800")
        
        self.buttons = []
        self.moves = 0
        self.currency = 0
        self.radar_uses_left = 0
        self.plank_uses_left = 0
        self.bat_taxi_uses_left = 0

        self.create_widgets()
        self.start_new_game()
        
    def create_widgets(self):
        """Creates and places all the GUI widgets."""
        # Main frame to center all content
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Main game UI frame (initially visible)
        self.main_game_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.main_game_frame.pack(fill="both", expand=True)

        # Store UI frame (initially hidden)
        self.store_frame = ctk.CTkFrame(self.main_frame)
        self.create_store_widgets(self.store_frame)
        
        # Start game button
        control_frame = ctk.CTkFrame(self.main_game_frame)
        control_frame.pack(pady=(10, 10), anchor="center")
        start_button = ctk.CTkButton(control_frame, text="Start New Game", command=self.start_new_game, corner_radius=8)
        start_button.pack(padx=5)
        
        # Currency label
        self.currency_label = ctk.CTkLabel(self.main_game_frame, text=f"Currency: {self.currency}", font=ctk.CTkFont(size=14, weight="bold"))
        self.currency_label.pack(pady=(0, 10), anchor="center")

        # Frame for cave buttons
        cave_frame = ctk.CTkFrame(self.main_game_frame, fg_color="transparent")
        cave_frame.pack(pady=10, padx=10, anchor="center")

        # Create 20 buttons for the caves in a 4x5 grid
        for i in range(1, 21):
            button = ctk.CTkButton(
                cave_frame,
                text=str(i),
                width=50,
                height=50,
                corner_radius=10,
                font=ctk.CTkFont(size=20, weight="bold"),
                command=lambda cave=i: self.move_player_from_gui(cave)
            )
            row = (i - 1) // 5
            col = (i - 1) % 5
            button.grid(row=row, column=col, padx=5, pady=5)
            self.buttons.append(button)

        # Frame for shooting controls
        shoot_frame = ctk.CTkFrame(self.main_game_frame)
        shoot_frame.pack(pady=10, padx=20, anchor="center")

        shoot_label = ctk.CTkLabel(shoot_frame, text="Shoot Arrow to:", font=ctk.CTkFont(size=14))
        shoot_label.pack(side="left", padx=(10, 5))
        
        self.shoot_menu = ctk.CTkOptionMenu(shoot_frame, values=[" "], width=100)
        self.shoot_menu.pack(side="left", padx=5)

        shoot_button = ctk.CTkButton(shoot_frame, text="Shoot", command=self.shoot_arrow_from_gui, corner_radius=8)
        shoot_button.pack(side="left", padx=5)
        
        # --- NEW CODE START ---
        # Frame for all tool controls (initially hidden)
        self.tools_frame = ctk.CTkFrame(self.main_game_frame)
        self.tools_frame.columnconfigure(0, weight=1)

        # Frame for Radar controls
        self.radar_control_frame = ctk.CTkFrame(self.tools_frame, fg_color="transparent")
        radar_label = ctk.CTkLabel(self.radar_control_frame, text="Radar Cave:", font=ctk.CTkFont(size=14))
        radar_label.pack(side="left", padx=(10, 5))
        
        self.radar_menu = ctk.CTkOptionMenu(self.radar_control_frame, values=[" "], width=100)
        self.radar_menu.pack(side="left", padx=5)

        self.radar_button = ctk.CTkButton(self.radar_control_frame, text="Use Radar", command=self.use_radar, corner_radius=8, state=tk.DISABLED)
        self.radar_button.pack(side="left", padx=5)

        # Frame for Bat Taxi controls
        self.bat_taxi_control_frame = ctk.CTkFrame(self.tools_frame, fg_color="transparent")
        bat_taxi_label = ctk.CTkLabel(self.bat_taxi_control_frame, text="Bat Taxi to:", font=ctk.CTkFont(size=14))
        bat_taxi_label.pack(side="left", padx=(10, 5))

        self.bat_taxi_menu = ctk.CTkOptionMenu(self.bat_taxi_control_frame, values=[" "], width=100)
        self.bat_taxi_menu.pack(side="left", padx=5)

        self.bat_taxi_button = ctk.CTkButton(self.bat_taxi_control_frame, text="Take Taxi", command=self.use_bat_taxi, corner_radius=8, state=tk.DISABLED)
        self.bat_taxi_button.pack(side="left", padx=5)
        # --- NEW CODE END ---

        # Store button
        store_button = ctk.CTkButton(self.main_game_frame, text="Open Store", command=self.open_store, corner_radius=8)
        store_button.pack(pady=10, padx=20, anchor="center")

        # Separate textbox for instructions (non-editable)
        self.instructions_box = ctk.CTkTextbox(self.main_game_frame, wrap="word", width=550, height=95)
        self.instructions_box.pack(pady=5, padx=20, anchor="center")
        self.instructions_box.insert("0.0", self.get_initial_instructions())
        self.instructions_box.configure(state="disabled")

        # Separate textbox for dynamic game messages
        self.message_box = ctk.CTkTextbox(self.main_game_frame, wrap="word", width=550, height=155)
        self.message_box.pack(pady=10, padx=20, anchor="center")

        # Exit button
        self.exit_button = ctk.CTkButton(self, text="Exit", command=self.quit, corner_radius=8, fg_color="#b00020")
        self.exit_button.pack(pady=10, padx=20, anchor="center")

    def create_store_widgets(self, parent_frame):
        """Creates the widgets for the in-game store."""
        store_label = ctk.CTkLabel(parent_frame, text="Store", font=ctk.CTkFont(size=18, weight="bold"))
        store_label.pack(pady=(10, 5))

        # Radar
        radar_frame = ctk.CTkFrame(parent_frame)
        radar_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(radar_frame, text="Radar (2 uses)").pack(side="left", padx=5)
        self.buy_radar_btn = ctk.CTkButton(radar_frame, text="Buy (50)", command=lambda: self.buy_ability("radar"), corner_radius=8)
        self.buy_radar_btn.pack(side="right", padx=5)
        self.radar_uses_label = ctk.CTkLabel(radar_frame, text=f"Uses Left: {self.radar_uses_left}")
        self.radar_uses_label.pack(side="right", padx=5)
        
        # Wooden Planks
        planks_frame = ctk.CTkFrame(parent_frame)
        planks_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(planks_frame, text="Wooden Planks (1 use)").pack(side="left", padx=5)
        self.buy_planks_btn = ctk.CTkButton(planks_frame, text="Buy (75)", command=lambda: self.buy_ability("planks"), corner_radius=8)
        self.buy_planks_btn.pack(side="right", padx=5)
        self.plank_uses_label = ctk.CTkLabel(planks_frame, text=f"Uses Left: {self.plank_uses_left}")
        self.plank_uses_label.pack(side="right", padx=5)
        
        # Bat Taxi Service
        bat_taxi_frame = ctk.CTkFrame(parent_frame)
        bat_taxi_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(bat_taxi_frame, text="Bat Taxi Service (1 use)").pack(side="left", padx=5)
        self.buy_bat_taxi_btn = ctk.CTkButton(bat_taxi_frame, text="Buy (60)", command=lambda: self.buy_ability("bat_taxi"), corner_radius=8)
        self.buy_bat_taxi_btn.pack(side="right", padx=5)
        self.bat_taxi_uses_label = ctk.CTkLabel(bat_taxi_frame, text=f"Uses Left: {self.bat_taxi_uses_left}")
        self.bat_taxi_uses_label.pack(side="right", padx=5)
        
        # Close button
        close_button = ctk.CTkButton(parent_frame, text="Close Store", command=self.close_store, corner_radius=8, fg_color="#b00020") 
        close_button.pack(pady=5, padx=20, anchor="center")

    def open_store(self):
        """Hides the main game frame and displays the store frame."""
        self.main_game_frame.pack_forget()
        self.store_frame.pack(fill="both", expand=True)
        self.exit_button.pack_forget()
        self.update_display()
            
    def close_store(self):
        """Hides the store frame and displays the main game frame."""
        self.store_frame.pack_forget()
        self.main_game_frame.pack(fill="both", expand=True)
        self.exit_button.pack(pady=10, padx=20, anchor="center")
        self.update_display()

    def buy_ability(self, ability):
        """Handles purchasing an ability from the store."""
        price_map = {"radar": 50, "planks": 75, "bat_taxi": 60}
        price = price_map.get(ability)
        
        if self.currency >= price:
            self.currency -= price
            self.game.message = f"Purchased {ability.replace('_', ' ')} for {price} currency."
            if ability == "radar":
                self.radar_uses_left += 2
            elif ability == "planks":
                self.plank_uses_left += 1
            elif ability == "bat_taxi":
                self.bat_taxi_uses_left += 1
        else:
            self.game.message = f"Not enough currency to buy {ability.replace('_', ' ')}."
            
        self.update_display()

    def start_new_game(self):
        """Initializes a new game with a default of 5 arrows and resets abilities."""
        self.game = HuntTheWumpus(initial_arrows=5)
        self.moves = 0
        self.currency = 0
        self.radar_uses_left = 0
        self.plank_uses_left = 0
        self.bat_taxi_uses_left = 0
        self.game.message = "Starting a new game. Good luck!"
        self.update_display()

    def get_initial_instructions(self):
        """Returns the game's starting instructions as a string."""
        return (
            "Welcome to Hunt the Wumpus!\n"
            "Objective: Hunt down the Wumpus without falling into pits or being carried by bats.\n"
            "To move, click on a connected cave button.\n"
            "To shoot, select a connected cave from the dropdown menu and click Shoot.\n"
            "Use currency earned to buy abilities in the store."
        )
    
    def move_player_from_gui(self, destination):
        """Handles a player's move initiated by a button click."""
        if self.game.game_over:
            return
        self.moves += 1
        
        hazard_check = self.game.move_player(destination, self.plank_uses_left > 0, self.bat_taxi_uses_left > 0)
        
        if hazard_check == "planks":
            self.plank_uses_left -= 1
        elif hazard_check == "bat_taxi":
            self.bat_taxi_uses_left -= 1
            # Instead of a popup, the bat taxi controls are now on the main page.
            # The player must use the controls to choose a new location.
            self.game.message += "\nChoose a cave with the Bat Taxi controls to fly to."
            
        self.update_display()
        if hazard_check is True:
            messagebox.showinfo("Game Over", self.game.message)

    def shoot_arrow_from_gui(self):
        """Handles shooting an arrow based on user input from the dropdown menu."""
        if self.game.game_over:
            return
        
        target_cave_str = self.shoot_menu.get()
        if target_cave_str and target_cave_str.strip() != " ":
            target_cave = int(target_cave_str)
            self.game.shoot_arrow([target_cave])
            
            if self.game.game_over and "You shot the Wumpus!" in self.game.message:
                self.award_currency()
                
            self.update_display()
            if self.game.game_over:
                messagebox.showinfo("Game Over", self.game.message)
        else:
            self.game.message = "You must select a cave to shoot at."
            self.update_display()

    def award_currency(self):
        """Awards currency based on number of moves."""
        reward = max(100 - (self.moves * 2), 10)
        self.currency += reward
        self.game.message += f"\n You won! You receive {reward} currency."

    def use_radar(self):
        """Uses the Radar ability to check a cave."""
        if self.radar_uses_left > 0:
            target_cave_str = self.radar_menu.get()
            if target_cave_str and target_cave_str.strip() != " ":
                target_cave = int(target_cave_str)
                self.radar_uses_left -= 1
                self.game.message = self.check_cave_contents(target_cave)
                self.update_display()
            else:
                self.game.message = "Please select a cave to use the radar on."
                self.update_display()
        else:
            self.game.message = "You don't have any Radar uses left."
            self.update_display()

    def use_bat_taxi(self):
        """Uses the Bat Taxi ability to move to any cave."""
        if self.bat_taxi_uses_left > 0:
            destination_str = self.bat_taxi_menu.get()
            if destination_str and destination_str.strip() != " ":
                destination = int(destination_str)
                self.bat_taxi_uses_left -= 1
                self.game.player_location = destination
                self.game.message = f"The bats dropped you off in cave {destination}."

                # Check for hazards at the new location
                hazard_check = self.game._check_hazards(self.plank_uses_left > 0, self.bat_taxi_uses_left > 0)
                if hazard_check == "planks":
                    self.plank_uses_left -= 1
                
                self.update_display()
                if hazard_check is True:
                    messagebox.showinfo("Game Over", self.game.message)
            else:
                self.game.message = "Please select a cave to fly to."
                self.update_display()
        else:
            self.game.message = "You don't have any Bat Taxi uses left."
            self.update_display()

    def check_cave_contents(self, cave_num):
        """Returns the contents of a specified cave."""
        if cave_num == self.game.wumpus_location:
            return f"Radar scan of cave {cave_num}: Wumpus is there!"
        elif cave_num in self.game.pit_locations:
            return f"Radar scan of cave {cave_num}: A bottomless pit is there."
        elif cave_num in self.game.bat_locations:
            return f"Radar scan of cave {cave_num}: Giant bats are there."
        else:
            return f"Radar scan of cave {cave_num}: It's empty."
    
    def update_display(self):
        """Updates the GUI with the current game state, currency, and abilities."""
        self.currency_label.configure(text=f"Currency: {self.currency}")
        
        self.buy_radar_btn.configure(state=tk.NORMAL if self.currency >= 50 else tk.DISABLED)
        self.buy_planks_btn.configure(state=tk.NORMAL if self.currency >= 75 else tk.DISABLED)
        self.buy_bat_taxi_btn.configure(state=tk.NORMAL if self.currency >= 60 else tk.DISABLED)

        self.radar_uses_label.configure(text=f"Uses Left: {self.radar_uses_left}")
        self.plank_uses_label.configure(text=f"Uses Left: {self.plank_uses_left}")
        self.bat_taxi_uses_label.configure(text=f"Uses Left: {self.bat_taxi_uses_left}")

        # Clear the dynamic message box
        self.message_box.configure(state="normal")
        self.message_box.delete("0.0", "end")
        
        # Game state information
        self.message_box.insert("end", f"--- Current State ---\n")
        self.message_box.insert("end", f"You are in cave {self.game.player_location}.\n")
        
        neighbors = self.game._get_neighbors(self.game.player_location)
        self.message_box.insert("end", f"Connected caves: {neighbors}\n")
        
        self.message_box.insert("end", f"Arrows remaining: {self.game.num_arrows}\n\n")

        # Update shoot menu options
        neighbor_strings = [str(n) for n in neighbors]
        if not neighbor_strings:
            self.shoot_menu.configure(values=[" "], state=tk.DISABLED)
            self.shoot_menu.set(" ")
        else:
            self.shoot_menu.configure(values=neighbor_strings, state=tk.NORMAL)
            self.shoot_menu.set(neighbor_strings[0])

        # --- MODIFIED CODE START ---
        # Update tools frame visibility and its contents
        has_tools = self.radar_uses_left > 0 or self.bat_taxi_uses_left > 0
        if has_tools:
            self.tools_frame.pack(pady=5, padx=20, anchor="center")
        else:
            self.tools_frame.pack_forget()

        # Update radar menu options and visibility
        all_caves = [str(i) for i in range(1, 21)]
        if self.radar_uses_left > 0:
            self.radar_control_frame.pack(pady=5, padx=0)
            self.radar_menu.configure(values=all_caves, state=tk.NORMAL)
            self.radar_button.configure(state=tk.NORMAL)
            self.radar_menu.set(all_caves[0])
        else:
            self.radar_control_frame.pack_forget()

        # Update bat taxi menu options and visibility
        if self.bat_taxi_uses_left > 0:
            self.bat_taxi_control_frame.pack(pady=5, padx=0)
            self.bat_taxi_menu.configure(values=all_caves, state=tk.NORMAL)
            self.bat_taxi_button.configure(state=tk.NORMAL)
            self.bat_taxi_menu.set(all_caves[0])
        else:
            self.bat_taxi_control_frame.pack_forget()
        # --- MODIFIED CODE END ---

        # Perceptions
        perceptions = self.game._get_perceptions()
        for p in perceptions:
            self.message_box.insert("end", f"{p}\n")
        
        self.message_box.insert("end", f"\nMessage: {self.game.message}\n")
        self.message_box.configure(state="disabled")

        # Update button colors based on game state
        for i, button in enumerate(self.buttons):
            cave_num = i + 1
            if cave_num == self.game.player_location:
                button.configure(fg_color="#34547c", state=tk.NORMAL)
            elif cave_num in neighbors:
                button.configure(fg_color="#3c6f4c", state=tk.NORMAL)
            else:
                button.configure(fg_color="#555555", state=tk.DISABLED)
                
if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = WumpusGUI()
    app.mainloop()