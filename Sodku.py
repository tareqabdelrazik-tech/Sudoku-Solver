import numpy as np
import multiprocessing
import random
from tkinter import filedialog, messagebox, Menu
import numpy as np
import customtkinter
from functools import partial
import re
import time




class SudokuSolver:
    def __init__(self):
        """
        Constructor for the SudokuSolver class.
        Initializes attributes related to Sudoku solving.
        """
        self.related_cells = {}  # Dictionary to store related cells for each cell in the Sudoku grid
        self.dim = 0  # Dimension of the Sudoku grid (number of rows or columns)
        self.grid_dim = 0  # Size of

        # sub-grids in the Sudoku grid
        self.domains = {}  # Dictionary to store possible values (domains) for each cell in the Sudoku grid
        self.length_values = {}  # Dictionary to store the count of remaining possible values for each cell

        self.solutions = None

    def grid_insert(self, sudoku, dim):
        """
        Initializes and inserts a Sudoku grid, assigns initial values, calculates relationships,
        and reduces the Sudoku grid using defined methods.

        Args:
            sudoku (list of lists): The initial Sudoku puzzle.
            dim (int): The dimension of the Sudoku grid (e.g., 9 for a 9x9 grid).
        """
        # Initialize the Sudoku grid and related parameters
        self.initialize_grid(sudoku, dim)

        # Assign initial values to cells based on the provided Sudoku puzzle
        self.assign_values()

        # Calculate relationships (related cells) for each cell in the Sudoku grid
        self.calculate_related_cells()

        # Perform reduction operations on the Sudoku grid (assuming `sudoku_reduction` is defined elsewhere)
        self.sudoku_reduction()

    def initialize_grid(self, sudoku, dimension):
        """
        Initializes the Sudoku grid and related parameters.

        Args:
            sudoku (list of lists): The initial Sudoku puzzle.
            dimension (int): The dimension of the Sudoku grid (e.g., 9 for a 9x9 grid).
        """

        self.dim = dimension  # Set the dimension of the grid
        self.grid_dim = int(np.sqrt(dimension))  # Calculate the size of the sub-grids
        self.sudoku = np.array(sudoku)  # Convert the Sudoku puzzle to a NumPy array

    def assign_values(self):
        """
        Initializes the domains for each cell in the Sudoku board.
        Each cell's domain is initially set to all possible values (1 to dim),
        except for cells that already have an assigned value.
        """

        # Initialize the domains dictionary with all possible values for each cell
        self.domains = {(row, col): set(range(1, self.dim + 1)) for row in range(self.dim) for col in range(self.dim)}

        # Iterate through each cell in the Sudoku board
        for row in range(self.dim):
            for col in range(self.dim):
                if self.sudoku[row, col] != 0:  # If the cell has a preassigned value
                    value = self.sudoku[row, col]
                    self.domains[(row, col)] = {value}  # Set the domain of the cell to the preassigned value

    def valid_sudoku(self, board):
        """
        Checks if a given Sudoku board is valid. A board is valid if no row, column, or sub-grid has duplicate values.

        Args:
            board (list of lists): The Sudoku board to check, where 0 represents an empty cell.

        Returns:
            bool: True if the board is valid, False otherwise.
        """

        def has_duplicates(group):
            """
            Helper funzction to check if a group (row, column, or sub-grid) has duplicates.

            Args:
                group (list): A list of integers representing a group of Sudoku cells.

            Returns:
                bool: True if there are no duplicates, False otherwise.
            """
            seen = set()
            for num in group:
                if num != 0:  # Ignore empty cells
                    if num in seen:
                        return False  # Duplicate found
                    seen.add(num)
            return True  # No duplicates found

        # Check rows and columns
        for i in range(self.dim):
            if not has_duplicates(board[i]):  # Check row
                return False
            if not has_duplicates([board[j][i] for j in range(self.dim)]):  # Check column
                return False

        # Calculate sub-grid size
        subgrid_size = int(self.dim ** 0.5)

        # Check sub-grids
        for row_start in range(0, self.dim, subgrid_size):
            for col_start in range(0, self.dim, subgrid_size):
                subgrid = [board[row][col] for row in range(row_start, row_start + subgrid_size)
                           for col in range(col_start, col_start + subgrid_size)]
                if not has_duplicates(subgrid):
                    return False

        return True

    def calculate_related_cells(self):
        """
        Calculates and stores all cells related to each cell in the Sudoku grid.
        Related cells are those in the same row, column, or subgrid.
        """

        # Iterate through each cell in the grid
        for row in range(self.dim):
            for col in range(self.dim):
                cell_coords = (row, col)  # Get the coordinates of the current cell
                # Store the set of related cells for the current cell
                self.related_cells[cell_coords] = self.get_related_cells(cell_coords)

    def get_related_cells(self, cell_coords):
        """
        Finds all cells related to the given cell in terms of Sudoku rules, i.e.,
        cells in the same row, column, or subgrid.

        Args:
            cell_coords (tuple): Coordinates of the cell (row, column).

        Returns:
            set: A set of coordinates of all related cells.
        """

        related_cells = set()  # Initialize an empty set to store related cells

        # Add all cells in the same row and column
        for i in range(self.dim):
            related_cells.add((i, cell_coords[1]))  # Add cells in the same column
            related_cells.add((cell_coords[0], i))  # Add cells in the same row

        # Calculate the starting coordinates of the subgrid
        subgrid_row_start = (cell_coords[0] // self.grid_dim) * self.grid_dim
        subgrid_col_start = (cell_coords[1] // self.grid_dim) * self.grid_dim

        # Add all cells in the same subgrid
        for row in range(subgrid_row_start, subgrid_row_start + self.grid_dim):
            for col in range(subgrid_col_start, subgrid_col_start + self.grid_dim):
                related_cells.add((row, col))

        # Remove the original cell from the set of related cells
        related_cells.remove(cell_coords)

        return related_cells  # Return the set of related cells

    def remove(self, domains, remaining_values, variable, value):
        """
        Removes a value from the domain of a variable and updates the remaining values.

        Args:
            domains (dict): Dictionary mapping variables to their possible values (domains).
            remaining_values (dict): Dictionary mapping variables to the count of their remaining possible values.
            variable (str): The variable from which the value is to be removed.
            value (any): The value to be removed from the variable's domain.
        """

        # Remove the specified value from the domain of the given variable
        domains[variable].remove(value)

        # If the variable's domain still has more than one value, update the remaining values count
        if len(domains[variable]) > 1:
            remaining_values[variable] = len(domains[variable])
            return

        # If the variable has only one remaining value, remove it from the remaining values dictionary
        if variable in remaining_values:
            del remaining_values[variable]

    def is_valid(self, domains, row, col, value):
        """
        Checks if assigning a value to a cell does not violate Sudoku constraints.

        Args:
            domains (dict): Dictionary mapping cells to their possible values (domains).
            row (int): The row index of the cell.
            col (int): The column index of the cell.
            value (any): The value to be assigned to the cell.

        Returns:
            bool: True if assigning the value is valid, False otherwise.
        """

        related_cells = self.related_cells[(row, col)]  # Get cells in the same row, column, and subgrid
        for cell in related_cells:  # Iterate through related cells
            related_row, related_col = cell[0], cell[1]  # Unpack the related cell's row and column

            if len(domains[(related_row, related_col)]) == 1:  # Check if the related cell is assigned a single value
                if list(domains[(related_row, related_col)])[0] == value:  # Check if the assigned value is the same
                    return False  # If a related cell already has the value, return False

        return True  # No related cell has the same value, return True



    def enter_element_machine(self, domains, remaining_values, row, col, value):
        """
        Attempts to assign a value to a cell in the Sudoku grid using a machine-driven approach.

        Args:
            domains (dict): Dictionary mapping cells to their possible values (domains).
            remaining_values (dict): Dictionary mapping cells to the count of their remaining possible values.
            row (int): The row index of the cell.
            col (int): The column index of the cell.
            value (any): The value to be assigned to the cell.

        Returns:
            bool: True if the value was successfully assigned and related cells updated, False otherwise.
        """

        # Check if the value can be assigned to the cell based on its current domain
        if value in domains[(row,col)]:
            domains[(row, col)] = {value}  # Assign the value to the cell's domain

            # Remove the cell from the remaining values dictionary, as it is now assigned a single value
            if (row, col) in remaining_values:
                del remaining_values[(row, col)]

            # Reduce the domains of related cells
            return self.reduction_related_cells(domains, remaining_values, (row, col), value,
                                                self.related_cells[(row, col)])

        return False  # Return False if the value cannot be assigned to the cell

    def reduction_related_cells(self, domains, remaining_values, key, value, relation):
        """
        Reduces the domain values of related cells in the Sudoku grid after assigning a value to a cell.

        Args:
            domains (dict): Dictionary mapping cells to their possible values (domains).
            remaining_values (dict): Dictionary mapping cells to the count of their remaining possible values.
            key (tuple): Coordinates (row, col) of the cell where a value was assigned.
            value (any): The value that was assigned to the cell.
            relation (set): Set of coordinates of cells related to the cell at 'key'.

        Returns:
            bool: True if reduction is successful for all related cells, False if a contradiction is found.
        """

        for index in relation:
            if value in domains[index]:  # Check if the assigned value is in the domain of the related cell
                self.remove(domains, remaining_values, index, value)  # Remove the value from the related cell's domain

                # Check if reducing the domain to a single value for the related cell is valid
                if len(domains[index]) == 1:
                    single_value = next(iter(domains[index]))  # Get the single value in the domain
                    if self.is_valid(domains, index[0], index[1], single_value):
                        # Recursively reduce the related cell's domain and its related cells
                        if not self.reduction_related_cells(domains, remaining_values, index, single_value,
                                                            self.related_cells[index]):
                            return False
                    else:
                        return False  # Return False if the Sudoku is no longer valid
                elif len(domains[index]) == 0:
                    return False

        return True  # Return True if reduction is successful for all related cells

    def sudoku_reduction(self):
        """
        Reduces domain values in the Sudoku grid based on cells with singleton domains.
        For each cell with a single value domain, reduce the domains of related cells that can no longer have that value.
        """
        for row in range(self.dim):
            for col in range(self.dim):
                if len(self.domains[(row, col)]) == 1:  # Check if the domain of the cell is a singleton set
                    value = next(iter(self.domains[(row, col)]))  # Get the single value in the cell's domain
                    for index in self.related_cells[(row, col)]:  # Iterate through related cells
                        if value in self.domains[index] and len(self.domains[index]) > 1:
                            # Remove the value from the domain of related cells that can have multiple values
                            self.remove(self.domains, self.length_values, index, value)

    def get_unfinished_cell(self, domains, remaining_values):
        """
        Finds the cell with the fewest remaining possible values to continue solving the Sudoku.

        Args:
            domains (dict): Dictionary mapping cells to their possible values (domains).
            remaining_values (dict): Dictionary mapping cells to the count of their remaining possible values.

        Returns:
            tuple or None: The cell (as a tuple of coordinates) with the fewest remaining values and its domain,
                           or None if all cells are finished.
        """

        # Check if there are any cells with remaining values to assign
        if len(remaining_values) == 0:
            return None

        # Find the cell with the minimum number of remaining values
        cell_with_fewest_values = min(remaining_values, key=remaining_values.get)

        # Get the possible values for that cell
        possible_values = domains[cell_with_fewest_values]

        # Return the cell and its possible values
        return cell_with_fewest_values, possible_values

    def remove_element(self, domains, length_values, row, col, value):
        """
        Remove a value from a cell in the Sudoku grid if it exists.

        Args:
            domains (dict): Dictionary mapping cells to their possible values (domains).
            length_values (dict): Dictionary mapping cells to the count of their remaining possible values.
            row (int): Row index of the cell.
            col (int): Column index of the cell.
            value (any): The value to be removed from the cell.

        Returns:
            None
        """
        if (row, col) in domains and value in domains[(row, col)]:
            self.remove(domains, length_values, (row, col), value)




    def unique_solution(self):
        values = np.array(list(self.length_values.values()))
        elements = np.array(list(self.length_values.keys()))

        # Find the minimum value and its indices
        min_value = np.min(values)
        min_indices = np.where(values == min_value)[0]
        min_elements = elements[min_indices]

        self.solutions = []

        for index in min_elements:
            row, col = index

            for value in self.domains[(row, col)]:
                # Backup the current state of domains and length_values
                domains_backup = {k: v.copy() for k, v in self.domains.items()}
                length_values_backup = {k: v for k, v in self.length_values.items()}

                self.enter_element_machine(self.domains, self.length_values, row, col, value)

                exist_solution = self.Solver()
                if not self.solutions:
                    if self.solved_sudoku[0]:
                        self.solutions.append(self.solved_sudoku[0])



                self.domains = {k: v.copy() for k, v in domains_backup.items()}
                self.length_values = {k: v for k, v in length_values_backup.items()}
                self.remove_element(self.domains , self.length_values , row , col , value)

        return True  # Unique solution found



    def Solver(self):
        """
        Solves a Sudoku puzzle using parallel backtracking.

        Returns:
            bool or dict: A solved Sudoku grid (dict) if a solution is found, False otherwise.
        """
        # Check if the current Sudoku grid is a valid initial state
        if not self.valid_sudoku(self.create_sudoku_matrix(self.domains)):
            return False

        self.sudoku_reduction()

        # Initialize list to store solved Sudoku grids

        self.solved_sudoku = []

        # Perform parallel backtracking to solve the Sudoku puzzle
        return self.parallel_backtrack(self.domains, self.length_values)

    def Non_Parallel_Solver(self):
        cell = self.get_unfinished_cell(self.domains , self.length_values)
        if cell is None :
            return self.domains

        ( row , col ) , possible_values = cell[0] , cell[1]

        domains_backup = {k: v.copy() for k, v in self.domains.items()}
        length_values_backup = {k: v for k, v in self.length_values.items()}


        for value in possible_values:
            if self.enter_element_machine(self.domains, self.length_values, row, col, value):
                result = self.Non_Parallel_Solver()
                if result:
                    return result  # Return the solved domains

            self.domains = {k: v.copy() for k, v in domains_backup.items()}
            self.length_values = {k: v for k, v in length_values_backup.items()}


        return False

    def enter_in_parallel(self, row, col, value, domains, length_values):
        """
        Attempt to enter a value into a Sudoku grid using parallel processing.

        Args:
            row (int): Row index of the cell.
            col (int): Column index of the cell.
            value (any): The value to be entered into the cell.
            domains (dict): Dictionary mapping cells to their possible values (domains).
            length_values (dict): Dictionary mapping cells to the count of their remaining possible values.

        Returns:
            dict or None: A solved Sudoku grid (domains) if a solution is found, None otherwise.
        """
        if self.enter_element_machine(domains, length_values, row, col, value):
            return self.try_value(domains, length_values)

        return None

    def parallel_backtrack(self, domains, length_values):
        """
        Perform parallel backtracking to solve a Sudoku puzzle or similar constraint satisfaction problem.

        Args:
            domains (dict): Dictionary mapping cells to their possible values (domains).
            length_values (dict): Dictionary mapping cells to the count of their remaining possible values.

        Returns:
            dict or False: A solved Sudoku grid (domains) if a solution is found, False otherwise.
        """
        cell = self.get_unfinished_cell(domains, length_values)

        if cell is None:
            return domains  # Return the solved Sudoku grid if all cells are assigned

        (row, col), possible_values = cell[0], cell[1]
        results = []

        self.num_cores = multiprocessing.cpu_count()

        pool = multiprocessing.Pool(self.num_cores)

        for value in possible_values:
            result = pool.apply_async(self.enter_in_parallel,
                                          args=(row, col, value, domains.copy(), length_values.copy()))
            results.append(result)

        return self.process_results(results ,pool)
    def process_results(self, results, pool ,solutions = None,max_solutions=1):
        """
        Process results obtained from parallel processing tasks until a desired number of solutions is found.

        Args:
            results (list): List of multiprocessing results or tasks.
            max_solutions (int): Maximum number of solutions to collect before stopping.

        Returns:
            bool: True if the desired number of solutions is found, False otherwise.
        """
        while results:
            any_ready = False

            for result in results:  # Iterate over a copy of the results list

                if result.ready():  # Check if the task is complete
                    any_ready = True
                    output = result.get()  # Get the result with a timeout


                    if output is not None :
                        self.solved_sudoku.append(output)

                    results.remove(result)  # Remove the processed result from the list

                    if len(self.solved_sudoku) >= max_solutions:
                        pool.close()
                        return True  # Exit once we have the desired number of solutions
            if self.dim == 16:
                if not any_ready:
                    time.sleep(0.05)  # Wait to prevent deadlock or excessive CPU usage
            elif self.dim == 9:
                if not any_ready:
                    time.sleep(0.01)
        pool.close()
        return False


    def try_value(self, domains, length_values):
        """
        Tries possible values for unfinished cells in a Sudoku grid using backtracking.

        Args:
            domains (dict): Dictionary mapping cells to their possible values (domains).
            length_values (dict): Dictionary mapping cells to the count of their remaining possible values.

        Returns:
            dict or False: A solved Sudoku grid (domains) if a solution is found, False otherwise.
        """
        # Get an unfinished cell with its possible values
        cell = self.get_unfinished_cell(domains, length_values)

        if cell is None:
            return domains  # Return the solved Sudoku grid if all cells are assigned

        (row, col), possible_values = cell[0], cell[1]

        # Backup the current state of domains and length_values
        domains_backup = {k: v.copy() for k, v in domains.items()}
        length_values_backup = {k: v for k, v in length_values.items()}

        for value in possible_values:
            # Try assigning the value to the cell using the enter_element_machine method
            if self.enter_element_machine(domains, length_values, row, col, value):
                result = self.try_value(domains, length_values)  # Recursively try to solve the Sudoku

                if result:
                    return result  # Return the solved Sudoku grid if a solution is found

            # Restore the state before trying a new value
            domains = {k: v.copy() for k, v in domains_backup.items()}
            length_values = {k: v for k, v in length_values_backup.items()}

            # Undo the value assignment
            self.remove_element(domains, length_values, row, col, value)

        return False  # Return False if no valid solution is found



    def create_sudoku_matrix(self, domains):
        """
        Create a 2D NumPy array representation of the Sudoku grid based on domains.

        Args:
            domains (dict): Dictionary mapping cells to their possible values (domains).

        Returns:
            numpy.ndarray: 2D NumPy array representation of the Sudoku grid.
        """
        # Determine the dimensions of the Sudoku grid based on the maximum row and column in domains
        max_row = max(row for row, col in domains)
        max_col = max(col for row, col in domains)

        # Initialize a 2D NumPy array to store the Sudoku grid
        sudoku_matrix = np.zeros((max_row + 1, max_col + 1), dtype=int)

        # Fill the Sudoku matrix based on the values in domains
        for row in range(max_row + 1):
            for col in range(max_col + 1):
                cell_values = domains.get((row, col), set())
                if len(cell_values) == 1:
                    # If only one value is possible for the cell, assign it to the matrix
                    cell_value = next(iter(cell_values))
                    sudoku_matrix[row, col] = cell_value
                else:
                    # Otherwise, leave the cell as 0 (indicating an empty cell in the Sudoku)
                    sudoku_matrix[row, col] = 0

        return sudoku_matrix



    def create_sudoku(self):
        # Initialize the matrix with zeros
        self.matrix = np.zeros((self.dim, self.dim)).astype(int)

        # Generate a random sequence for the first row
        numbers = np.arange(1, self.dim + 1)
        first_row = np.random.choice(numbers, size=len(numbers), replace=False)

        # Generate a random sequence for the first column, shifted by one
        first_col_shifted = np.random.choice(numbers - 1, size=len(numbers), replace=False)

        # Place the first row values into the matrix using the shifted indices
        self.matrix[(first_row - 1).astype(int), first_col_shifted] = first_row
        # Solve the Sudoku to fill the matrix

        self.grid_insert(self.matrix,self.dim)

        self.Solver()

        self.matrix = np.array(self.create_sudoku_matrix(self.solved_sudoku.pop(0)))

        # Determine the number of elements to remove based on the difficulty level
        difficulty_level = int(self.difficulty)
        num_elements_to_remove = int(self.matrix.size * difficulty_level / 100)

        # Select random indices to remove elements from the matrix
        random_indices = np.random.choice(self.matrix.size, size=num_elements_to_remove, replace=False)

        row_indices, col_indices = np.unravel_index(random_indices, self.matrix.shape)

        # Remove elements to create the puzzle
        self.matrix[row_indices, col_indices] = 0
        return self.matrix
    
if __name__ == "__main__":

    solver = SudokuSolver()
    solver.dim = 16
    solver.difficulty = 50
    Sudoku_grid = list()
    Start_time = time.time()
    for i in  range(100):
        matrix = solver.create_sudoku()
        solver.grid_insert(matrix,  16)

        sudoku_matrix = solver.Solver()


    End_time = time.time()

    print(End_time - Start_time)
