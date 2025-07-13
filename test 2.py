import tkinter as tk
from tkinter import messagebox
import random
import time

class SudokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Game")
        self.root.geometry("600x650")

        # Generate and display the initial puzzle
        self.initial_grid = self.generate_sudoku()
        self.create_grid()

    def generate_sudoku(self):
        """Generate a solved Sudoku grid and remove numbers for a puzzle."""
        grid = [[0] * 9 for _ in range(9)]
        self.fill_grid(grid)
        
        # Remove numbers to create a puzzle
        squares = 81
        empties = squares * 3 // 4
        for _ in range(empties):
            row, col = random.randint(0, 8), random.randint(0, 8)
            while grid[row][col] == 0:
                row, col = random.randint(0, 8), random.randint(0, 8)
            grid[row][col] = 0
        return grid

    def fill_grid(self, grid):
        """Fill the grid following Sudoku rules to create a valid solution."""
        def can_place(row, col, num):
            # Check if `num` can be placed without breaking constraints
            for x in range(9):
                if grid[row][x] == num or grid[x][col] == num:
                    return False
            start_row, start_col = 3 * (row // 3), 3 * (col // 3)
            for i in range(3):
                for j in range(3):
                    if grid[start_row + i][start_col + j] == num:
                        return False
            return True

        def solve():
            # Solve the grid using backtracking
            for i in range(9):
                for j in range(9):
                    if grid[i][j] == 0:
                        for num in range(1, 10):
                            if can_place(i, j, num):
                                grid[i][j] = num
                                if solve():
                                    return True
                                grid[i][j] = 0
                        return False
            return True

        solve()

    def create_grid(self):
        """Create the Sudoku grid on the GUI."""
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.entries = [[None for _ in range(9)] for _ in range(9)]
        colors = ['#FFCCCB', '#CCFFCC', '#CCCCFF']

        for box_row in range(3):
            for box_col in range(3):
                frame = tk.Frame(main_frame, bd=2, relief='solid', bg='black')
                frame.grid(row=box_row, column=box_col, padx=5, pady=5, sticky='nsew')

                for r in range(3):
                    for c in range(3):
                        grid_row = box_row * 3 + r
                        grid_col = box_col * 3 + c
                        cell_value = self.initial_grid[grid_row][grid_col]
                        color = colors[(box_row + box_col) % len(colors)]

                        entry = tk.Entry(frame, width=5, font=('Arial', 18), justify='center', bg=color, bd=1)
                        entry.grid(row=r, column=c, sticky='nsew')

                        if cell_value != 0:
                            entry.insert(0, cell_value)
                            entry.config(state='readonly', bg='lightgray')
                        else:
                            self.entries[grid_row][grid_col] = entry

                for i in range(3):
                    frame.grid_rowconfigure(i, weight=1)
                    frame.grid_columnconfigure(i, weight=1)

        for i in range(3):
            main_frame.grid_rowconfigure(i, weight=1)
            main_frame.grid_columnconfigure(i, weight=1)

        # Solve and Reset Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        solve_button = tk.Button(button_frame, text="Solve Puzzle", command=self.start_solving, bg='#2196F3', fg='white', font=('Arial', 14))
        solve_button.grid(row=0, column=0, padx=10)
        
        reset_button = tk.Button(button_frame, text="Reset Puzzle", command=self.reset_puzzle, bg='#FF5722', fg='white', font=('Arial', 14))
        reset_button.grid(row=0, column=1, padx=10)

    def reset_puzzle(self):
        """Reset the puzzle to a new initial state."""
        self.initial_grid = self.generate_sudoku()
        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                if entry:
                    entry.config(state='normal', bg='white')
                    entry.delete(0, tk.END)
                    value = self.initial_grid[i][j]
                    if value != 0:
                        entry.insert(0, value)
                        entry.config(state='readonly', bg='lightgray')

    def start_solving(self):
        """Start the solving process with MRV heuristic and forward-checking visualization."""
        grid = [[int(entry.get()) if entry and entry.get().isdigit() else 0 for entry in row] for row in self.entries]
        if self.mrv_forward_check(grid):
            messagebox.showinfo("Sudoku Solved", "The puzzle has been solved successfully!")
            self.root.after(1000, self.close_game)  # Close the game after 1 second
        else:
            messagebox.showerror("Unsolvable", "This puzzle has no solution.")

    def mrv_forward_check(self, grid):
        """Solve the Sudoku grid using MRV heuristic and forward checking with visual updates."""
        def select_unassigned_variable():
            # Choose cell with minimum remaining values (MRV)
            options = [(len(possibilities[i][j]), i, j) for i in range(9) for j in range(9) if grid[i][j] == 0]
            return min(options)[1:] if options else (-1, -1)

        def forward_check(row, col, num):
            # Temporarily place num and reduce possibilities in the same row, column, and 3x3 subgrid
            temp_possibilities = [row[:] for row in possibilities]
            for x in range(9):
                possibilities[row][x].discard(num)
                possibilities[x][col].discard(num)
            start_row, start_col = 3 * (row // 3), 3 * (col // 3)
            for i in range(3):
                for j in range(3):
                    possibilities[start_row + i][start_col + j].discard(num)
            return temp_possibilities

        def backtrack():
            # Solve using backtracking with MRV and forward-checking
            row, col = select_unassigned_variable()
            if row == -1: return True  # Puzzle solved

            for num in sorted(possibilities[row][col]):
                temp_possibilities = forward_check(row, col, num)
                grid[row][col] = num
                self.update_cell(row, col, num)  # Update GUI cell
                if backtrack():
                    return True
                grid[row][col] = 0
                self.update_cell(row, col, '')  # Clear cell if backtracking
                possibilities[:] = temp_possibilities  # Restore possibilities

            return False

        # Initialize possibilities for each cell
        possibilities = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                if grid[i][j] != 0:
                    possibilities[i][j] = {grid[i][j]}
                    forward_check(i, j, grid[i][j])

        return backtrack()

    def update_cell(self, row, col, value):
        """Update the value of a cell in the GUI and add delay for visualization."""
        entry = self.entries[row][col]
        if entry:
            entry.delete(0, tk.END)
            entry.insert(0, value)
            entry.update()
            time.sleep(0.1)  # Longer delay for clearer visualization

    def close_game(self):
        """Close the game window."""
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x650")
    game = SudokuGame(root)
    root.mainloop()
