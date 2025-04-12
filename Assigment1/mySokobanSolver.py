"""

    Sokoban assignment


The functions and classes defined in this module will be called by a marker script.
You should complete the functions and classes according to their specified interfaces.

No partial marks will be awarded for functions that do not meet the specifications
of the interfaces.

You are NOT allowed to change the defined interfaces.
In other words, you must fully adhere to the specifications of the
functions, their arguments and returned values.
Changing the interfacce of a function will likely result in a fail
for the test of your code. This is not negotiable!

You have to make sure that your code works with the files provided
(search.py and sokoban.py) as your code will be tested
with the original copies of these files.

Last modified by 2021-08-17  by f.maire@qut.edu.au
- clarifiy some comments, rename some functions
  (and hopefully didn't introduce any bug!)

"""

# You have to make sure that your code works with 
# the files provided (search.py and sokoban.py) as your code will be tested 
# with these files
import search 
import sokoban
import re

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def my_team():
    """
    Return the list of the team members of this assignment submission as a list
    of triplet of the form (student_number, first_name, last_name)
    """
    return [ (11032553, 'Hunter', 'Wilde'), (12026395, 'Oliver', 'Kele') ]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def read_and_clean_warehouse(file_path: str) -> list[list[str]]:
    """
    Reads a warehouse text file and converts it into a cleaned 2D list.
    - Removes player ('@') and boxes ('$'), replacing them with spaces (' ').
    - Replaces boxes on goal cells ('*') and players on goal cells ('!') with '.'.
    @param file_path (str):
        The relative file path of the warehouse file.
    @return:
        list[list[str]]: A cleaned 2D warehouse grid.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        # Read lines, clean thsem, and filter out empty lines
        return [
            [re.sub(r'[@$]', ' ', re.sub(r'[!*]', '.', char)) for char in line.rstrip()]
            for line in file.readlines()[1:] if line.strip()  # Skip empty lines
        ]

def find_corners(warehouse2D: list[list[str]]) -> (list[list[str]], tuple):
    """
    Finds corners and replaces them with 'X' if not a target square or '.' if a target square.
    @param warehouse2D (list[list[str]]):
        A 2D array representing the warehouse.
    @return:
       warehouse_corners_marked (list[list[str]]): A 2D array representing the warehouse with corners marked by an 'X' (if not target square) or '.' if target square.
    """
    corner_positions = []

    for row_index, row in enumerate(warehouse2D[1:len(warehouse2D) - 1], start=1):
        first_hash = row.index('#')
        last_hash = len(row) - 1 - row[::-1].index('#')

        for index in range(first_hash + 1, last_hash):
            char = row[index]
            if char == '#' or char == '.': continue
            up_hash = 1 if warehouse2D[row_index + 1][index] == '#' else 0
            down_hash = 1 if warehouse2D[row_index - 1][index] == '#' else 0
            left_hash = 1 if row[index - 1] == '#' else 0
            right_hash = 1 if row[index + 1] == '#' else 0
            if (up_hash + down_hash + left_hash + right_hash) >= 2:
                warehouse2D[row_index][index] = 'X'
                corner_positions.append((row_index, index))

    return warehouse2D, corner_positions

def find_walls(warehouse_details: tuple[list[list[str]], list[tuple]]) -> list[list[str]]:
    """
    Finds taboo cells along walls & between corners, and then marks them with 'X'.
    :param warehouse_details: A tuple containing a 2D array and a tuple of x and y coords for corner positions.
    :return: warehouse2D (list[list[str]]): A 2D array representing the warehouse with taboo cells marked by an 'X'.
    """
    warehouse2D, corner_positions = warehouse_details

    for corner in corner_positions:
        row_idx, col_idx = corner  # Assuming corner is (row, col)

        # Process horizontally (to the right)
        for i in range(col_idx + 1, len(warehouse2D[row_idx])):
            cell = warehouse2D[row_idx][i]
            if cell == ' ':
                continue
            if cell == '#':
                break
            if cell == 'X':
                # Found another corner in the same row
                next_corner_col = i

                # Check for walls above
                above_wall = True
                for j in range(col_idx + 1, next_corner_col):
                    if row_idx > 0:
                        above_cell = warehouse2D[row_idx - 1][j]
                        if above_cell != '#':
                            above_wall = False
                            break

                # Check for walls below
                below_wall = True
                for j in range(col_idx + 1, next_corner_col):
                    if row_idx < len(warehouse2D) - 1:
                        below_cell = warehouse2D[row_idx + 1][j]
                        if below_cell != '#':
                            below_wall = False
                            break

                # Mark taboo cells if along a wall
                if above_wall or below_wall:
                    for j in range(col_idx + 1, next_corner_col):
                        if warehouse2D[row_idx][j] == ' ':
                            warehouse2D[row_idx][j] = 'X'
                break

        # Process vertically (downward) - existing code
        for n in range(row_idx + 1, len(warehouse2D)):
            if n >= len(warehouse2D) or col_idx >= len(warehouse2D[n]):
                break

            cell = warehouse2D[n][col_idx]
            if cell == ' ':
                continue
            if cell == '#' or cell == '.':
                break
            if cell == 'X':
                # Found next corner in same column
                next_corner_row = n

                # Check for walls to the left
                left_wall = True
                for m in range(row_idx + 1, next_corner_row):
                    if col_idx > 0:
                        left_cell = warehouse2D[m][col_idx - 1]
                        if left_cell != '#':
                            left_wall = False
                            break

                # Check for walls to the right
                right_wall = True
                for m in range(row_idx + 1, next_corner_row):
                    if col_idx < len(warehouse2D[m]) - 1:
                        right_cell = warehouse2D[m][col_idx + 1]
                        if right_cell != '#':
                            right_wall = False
                            break

                # Mark taboo cells if along a wall
                if left_wall or right_wall:
                    for m in range(row_idx + 1, next_corner_row):
                        if warehouse2D[m][col_idx] == ' ':
                            warehouse2D[m][col_idx] = 'X'
                break

    return warehouse2D

def Array2String(warehouse2D):
    result = "\n".join(" ".join(map(str, row)) for row in warehouse2D)
    return result

def taboo_cells(warehouse):
    """
    Identify the taboo cells of a warehouse. A "taboo cell" is by definition
    a cell inside a warehouse such that whenever a box get pushed on such
    a cell then the puzzle becomes unsolvable.

    Cells outside the warehouse are not taboo. It is a fail to tag one as taboo.

    When determining the taboo cells, you must ignore all the existing boxes,
    only consider the walls and the target  cells.
    Use only the following rules to determine the taboo cells;
     Rule 1: if a cell is a corner and not a target, then it is a taboo cell.
     Rule 2: all the cells between two corners along a wall are taboo if none of
             these cells is a target.

    :param warehouse: a Warehouse object with a worker inside the warehouse.
    :return: A string representing the warehouse with only
        wall cells marked with '#' & taboo cells marked with a 'X'.
        The returned string should NOT have marks for the worker,
        the targets, and the boxes.
    """
    clean_warehouse = read_and_clean_warehouse(warehouse)
    marked_corners = find_corners(clean_warehouse)
    marked_walls = find_walls(marked_corners)
    return Array2String(marked_walls)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class SokobanPuzzle(search.Problem):
    """
    An instance of the class 'SokobanPuzzle' represents a Sokoban puzzle.
    An instance contains information about the walls, the targets, the boxes
    and the worker.

    Your implementation should be fully compatible with the search functions of
    the provided module 'search.py'.
    """
    def __init__(self, warehouse):
        """
        Writes the lines of the warehouse file into the `rows` array;
        searches each row for the initial state (i.e. the player's position '@')
        & the goal state (i.e. the target square's position '.'),
        the indices of which are then stored in the `initial` and `goal` variables.
        :param warehouse: text file mapping the warehouse layout.
        """
        file = open(warehouse, 'r')
        rows = file.readlines()
        for row in rows:
            if '@' in row:
                self.initial = (row.index('@'), rows.index(row)) # tuple[int x,int y]
            if '.' in row:
                self.goal = (row.index('.'), rows.index(row)) # tuple[int x,int y]
        self.tabooCells = taboo_cells(warehouse)

    def actions(self, state):
        """
        :param state: a given state in the form tuple[int, int].
        :return: a list of actions which can be performed in the given state.
            :type: string[]
        """
        up, down, left, right = ((state[0], state[1] + 1), (state[0], state[1] - 1),
                                 (state[0] - 1, state[1]), (state[0] + 1, state[1]))
        actions = []

        if self.tabooCells[up] == " ":
            actions.append('Up')
        if self.tabooCells[down] == " ":
            actions.append('Down')
        if self.tabooCells[left] == " ":
            actions.append('Left')
        if self.tabooCells[right] == " ":
            actions.append('Right')

        return actions

    def result(self, state, action):
        """
        Applies the given action to the given state and returns the resulting state.
        :param state: a given state.
            :type: tuple[int, int]
        :param action: action to be applied.
            E.g. 'Left', 'Down', 'Right', 'Up'.
        :return: state resulting from applying the action to the given state.
        """
        if action in self.actions(state):
            if action == 'Up':
                return (state[0], state[1] + 1)
            elif action == 'Down':
                return (state[0], state[1] - 1)
            elif action == 'Left':
                return (state[0] - 1, state[1])
            elif action == 'Right':
                return (state[0] + 1, state[1])
        else:
            return state

    def path_cost(self, c, state1, action, state2):
        """
        Calculate the cost of a path from state 1 to state 2 via the given action,
        assuming cost c.
        :param c:
        :param state1:
        :param action:
        :param state2:
        :return:
        """

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_elem_action_seq(warehouse, action_seq):
    """
    Determine if the sequence of actions listed in 'action_seq' is legal or not.

    Important notes:
      - a legal sequence of actions does not necessarily solve the puzzle.
      - an action is legal even if it pushes a box onto a taboo cell.

    :param warehouse: a valid Warehouse object

    :param action_seq: a sequence of legal actions.
           For example, ['Left', 'Down', Down','Right', 'Up', 'Down']

    :return:
        The string 'Impossible', if one of the action was not valid.
           For example, if the agent tries to push two boxes at the same time,
                        or push a box into a wall.
        Otherwise, if all actions were successful, return
               A string representing the state of the puzzle after applying
               the sequence of actions.  This must be the same string as the
               string returned by the method  Warehouse.__str__()
    """
    
    ##         "INSERT YOUR CODE HERE"
    
    raise NotImplementedError()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_weighted_sokoban(warehouse):
    """
    This function analyses the given warehouse.
    It returns the two items. The first item is an action sequence solution.
    The second item is the total cost of this action sequence.

    :param warehouse: a valid Warehouse object

    :return:
        If puzzle cannot be solved
            return 'Impossible', None
        If a solution was found,
            return S, C
            where S is a list of actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
            C is the total cost of the action sequence C
    """
    
    raise NotImplementedError()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
