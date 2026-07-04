from sudoku_better_version_ import SudokuSolver
import numpy as np
import multiprocessing
import random
from tkinter import filedialog, messagebox, Menu,StringVar
import numpy as np
import customtkinter
from functools import partial
import re
import time
from tkinter import END
from tkinter import filedialog, messagebox, Menu
import pygame



solver =SudokuSolver()

class Sudoku_GUI:
    def __init__(self, dim, difficulty):
        # Initialize the Sudoku solver with specified dimensions and difficulty level
        self.initialize_solver(dim, difficulty)
        # Generate a Sudoku grid and insert it into the solver's grid
        solver.grid_insert(solver.create_sudoku(), solver.dim)
        # Set up the graphical user interface (GUI) for the Sudoku game
        self.setup_gui()

    def initialize_solver(self, dim, difficulty):
        """
        Initializes the Sudoku solver with dimensions and difficulty level.

        Args:
        - dim (int): Dimension of the Sudoku grid (e.g., 9 for a 9x9 grid).
        - difficulty (str): Difficulty level of the Sudoku puzzle.

        Initializes the following attributes of the solver:
        - domains: Dictionary to store domain values for each cell.
        - related_cells: Dictionary to store related cells for each cell.
        - length_values: Dictionary to store length values.
        - solution: List to store the solution steps.

        Sets the dimensions, grid dimensions, and difficulty level for the solver.
        """
        solver.domains = {}  # Initialize dictionary to store domain values for each cell
        solver.related_cells = {}  # Initialize dictionary to store related cells for each cell
        solver.length_values = {}  # Initialize dictionary to store length values
        solver.solution = []  # Initialize list to store solution steps

        solver.dim = int(dim)  # Set dimension of the Sudoku grid
        solver.grid_dim = np.sqrt(int(dim))  # Calculate grid dimension based on square root of dim
        solver.difficulty = difficulty  # Set the difficulty level of the Sudoku puzzle

    def setup_gui(self, entries_config=None):
        """
        Sets up the GUI for the Sudoku application.

        Args:
        - entries_config (dict): Configuration for individual Sudoku grid entries.

        Initializes the main window and sets up various components:
        - Creates the root window using customtkinter.CTk with a white smoke foreground color.
        - Sets the window title and size.
        - Initializes dictionaries to store CTkEntry widgets and their indices.
        - Creates Sudoku grid entries based on entries_config (if provided).
        - Creates buttons for user interactions.
        - Initializes game-related attributes like counter and timer.
        - Sets up labels for displaying game status.
        - Configures the menu bar for additional functionalities.
        - Starts the main event loop (mainloop()) to run the GUI application.
        """
        self.root = customtkinter.CTk(fg_color="whitesmoke")  # Create main window with white smoke foreground color
        self.root.title("Sudoku")  # Set window title

        window_size = "1920x1080" if solver.dim == 16 else "860x720"
        self.root.geometry(window_size)

        self.matrix_entries = {}  # Dictionary to store CTkEntry widgets mapped to their positions
        self.entries_index = {}  # Dictionary to store CTkEntry widgets mapped to (row, col) indices
        self.counter = 0  # Initialize step counter for the game

        self.create_entries(entries_config)  # Create Sudoku grid entries based on configuration (if provided)
        self.create_buttons()  # Create buttons for user interactions

        self.running = False  # Flag to indicate if the game is running or paused

        self.create_labels()  # Create labels for displaying game status
        self.start_timer()  # Start the timer for tracking game duration
        self.menu_bar()  # Configure the menu bar for additional functionalities

        self.root.mainloop()  # Start the main event loop to run the GUI application

    def configure_entry(self, row, col, entry, state='disabled', color='skyblue'):
        """
        Configures a CTkEntry widget based on Sudoku grid value.

        Args:
        - row (int): Row index in the Sudoku grid.
        - col (int): Column index in the Sudoku grid.
        - entry (CTkEntry): Entry widget to configure.
        - state (str): State of the entry ('disabled' or 'normal').
        - color (str): Foreground color of the entry ('skyblue' or any valid color).

        Sets the appearance of the entry widget based on the Sudoku grid value:
        - Inserts the Sudoku value and applies the specified state and color if the value is not zero.
        - Sets the foreground color to 'white' if the Sudoku value is zero.
        """
        sudoku_value = solver.sudoku[row][col]

        if sudoku_value != 0:
            entry.insert(0, str(sudoku_value))  # Insert Sudoku value if not zero
            entry.configure(state=state, fg_color=color)  # Apply state and color
        else:
            entry.configure(fg_color='white')  # Set foreground color to white for zero value


    def create_entries(self, entries_config=None):
        """
        Create CTkEntry widgets for the Sudoku grid.

        Args:
        - entries_config (dict): Optional dictionary with configurations for specific entries.
                                 Keys are (row, col) tuples, values are [state, color].
        """
        dim = solver.dim
        grid_dim = solver.grid_dim
        subgrid_colors = ['lightskyblue', 'navyblue']

        for row in range(dim):
            for col in range(dim):
                # Determine subgrid color based on row and column indices
                subgrid_row_start = (row // grid_dim) * grid_dim
                subgrid_col_start = (col // grid_dim) * grid_dim
                color_index = (subgrid_row_start // grid_dim + subgrid_col_start // grid_dim) % 2

                # Create CTkEntry widget with specified properties
                entry = customtkinter.CTkEntry(
                    self.root,
                    height=50,
                    width=55,
                    font=("Arial", 22),
                    justify='center',
                    border_color=subgrid_colors[color_index],
                    border_width=2,
                    corner_radius=4
                )

                # Apply configurations from entries_config if provided
                if entries_config and (row, col) in entries_config:
                    state, color = entries_config[(row, col)]
                    self.configure_entry(row, col, entry, state, color)
                else:
                    self.configure_entry(row , col , entry)

                # Bind events to the entry widget
                entry.bind("<KeyRelease>", partial(self.on_key_release, widget=entry))
                entry.bind("<FocusIn>", partial(self.on_focus_in, widget=entry))
                entry.bind("<FocusOut>", partial(self.on_focus_out, widget=entry))

                # Position the entry widget in the grid
                entry.place(x=100 + col * 54, y=50 + row * 52)

                # Store mappings of entry widget to (row, col) and (row, col) to entry widget
                self.matrix_entries[entry] = (row, col)
                self.entries_index[(row, col)] = entry



    def create_labels(self):
        self.time_label = customtkinter.CTkLabel(self.root, text="00:00", font=("arial", 38))
        self.time_label.place(x=200 + solver.dim * 52 , y = 100 )

        self.counter_label = customtkinter.CTkLabel(self.root, text="0", font=("arial", 38))
        self.counter_label.place(x=200 + solver.dim *56 , y=200 )

    def create_buttons(self):
        dim = solver.dim  # Assuming solver.dim is defined and accessible here
        # Define button properties in a list for easier management
        button_properties = [
            ("Solve", self.solve, "green"),  # Button to solve the game
            ("Clean", self.clean_matrix, "red"),  # Button to clean/reset the matrix
            ("New Game", self.create_game, 'lightblue3')  # Button to create a new game
        ]

        # Loop through each button property to create and place the buttons
        for text, command, color in button_properties:
            # Create a button with custom properties
            button = customtkinter.CTkButton(self.root, text=text, command=command, height=35, width=100,
                                             fg_color=color)

            # Place buttons based on their text label
            if text == "Solve":
                button.place(x=solver.dim * 12, y=50 + solver.dim * 53)
            elif text == "Clean":
                button.place(x=solver.dim * 32, y=50 + solver.dim * 53)
            elif text == "New Game":
                button.place(x=solver.dim * 52, y=50 + solver.dim * 53)

    def menu_bar(self ):

        # Create a File menu
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        # Adding a file menu
        file_menu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_game)
        file_menu.add_command(label="Save", command=self.save_game)
        file_menu.add_command(label="Exit", command=self.root.destroy)
    def open_game(self):
        """
        Open a saved Sudoku game from a file and initialize the game board accordingly.
        """
        # Hide the main window while the file dialog is open
        self.root.withdraw()

        # Ask the user to select a file to open
        file_path = filedialog.askopenfilename(defaultextension=".txt")

        # Check if the user canceled the file dialog
        if not file_path:
            print("Open operation canceled.")
            self.root.deiconify()  # Restore the main window
            return

        try:
            # Read the content of the selected file
            with open(file_path, 'r') as new_sudoku:
                # Parse each line in the file
                for line in new_sudoku:
                    if line.startswith('game dim '):
                        # Extract the dimension of the Sudoku grid
                        dim = int(line[len('game dim '):].strip())
                        sudoku = np.zeros((dim, dim), dtype=int)
                        entries_config = {}

                    elif line.startswith('time '):
                        # Extract the total seconds
                        self.total_seconds = int(line[len('time '):].strip())
                    elif line.startswith('step count '):
                        # Extract the step count
                        self.counter = int(line[len('step count '):].strip())

                    elif line.startswith('difficulty '):
                        # Extract the step count
                         difficulty = int(line[len('difficulty '):].strip())

                    else:
                        # Parse the line for entry values and configurations
                        pattern = r'(\d+), (\d+), (\d+), color (\w+), state (\w+)'
                        # Using re.match to apply the pattern to the string
                        match = re.match(pattern, line)
                        if match:
                            value = int(match.group(1))
                            row = int(match.group(2))
                            col = int(match.group(3))
                            color_name = match.group(4)
                            state = match.group(5)

                            # Update Sudoku grid with parsed values
                            sudoku[row, col] = value

                            # Store entry configurations for later creation
                            entries_config[(row, col)] = [state, color_name]

                # Set settings to the Solver Class
                self.initialize_solver(dim, difficulty)

                # Insert Sudoku grid into the solver
                solver.grid_insert(sudoku, dim)

                # Create the graphical user interface
                self.setup_gui(entries_config)







        except Exception as e:
            print(f"Error opening file: {e}")
            return

        print("Open operation completed.")

    def update_entry(self, row, col, value, color, entry_state):
        """
        Update the specified Entry widget with the provided value, color, and state.

        Parameters:
        - row: Row index of the Entry widget in the grid
        - col: Column index of the Entry widget in the grid
        - value: Value to be inserted into the Entry widget
        - color: Desired foreground color for the Entry widget
        - entry_state: Desired state ('normal', 'disabled', etc.) for the Entry widget
        """
        # Retrieve the Entry widget from self.entries_index using (row, col) as key
        entry = self.entries_index[(row, col)]


        if entry:
            # Clear the current content of the Entry widget and insert the new value
            entry.delete(0, END)
            entry.insert(0, str(value))

            # Configure the Entry widget with the specified foreground color and state
            entry.configure(fg_color=color, state=entry_state)
        else:
            print(f"No Entry widget found at position ({row}, {col}) in self.entries_index.")



    def save_game(self):
        """
        Save the current state of the game to a file.
        """
        try:
            # Open a file dialog to get the save file path
            file_path = filedialog.asksaveasfilename(defaultextension=".txt")
            # Check if the user canceled the file dialog
            if not file_path:
                print("Save operation canceled.")
                return

            with open(file_path, 'w') as save_current_game:
                # Write header or any other information
                save_current_game.write(f"game dim {solver.dim}\n")
                save_current_game.write(f"time {self.total_seconds}\n")
                save_current_game.write(f"step count {self.counter}\n")
                save_current_game.write(f"difficulty {solver.difficulty}\n")


                # Iterate through all widgets in the grid

                for (row, col) in self.matrix_entries.values():
                    widget_info = self.entries_index[(row,col)]
                    value = widget_info.get()  # Get text value of the widget
                    fg_color = widget_info.cget('fg_color')  # Get foreground color
                    entry_state = widget_info.cget('state')

                        # Convert value to integer if possible

                    try:
                        value = int(value)

                    except ValueError:

                        value = 0
                    # Write widget information to the file
                    save_current_game.write(f"{value}, {row}, {col}, color {fg_color}, state {entry_state}\n")


            print("Save operation completed.")

        except Exception as e:
            print(f"Error saving file: {e}")





    def solve(self):
        """
        Solve the Sudoku puzzle and display the solution (if found).

        Steps:
        1. Check if the game has ended.
        2. Insert initial Sudoku grid.
        3. Attempt to find a solution using the solver.
        4. If a solution exists, display the first solution found.
        5. Display the number of solutions found.
        6. Insert the solution values into the GUI.
        """
        # Step 1: Check if the game has ended (assumed method self.game_end exists)
        self.game_end()

        # Step 2: Insert the initial Sudoku grid into the solver
        solver.grid_insert(solver.create_sudoku_matrix(solver.domains), solver.dim)

        # Step 3: Attempt to find a solution using the solver
        exist_solution = solver.Solver()  # Assuming this checks if a solution exists
        # Step 4: If a solution exists, display the first solution found
        if exist_solution:
            num_solutions = len(solver.solved_sudoku)
            self.solution = solver.create_sudoku_matrix(solver.solved_sudoku.pop(0))
            # Step 5: Display the number of solutions found
            self.solution_count = customtkinter.CTkLabel(self.root, text="Solutions Found: " + str(num_solutions),
                                                         font=("Arial", 20))
            self.solution_count.place(x=(100 + solver.dim * 52) // 2, y=10)

        # Step 6: Insert the solution values into the GUI
        print(exist_solution)
        self.insert_values(0, 0, exist_solution)



    def insert_values(self, row, col, exist_solution):
        """
        Insert values into the entry widgets based on the provided solution.

        Parameters:
        - row: Current row index
        - col: Current column index
        - exist_solution: Boolean indicating if a solution exists
        """
        if row < solver.dim:
            if col < solver.dim:
                if exist_solution:
                    # If a solution exists, insert the solution value into the entry
                    entry_widget = self.entries_index[row, col]
                    entry_widget.delete(0, END)
                    entry_widget.insert(0, str(self.solution[row,col]))
                    entry_widget.configure(state='disabled')
                else:
                    # If no solution exists, change text color to indicate no solution
                    entry_widget = self.entries_index[row, col]
                    if entry_widget.cget('state') != 'disabled':
                        entry_widget.configure(fg_color='lightsalmon')

                # Schedule the next insert_values call for the next column
                self.root.after(35, self.insert_values, row, col + 1, exist_solution)
            else:
                # Schedule the next insert_values call for the next row
                self.root.after(75, self.insert_values, row + 1, 0, exist_solution)




    def on_focus_in(self, event, widget):
        """
        Handles the event when an entry widget gains focus.

            Args:
            - event: The event object associated with the focus in event.
            - widget: The entry widget that gained focus.
        """

        index = self.matrix_entries[widget]  # Get the index (row, column) of the widget
        key = (index[0], index[1])
        self.change_color(key)


    def play_sound(self):
        # Play a sound if cursor on an entry
        pygame.mixer.init()
        music_file = "pop_sound.mp3"
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(1)
    def change_color(self, index):
        """
        Change foreground and background color of an entry widget and related cells.

        Args:
        - entry: The entry widget to change color.

        Changes the foreground to 'lightblue' and background to 'gray' of the given entry.
        Iterates through related cells and changes color if their current foreground color is 'white'.
        """


        # Change color of the current entry
        def change(entry):
            entry.configure(fg_color='lightsteelblue', bg_color='gray')

        related_cells = solver.related_cells[index]
        # Get related cells for the current cell from solver's related_cells

        # Iterate through related cells and change color if current color is 'white'
        for cell in related_cells:
            cell_row, cell_col = cell
            related_entry = self.entries_index[cell_row, cell_col]

            if related_entry.cget('fg_color') == 'white':
                # Use lambda to pass the current related_entry to the change_color function
                self.root.after(30, lambda e=related_entry: change(e))

    def on_focus_out(self, event, widget):
        """
        Handles the event when an entry widget loses focus.

        Args:
        - event: The event object associated with the focus out event.
        - widget: The entry widget that lost focus.

        Resets the color of related entry widgets to 'white' on 'white' background
        if their current foreground color is 'lightblue'.
        """
        # Get the index (row, column) of the widget from matrix_entries
        index = self.matrix_entries[widget]
        row, col = index[0], index[1]

        # Get related cells for the current cell from solver's related_cells
        related_cells = solver.related_cells[(row, col)]

        # Iterate through related cells and reset color if current color is 'lightblue'
        for cell in related_cells:
            cell_row, cell_col = cell
            entry = self.entries_index[cell_row, cell_col]

            if entry.cget('fg_color') == 'lightsteelblue':
                entry.configure(fg_color='white', bg_color='white')


    def on_key_release(self, event, widget):
        """
        Handles the event when a key is released in an entry widget.

        Args:
        - event: The event object associated with the key release event.
        - widget: The entry widget where the key was released.

        Processes the entry, validates it, updates solver and UI accordingly,
        handles repeated entries, and updates the counter if necessary.
        """
        entry = widget
        entry_value = entry.get()

        # Get the index (row, column) of the widget from matrix_entries
        index = self.matrix_entries[widget]

        # If entry value is empty, remove element and reset color to 'white'
        if len(entry_value) == 0:
            self.remove_element(index)
            entry.configure(fg_color='white')
            return

        # Validate entry
        if not self.is_valid_entry(entry_value):
            self.handle_invalid_entry(entry, index)
            return

        # Check for repeated entry
        repeated = self.is_repeated_entry(index, entry_value)

        # Update solver and UI based on the entry value
        if self.update_solver(index, entry_value):
            self.play_sound()
            entry.configure(fg_color="palegreen")  # Valid entry color
        else:
            self.handle_solver_failure(entry, index, entry_value)  # Failed entry color

        # Increment counter if entry is not repeated
        if not repeated:
            self.increment_counter()

    def is_valid_entry(self, entry_value):
        return entry_value.isdigit() and 1 <= int(entry_value) <= solver.dim

    def handle_invalid_entry(self, entry, index):
        entry.configure(fg_color="tomato")
        # Schedule the reset of the background color and deletion of the entry's content after 400 milliseconds
        entry.after(500, lambda: self.reset_entry(entry))

    def reset_entry(self, entry):
        entry.configure(fg_color="white")
        entry.delete(0, 'end')



    def is_repeated_entry(self, index, entry_value):
        return len(solver.domains[index]) == 1 and solver.domains[index] == {int(entry_value)}

    def update_solver(self, index, entry_value):

        solver.domains[index] = {int(entry_value)}
        return solver.is_valid(solver.domains, index[0], index[1], int(entry_value))

    def handle_solver_failure(self, entry, index, entry_value):
        solver.domains[index] = {int(entry_value)}
        entry.configure(fg_color="lightsalmon")

    def increment_counter(self):
        self.counter += 1
        self.counter_label.configure(text=str(self.counter))



    def remove_element(self, index):
        # Reset the domain of the given index to contain all possible values (1 to dim)
        solver.domains[index] = set(range(1, solver.dim + 1))


    def clean_matrix(self):
        # Initialize a zero matrix of the appropriate dimensions
        self.matrix = np.zeros((solver.dim, solver.dim))

        # Iterate over each cell in the matrix
        for row in range(solver.dim):
            for col in range(solver.dim):
                # Ensure the entry is writable
                self.entries_index[row, col].configure(state='normal')

                # Reset the foreground color to white
                self.entries_index[row, col].configure(fg_color="white")

                # Clear the content of the entry widget
                self.entries_index[row, col].delete(0, END)

        # Insert the zero matrix into the solver's grid

        # Set settings to the Solver Class
        self.initialize_solver(solver.dim, solver.difficulty)

        # Insert the zero's grid into the solver's grid
        solver.grid_insert(self.matrix, solver.dim)



    def start_timer(self):
        # Define the time difficulty relation based on dimension and difficulty
        time_difficulty_relation = {
            (9, (65, 69)): 25 , (9, (70, 74)):20 , (9, (75, 80)):15 ,
            (16, (65, 69)): 40, (16, (70 ,74)):30 , (16, (75 ,80)):25
        }

        # Determine the key for the current dimension and difficulty category
        difficulty_key = (solver.dim, solver.difficulty_category)

        # Initialize the total seconds for the timer
        self.total_seconds = 60 * time_difficulty_relation[difficulty_key]

        # Start the timer if not already running
        if not self.running:
            self.running = True
            self.update_timer()



    def update_timer(self):
        # Check if there are seconds left in the timer
        if self.total_seconds > 0:
            # Decrement the total seconds by 1
            self.total_seconds -= 1

            # Update the timer label with the new time
            self.time_label.configure(text=self.format_time())

            # Schedule the update_timer method to be called again after 1000 milliseconds (1 second)
            self.root.after(1000, self.update_timer)
        else:
            # If the timer has run out, call the game_end method
            self.game_end()

    def game_end(self):
        # Set the total seconds to 0 (in case it wasn't already exactly 0)
        self.total_seconds = 0

        # Update the timer label to indicate that the game is over
        self.time_label.configure(text="Game Over")

    def format_time(self):
        # Calculate the number of minutes and seconds from total_seconds
        minutes, seconds = divmod(self.total_seconds, 60)

        # Return the time formatted as MM:SS
        return f"{minutes:02}:{seconds:02}"
    def create_game(self):
        self.root.destroy()
        Start_SudokuGUI()


class Start_SudokuGUI:
    def __init__(self):
        self.setup_gui()

    def setup_gui(self):
        # Create the main window for selecting Sudoku dimension and difficulty
        self.start_widget = customtkinter.CTk()
        self.start_widget.title("Select Sudoku Dimension")
        self.start_widget.geometry("480x240")

        # Define available puzzle dimensions and difficulty levels
        puzzle_dims = ["16", "9"]
        self.difficulties = ["Easy", "Medium", "Hard"]

        # Initialize variables to store selected size and difficulty
        self.selected_size = StringVar(value=puzzle_dims[0])
        self.selected_difficulty = StringVar(value=self.difficulties[0])

        # Configure the grid layout for the window
        self.start_widget.columnconfigure(0, weight=1)
        self.start_widget.columnconfigure(1, weight=1)

        # Create radio buttons for selecting puzzle dimensions
        for index, option in enumerate(puzzle_dims):
            dim = customtkinter.CTkRadioButton(self.start_widget, text=f"{option}x{option}",
                                               variable=self.selected_size, value=option)
            dim.grid(row=index, column=0, padx=10, pady=5, sticky="w")

        # Create radio buttons for selecting difficulty levels
        for index, option in enumerate(self.difficulties):
            diff = customtkinter.CTkRadioButton(self.start_widget, text=option,
                                                variable=self.selected_difficulty, value=option.lower())
            diff.grid(row=index, column=1, padx=30, pady=20, sticky="w")

        # Create a "Start" button to begin the Sudoku game
        solve_button = customtkinter.CTkButton(self.start_widget, text="Start", command=self.get_size)
        solve_button.grid(row=max(len(puzzle_dims), len(self.difficulties)), column=0, columnspan=2, padx=40, pady=20)

        # Enter the main event loop to handle GUI events
        self.start_widget.mainloop()

    def get_size(self):
        # Retrieve the selected puzzle size and difficulty level
        size = self.selected_size.get()

        # Define difficulty ranges based on selected difficulty level
        difficulty_ranges = {
            "easy": (65, 69),
            "medium": (70, 74),
            "hard": (75,80)
        }

        # Retrieve the range of difficulty for the selected difficulty level
        difficulty = difficulty_ranges[self.selected_difficulty.get().lower()]

        # Randomly determine the number of elements to remove based on difficulty
        remove_elements = random.randint(difficulty[0], difficulty[1])

        # Set the difficulty category in the Sudoku solver
        solver.difficulty_category = difficulty

        # Destroy the current window after selecting size and difficulty
        self.start_widget.destroy()

        # Assuming Sudoku_GUI is defined elsewhere and takes size and difficulty parameters
        app = Sudoku_GUI(size, remove_elements)  # Start the Sudoku game with selected size and difficulty

if __name__ == "__main__":
    app = Start_SudokuGUI()
