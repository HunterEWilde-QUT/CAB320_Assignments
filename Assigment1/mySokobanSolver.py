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

def intialise_warehouse(file_path):
    """
    Loads a warehouse.txt file and creating a Warehouse object.
    FOR TESTING PURPOSES ONLY!
    :param file_path:
    :return:
    """
    wh = sokoban.Warehouse()
    wh.load_warehouse(file_path)

    return wh

def process_lines(warehouse_string):
    """
    Turn a string into lines.
    Replace all @ and $ with " " (i.e. replace boxes and players with blanks).
    Replaces boxes on goal cells ('*') and players on goal cells ('!') with '.'
        (i.e. ignore boxes and players, just mark goal cells).
    :param warehouse_string:
    :return:
    """
    lines = warehouse_string.splitlines()
    processed_lines = []

    for line in lines:
        # Scan across characters in the line and apply the regex replacements
        processed_line = re.sub(r'[@$]', ' ', re.sub(r'[!*]', '.', line))
        processed_lines.append(processed_line)

    return processed_lines

def find_corners(warehouse):
    """
    Finds corners and replaces them with 'X' if not a target square or '.' if a target square.
    :param warehouse: A 2D array representing the warehouse.
    :return: warehouse_corners_marked: A 2D array representing the warehouse with corners marked by an 'X' (if not target square) or '.' if target square.
    """
    wh_string = warehouse.__str__()
    lines = process_lines(wh_string)

    # Find all empty cells inside the warehouse
    wall_pos = warehouse.walls  # list of tuples [(x,y)...]

    # Record blank cells (inside the warehouse)
    blank_pos = []  # a list of tuples

    # Iterate over each line (a string) in lines (a list of strings)
    # For each line, iterate over each character in the string
    for y, line in enumerate(lines[1:(len(lines) - 1)], 1):  # don't look for corners in first or last line
        last_hash = len(line) - 1 - line[::-1].index('#')
        found_first_hash = False

        for x, char in enumerate(line[:last_hash]):
            if not found_first_hash:
                if char == " ": continue
                if char == "#": found_first_hash = True
            else:
                # Ignore target cells as they can not be taboo, and method for finding their positions
                if char == " ": blank_pos.append((x, y))

    # Find corners by comparing blank_pos to wall_pos
    corners = []

    # Directions to check for adjacent positions (left, right, up, down)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # (dx, dy) for left, right, up, down

    # Iterate over blank positions and check if they are corners
    for x, y in blank_pos:
        # Check if both vertical and horizontal directions have walls
        has_wall_x = (x - 1, y) in wall_pos or (x + 1, y) in wall_pos  # left or right
        has_wall_y = (x, y - 1) in wall_pos or (x, y + 1) in wall_pos  # up or down

        if has_wall_x and has_wall_y:
            corners.append((x, y))

    return corners

def find_corner_pairs(warehouse, corners: list[tuple[int,int]]) -> list[tuple[chr,tuple[int,int],tuple[int,int]]]:
    """
    Find series of cells between two corners with no target cells.
    :param warehouse:
    :param corners: list of corner coords.
    :return:
    """
    corner_pairs = []  # [('V'/'H', C1, C2),...] where C1 and C2 are (x,y) tuples
    targets_set = set(warehouse.targets)
    walls_set = set(warehouse.walls)
    target_or_wall_set = targets_set.union(walls_set)

    # for each corner
    for i in range(len(corners)):
        # unpack the corner's coordinates
        x1, y1 = corners[i]
        # look through the other corners
        for j in range(i + 1, len(corners)):
            # unpack the next corner's coordinates
            x2, y2 = corners[j]
            # record series of cells that could be taboo & whether to look horizontally or vertically
            if y1 == y2:
                # Horizontal scan
                x_start, x_end = sorted([x1, x2])
                has_target_or_wall = any((x, y1) in target_or_wall_set for x in range(x_start + 1, x_end))
                if not has_target_or_wall:
                    corner_pairs.append(('H', (x1, y1), (x2, y2)))

            elif x1 == x2:
                # Vertical scan
                y_start, y_end = sorted([y1, y2])
                has_target_or_wall = any((x1, y) in target_or_wall_set for y in range(y_start + 1, y_end))
                if not has_target_or_wall:
                    corner_pairs.append(('V', (x1, y1), (x2, y2)))

    return corner_pairs

def check_walls(warehouse, corners: list[tuple[int,int]]) -> list[tuple[int,int]]:
    """
    Check for taboo cells along a wall, based on corner_pairs.
    :param warehouse: warehouse text file.
    :param corners: list of corner coords.
    :return:
    """
    corner_pairs = find_corner_pairs(warehouse, corners)

    along_wall = []  # list to store taboo cells (tuple[x,y]) along a wall between two corners with no target cells on the wall
    walls = warehouse.walls

    for corner_pair in corner_pairs:
        # Unpack corner pair and direction
        direction, (x1, y1), (x2, y2) = corner_pair

        if direction == 'H':
            for x in range(x1 + 1, x2):
                # Check for walls above and below
                above = (x, y1 - 1) in walls
                below = (x, y1 + 1) in walls
                if above or below:
                    along_wall.append((x, y1))
        elif direction == 'V':
            y_start, y_end = sorted([y1, y2])
            for y in range(y_start + 1, y_end):
                # Check for walls to the left and right
                left = (x1 - 1, y) in walls
                right = (x1 + 1, y) in walls
                if left or right:
                    along_wall.append((x1, y))

    return along_wall

def find_taboo_cells(warehouse) -> list[tuple[int,int]]:
    """
    Find the (x,y) coordinates of every taboo cell in the warehouse.
    :param warehouse: warehouse text file.
    :return: a list of tuples (x,y) containing the coordinates of all taboo cells.
    """
    taboo_cells_coords = []

    corners = find_corners(warehouse)
    taboo_cells_coords.extend(corners)

    between_corners = check_walls(warehouse, corners)
    taboo_cells_coords.extend(between_corners)

    return taboo_cells_coords

def taboo_cells(warehouse) -> str:
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
    taboo_cells_coords = find_taboo_cells(warehouse)

    warehouse_string = warehouse.__str__()

    # Returns a list of lines with only " ", ".", and "#" (empty cell, target cell, and walls)
    warehouse_lines = process_lines(warehouse_string)

    # Replace target cells with blanks and insert "X" to mark taboo cells
    new_lines = []

    for y, line in enumerate(warehouse_lines):
        new_line = ''
        for x, char in enumerate(line):
            if (x, y) in taboo_cells_coords:
                new_line += 'X'
            elif char == '.': # Replace target cells with blanks
                new_line += ' '
            else:
                new_line += char
        new_lines.append(new_line)

    return "\n".join(new_lines)

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
        self.initial = (int, int)
        self.goal = (int, int)
        self.tabooCells = find_taboo_cells(warehouse)

        file = open(warehouse, 'r')
        rows = file.readlines()
        for row in rows:
            if '@' in row:
                self.initial = (row.index('@'), rows.index(row)) # tuple[int x,int y]
            if '.' in row:
                self.goal = (row.index('.'), rows.index(row)) # tuple[int x,int y]

    def actions(self, state: tuple[int,int]) -> list[str]:
        """
        :param state: a given state.
        :return: a list of actions which can be performed in the given state.
        """
        up, down, left, right = ((state[0], state[1] + 1), (state[0], state[1] - 1),
                                 (state[0] - 1, state[1]), (state[0] + 1, state[1]))
        actions = []

        if up not in self.tabooCells:
            actions.append('Up')
        if down not in self.tabooCells:
            actions.append('Down')
        if left not in self.tabooCells:
            actions.append('Left')
        if right not in self.tabooCells:
            actions.append('Right')

        return actions

    def result(self, state: tuple[int,int], action: str) -> tuple[int,int]:
        """
        Applies the given action to the given state and returns the resulting state.
        :param state: a given state.
        :param action: action to be applied.
            E.g. 'Left', 'Down', 'Right', 'Up'.
        :return: state resulting from applying the action to the given state.
        """
        if action in self.actions(state):
            if action == 'Up':
                return state[0], state[1] + 1
            elif action == 'Down':
                return state[0], state[1] - 1
            elif action == 'Left':
                return state[0] - 1, state[1]
            elif action == 'Right':
                return state[0] + 1, state[1]
        else:
            return state

    def path_cost(self, c, state1: tuple[int,int], action: str, state2: tuple[int,int]):
        """
        Calculate the cost of a path from state 1 to state 2 via the given action, assuming cost c.
        :param c: cost to move to state 1.
        :param state1: current state.
        :param action: action of moving from state 1 to state 2.
        :param state2: state resulting from applying the action.
        :return: total cost of path to state 2.
        """
        # Default cost for moving is 1
        move_cost = 1

        # Unpack the states
        worker_pos1, box_positions1 = state1
        worker_pos2, box_positions2 = state2

        # If the box positions are different, we pushed a box
        if box_positions1 != box_positions2:
            # Find which box was moved
            for i, (box1, box2) in enumerate(zip(box_positions1, box_positions2)):
                if box1 != box2:
                    # This box was moved, add its weight to the cost
                    move_cost += self.warehouse.weights[i]
                    break

        return c + move_cost

    def goal_test(self, state):
        """
        Return True if the state is a goal state.
        A state is a goal state if all boxes are on target positions.
        :param state: current state (worker_position, box_positions).
        :return: True if the state is a goal state, False otherwise.
        """
        # Unpack the state
        _, box_positions = state

        # Check if all boxes are on target positions
        # We need to ensure that every box is on a target
        return all(box in self.warehouse.targets for box in box_positions)

    def value(self, state):
        """
        Compute the value of the given state.
        Used for optimization problems.
        :param state: current state.
        :return: value of the given state.
        """
        # Unpack the state
        _, box_positions = state

        # For Sokoban, we can use the negative of the Manhattan distance
        # from boxes to their nearest targets as a value function
        total_distance = 0
        for box in box_positions:
            # Find the minimum Manhattan distance to any target
            min_distance = float('inf')
            for target in self.warehouse.targets:
                distance = abs(box[0] - target[0]) + abs(box[1] - target[1])
                min_distance = min(min_distance, distance)
            total_distance += min_distance

        return -total_distance  # Negative because we want to maximize value

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_elem_action_seq(warehouse, action_seq):
    """
    Determine if the sequence of actions listed in 'action_seq' is legal or not.

    Important notes:
      - a legal sequence of actions does not necessarily solve the puzzle.
      - an action is legal even if it pushes a box onto a taboo cell.

    :param warehouse: a valid Warehouse object
    :param action_seq: a sequence of legal actions.
        E.g. ['Left', 'Down', Down','Right', 'Up', 'Down']
    :return: The string 'Impossible', if one of the action was not valid.
        E.g. if the agent tries to push two boxes at the same time, or push a box into a wall.
        Otherwise, if all actions were successful,
        return a string representing the state of the puzzle after applying the sequence of actions.
        This must be the same string as the string returned by the method `Warehouse.__str__()`.
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
    # Create a SokobanPuzzle instance
    problem = SokobanPuzzle(warehouse)

    # Check if the puzzle is already in a goal state
    if problem.goal_test(problem.initial):
        return [], 0

    # Define a heuristic function for A* search
    def h(node):
        # Manhattan distance from each box to its nearest target
        total_distance = 0
        # Unpack the state
        _, box_positions = node.state

        # Find the minimum weight of the boxes
        min_weight = min(problem.warehouse.weights) if problem.warehouse.weights else 1

        # Calculate the Manhattan distance from each box to its nearest target
        for box in box_positions:
            # Find the minimum Manhattan distance to any target
            min_distance = float('inf')
            for target in problem.warehouse.targets:
                distance = abs(box[0] - target[0]) + abs(box[1] - target[1])
                min_distance = min(min_distance, distance)
            # Multiply by the minimum weight to ensure the heuristic is admissible
            total_distance += min_distance * min_weight

        return total_distance

    # Use A* search to find a solution
    solution_node = search.astar_graph_search(problem, h)

    # If no solution was found, return 'Impossible'
    if solution_node is None:
        return 'Impossible', None

    # Extract the action sequence from the solution node
    action_sequence = solution_node.solution()

    # Calculate the total cost of the action sequence
    total_cost = solution_node.path_cost

    return action_sequence, total_cost

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
