import tkinter as tk
import random


class Maze(object):
    """Maze generated via randomized DFS algorithm

    Attributes:
        board: 2D list of ints representing the maze

        end: tuple for position of end square

        path: list of tuples representing the solution from the start
        square to end square. Each tuple contains a tuple for the
        position and a int for the direction.

    """

    # Constants for the different types of board squares
    WALL = 0
    SPACE = 1
    START = 2
    STOP = 3

    # Default starting position
    START_CELL = (0, 0)

    # Constants for the different directions in the path
    NO_DIR = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4

    @staticmethod
    def generate_board(rows, cols):
        """Given the size for the maze, including space needed for walls,
        return the board, the 2D list of backpointers, and ending
        position

        """

        max_length = 0
        stack = [Maze.START_CELL]
        visited = set()

        board = [[Maze.WALL for c in xrange(cols)]
                 for r in xrange(rows)]

        # array to keep track of backpointers
        back = [[None for _ in xrange(cols)]
                for _ in xrange(rows)]

        # randomized dfs algorithm that generates the maze
        while (stack):
            cell = stack[-1]
            r = cell[0]
            c = cell[1]
            visited.add(cell)

            board[r][c] = Maze.SPACE

            # set ending square to the square furthest from the start
            if len(stack) > max_length:
                max_length = len(stack)
                end = (r, c)

            children = [
                (r+2, c), (r-2, c),
                (r, c+2), (r, c-2)]
            children = filter(
                lambda (r, c): r >= 0 and r < rows
                and c >= 0 and c < cols and (r, c) not in visited,
                children)

            if children:
                child = random.choice(children)
                c_r = child[0]
                c_c = child[1]

                # remove wall between cells
                w_r = (r + c_r)/2
                w_c = (c + c_c)/2
                board[w_r][w_c] = Maze.SPACE

                stack.append(child)
                back[child[0]][child[1]] = (r, c)
            else:
                stack.pop()

        return (board, back, end)

    @staticmethod
    def get_dir(start, end):
        """Compare the positions of two consecutive squares on the path and
        return the direction between them.

        """

        if end[0] > start[0]:
            return Maze.DOWN

        if end[0] < start[0]:
            return Maze.UP

        if end[1] > start[1]:
            return Maze.RIGHT

        if end[1] < start[1]:
            return Maze.LEFT

    @staticmethod
    def get_path(back, end):
        """Given the 2D list of backpointers and the position of the ending
        square, return the path from start to end.

        """

        path = []
        cell = end
        while cell:
            prev = cell
            if not (cell == Maze.START_CELL or cell == end):
                path.append((cell, Maze.NO_DIR))
            cell = back[cell[0]][cell[1]]
            if cell:
                between_cell = ((prev[0] + cell[0])/2,
                                (prev[1] + cell[1])/2)
                path.append((between_cell, Maze.get_dir(cell, prev)))

        return path

    def __init__(self, rows, cols):
        """Create a maze with some number of rows and columns. These values
        include the space needed for walls between cells.

        """

        board, back, end = self.generate_board(rows, cols)
        self.board = board
        self.board[self.START_CELL[0]][self.START_CELL[1]] = self.START
        self.board[end[0]][end[1]] = self.STOP

        self.path = self.get_path(back, end)


class MazeUI(tk.Canvas):
    """Tkinter Canvas that displays a Maze object.

    """

    # values in pixels
    MAX_WIDTH = 600
    MAX_HEIGHT = 600
    MIN_SIZE = 3

    # these row and column values don't include space for walls
    MAX_ROWS = (MAX_HEIGHT/MIN_SIZE + 1)/2
    MAX_COLS = (MAX_WIDTH/MIN_SIZE + 1)/2

    MIN_ROWS = 2
    MIN_COLS = 1

    # Define colors for different types of board squares
    GET_COLOR = ("black", "white", "green", "red")

    PATH_COLOR = "blue"
    ARROW_COLOR = "black"

    def __init__(self, master, rows, cols):
        """Create MazeUI with a certain number of rows and columns, not
        including space for walls between cells.

        """

        self.rows = max((min((rows, self.MAX_ROWS)), self.MIN_ROWS))
        self.cols = max((min((cols, self.MAX_COLS)), self.MIN_COLS))

        # need space for wall between two cells
        rows_actual = 2*self.rows - 1
        cols_actual = 2*self.cols - 1
        self.maze = Maze(rows_actual, cols_actual)

        self.size = min((
            self.MAX_HEIGHT/rows_actual, self.MAX_WIDTH/cols_actual))

        tk.Canvas.__init__(
            self, master, height=rows_actual*self.size,
            width=cols_actual*self.size,
            background="black")

        board = self.maze.board
        for r in xrange(len(board)):
            for c in xrange(len(board[0])):
                self.paint_cell(r, c, self.GET_COLOR[board[r][c]])

    def paint_cell(self, row, col, color):
        """Paint the square at row and col a certain color.

        """

        y = self.size*row
        x = self.size*col
        self.create_rectangle(x, y, x+self.size, y+self.size,
                              fill=color,
                              outline=color)

    def paint_arrow(self, row, col, direction, color):
        """Draw a triangle of a certain color and direction over the square at
        position row and col.

        """

        y_u = self.size*row
        y_d = y_u + self.size
        x_l = self.size*col
        x_r = x_l + self.size

        if direction == Maze.LEFT:
            points = ((x_r, y_u), (x_r, y_d), (x_l, (y_u + y_d)/2))
        elif direction == Maze.DOWN:
            points = ((x_l, y_u), (x_r, y_u), ((x_r + x_l)/2, y_d))
        elif direction == Maze.RIGHT:
            points = ((x_l, y_u), (x_l, y_d), (x_r, (y_u + y_d)/2))
        elif direction == Maze.UP:
            points = ((x_l, y_d), (x_r, y_d), ((x_r + x_l)/2, y_u))
        else:
            return

        self.create_polygon(points, outline=color,
                            fill=color)

    def solve_maze(self):
        """Draw the solution for the maze.

        """

        for cell in self.maze.path:
            direction = cell[1]
            cell = cell[0]
            self.paint_cell(cell[0], cell[1], self.PATH_COLOR)
            self.paint_arrow(cell[0], cell[1], direction, self.ARROW_COLOR)


class App(tk.Frame):
    """Tkinter Frame containing all UI

    Attributes:
        maze_ui: Tkinter Canvas showing the maze
        rows: Tkinter Spinbox that sets the number of rows
        cols: Tkinter Spinbox that sets the number of columns

    """

    # Default size of the maze
    DEFAULT_ROWS = 20
    DEFAULT_COLS = 20

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.maze_ui = None

        spinbox_frame = tk.Frame(self)
        tk.Label(spinbox_frame, text="Rows: ").grid(
            row=0)
        self.rows = tk.Spinbox(
            spinbox_frame, from_=MazeUI.MIN_ROWS, to=MazeUI.MAX_ROWS)
        self.rows.grid(column=1, row=0)

        tk.Label(spinbox_frame, text="Columns: ").grid(
            row=1)
        self.cols = tk.Spinbox(
            spinbox_frame, from_=MazeUI.MIN_COLS, to=MazeUI.MAX_COLS)
        self.cols.grid(column=1, row=1)
        spinbox_frame.grid(row=1)

        self.set_spinbox(self.rows, self.DEFAULT_ROWS)
        self.set_spinbox(self.cols, self.DEFAULT_COLS)

        self.regenerate_maze()

        tk.Button(self, text="Regenerate", command=self.regenerate_maze).grid(
            row=2)
        tk.Button(self, text="Solve", command=self.solve_maze).grid(
            row=3)

    @staticmethod
    def set_spinbox(spinbox, val):
        """Convenience function to set spinbox value

        """

        spinbox.delete(0, "end")
        spinbox.insert(0, val)

    def solve_maze(self):
        """Show maze solution

        """

        self.maze_ui.solve_maze()

    def regenerate_maze(self):
        """Create a new maze with the number of rows and columns indicated by
        spinboxes.

        """

        if self.maze_ui:
            self.maze_ui.destroy()

        r_str = self.rows.get()
        c_str = self.cols.get()

        # if spinboxes don't contain a valid integer, use the default values
        try:
            rows = int(r_str)
        except:
            rows = self.DEFAULT_ROWS

        try:
            cols = int(c_str)
        except:
            cols = self.DEFAULT_COLS

        self.maze_ui = MazeUI(self, rows, cols)
        self.maze_ui.grid(row=0)

        self.set_spinbox(self.rows, self.maze_ui.rows)
        self.set_spinbox(self.cols, self.maze_ui.cols)


def main():
    root = tk.Tk()
    root.title("Maze")
    App(root).grid()
    root.mainloop()

if __name__ == "__main__":
    main()
