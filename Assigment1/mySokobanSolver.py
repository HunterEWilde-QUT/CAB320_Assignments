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
    Target cells are NEVER taboo cells, regardless of position.
    :param warehouse: warehouse text file.
    :return: a list of tuples (x,y) containing the coordinates of all taboo cells.
    """
    taboo_cells_coords = []

    # Get target positions as a set for efficient lookups
    target_positions = set(warehouse.targets)
    
    # Find potential taboo cells
    corners = find_corners(warehouse)
    between_corners = check_walls(warehouse, corners)
    
    # Combine all potential taboo cells
    potential_taboo = corners + between_corners
    
    # Exclude target cells from taboo cells
    taboo_cells_coords = [cell for cell in potential_taboo if cell not in target_positions]

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

deltas = {
    'Left': (-1, 0),
    'Right': (1, 0),
    'Up': (0, -1), # Y decreases going up
    'Down': (0, 1)  # Y increases going down
}

def move_pos(pos: tuple[int,int], direction: str) -> tuple[int,int]:
    """
    Updates the position of a given object to move in one of four directions
    using the global deltas dictionary.
    :param pos: a given position (x,y).
    :param direction: a given direction ('Left', 'Right', 'Up', 'Down').
    :return: the new position (x,y) after moving in the given direction.
             Returns the original position if the direction is invalid.
    """
    x, y = pos
    if direction in deltas:
        dx, dy = deltas[direction]
        return x + dx, y + dy
    else:
        # Return original position if direction is not in deltas
        return pos 

def move_warehouse(current_warehouse, action):
    """
    Updates a warehouse resulting from a given movement by the worker.
    Checks if the worker has moved onto a box. If so, the box is pushed.
    Assumes the action is valid (checked by SokobanPuzzle.actions).
    Uses the move_pos function which relies on the global deltas.
    :param current_warehouse: a given Warehouse object.
    :param action: a movement performed by the worker.
    """
    worker_pos = current_warehouse.worker
    # Make a mutable copy of the boxes list
    box_positions = list(current_warehouse.boxes) 

    # Calculate the new worker position based on action using move_pos
    new_worker_pos = move_pos(worker_pos, action)

    # Create a reference to the mutable list copy
    new_box_positions = box_positions 

    # Check if there's a box at the new worker position
    for i, box_pos in enumerate(box_positions):
        if new_worker_pos == box_pos:
            # Calculate the new position for the pushed box using move_pos
            new_box_pos = move_pos(box_pos, action)
            # Update the position of the pushed box in the list
            new_box_positions[i] = new_box_pos 
            break # Assume only one box can be pushed at a time

    # Assemble & return the new warehouse using the updated positions
    resulting_warehouse = current_warehouse.copy(worker=new_worker_pos, boxes=new_box_positions) 
    return resulting_warehouse

def add_weights_to_string(warehouse_obj, warehouse_string):
    """
    Add the weights to the warehouse string in the correct order.
    The boxes in the warehouse are ordered by y-coordinate first, then x-coordinate.
    """
    # Get the boxes in the NEW warehouse
    boxes = warehouse_obj.boxes
    
    # Create a mapping from current box positions to weights
    weights = warehouse_obj.weights
    box_weight_map = dict(zip(warehouse_obj.boxes, warehouse_obj.weights))
    
    # Sort boxes in reading order (y, x)
    sorted_boxes = sorted(boxes, key=lambda pos: (pos[1], pos[0]))
    
    # Get weights in the correct order based on the sorted boxes
    reordered_weights = [box_weight_map[box] for box in sorted_boxes]
    
    # Convert weights list to a space-separated string
    weights_str = " ".join(str(w) for w in reordered_weights)

    # Return the weights string followed by the warehouse string
    return weights_str + "\n" + warehouse_string

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
        Reads a warehouse text file and creates a SokobanPuzzle instance,
        which captures the initial state of the warehouse
        & other information about the warehouse stored as a Warehouse object
        (e.g. worker position, boxes' positions, weights, wall positions).
        :param warehouse: text file mapping the warehouse layout.
        """
        # Store the initial state as a string
        warehouse_string = warehouse.__str__()
        # Store the initial state as a string with weights information added at the front
        warehouse_string = warehouse.__str__()
        # Convert weights list to a space-separated string
        weights_str = " ".join(str(w) for w in warehouse.weights)
        # Intial state looks like a txt document -> states are unpacked using the from_lines method
        self.initial = weights_str + "\n" + warehouse_string
        # Keep a reference to the original warehouse object for properties like walls, targets, weights
        self.warehouse_obj = warehouse 
        # Ensure tabooCells and walls are stored efficiently (as sets)
        self.tabooCells = set(find_taboo_cells(warehouse))  
        self.walls = set(warehouse.walls) # Store walls as a set for faster lookups
    
    def actions(self, state: str) -> list[str]:
        """
        Gives the list of valid moves a worker can perform from a given state,
        using the global deltas dictionary and checking taboo cells.
        :param state: a given version of the warehouse.
        :return: a list of actions which can be performed in the given state.
        """
        # Unpack the worker's position from the current state
        current_warehouse = sokoban.Warehouse()
        current_warehouse.from_lines(state.splitlines())
        worker_x, worker_y = current_warehouse.worker

        # Use object fields for efficiency
        walls_set = self.walls
        taboo_cells_set = self.tabooCells
        box_positions = set(current_warehouse.boxes)

        possible_actions = ['Up', 'Down', 'Left', 'Right']
        valid_actions = []

        for action in possible_actions:
            # Calculate next positions using the global deltas dictionary
            dx, dy = deltas[action]
            next_worker_pos = (worker_x + dx, worker_y + dy)

            # Case 1: Move to an empty cell (not a wall, not a box)
            if next_worker_pos not in walls_set and next_worker_pos not in box_positions:
                valid_actions.append(action)
                continue

            # Case 2: Move into a box, pushing it
            if next_worker_pos in box_positions:
                # Calculate where the box would end up using global deltas
                next_box_pos = (next_worker_pos[0] + dx, next_worker_pos[1] + dy)
                
                # Check if the box's destination is valid:
                # Neither a taboo cell nor another box.
                # (Assuming taboo cells are never targets; adjust if needed)
                if next_box_pos not in taboo_cells_set and \
                   next_box_pos not in box_positions:
                    valid_actions.append(action)
        
        return valid_actions

    def result(self, state: str, action: str) -> str:
        """
        Applies the given action to the given state and returns the resulting state.
        :param state: a given state of the warehouse.
        :param action: a movement performed by the worker.
            E.g. 'Left', 'Down', 'Right', 'Up'.
        :return: a new state resulting from applying the action to the given state.
        """
        # If the action is not valid, return the current state
        if action not in self.actions(state):
            return state
        else:
            warehouse = sokoban.Warehouse()
            warehouse.from_lines(state.splitlines())
            new_warehouse = move_warehouse(warehouse, action) 
            new_warehouse_string = new_warehouse.__str__()
            result_state = add_weights_to_string(new_warehouse, new_warehouse_string)
            return result_state

    def path_cost(self, c, state1: str, action: str, state2: str):
        """
        Calculate the cost of a path from state 1 to state 2 via the given action, assuming cost c.
        :param c: cost to move to state 1.
        :param state1: current state, representing the current position of the worker & boxes.
        :param action: action of moving from state 1 to state 2.
        :param state2: state resulting from applying the action.
        :return: total cost of path to state 2.
        """
        # Default cost for moving is 1

        move_cost = 1

        # Unpack the states
        current_warehouse = sokoban.Warehouse()
        current_warehouse.from_lines(state1.splitlines())
        new_warehouse = sokoban.Warehouse()
        new_warehouse.from_lines(state2.splitlines())

        # worker_pos1, box_positions1 = current_warehouse.worker, current_warehouse.boxes # Not needed?
        box_positions1 = current_warehouse.boxes
        # worker_pos2, box_positions2 = new_warehouse.worker, new_warehouse.boxes # Not needed?
        box_positions2 = new_warehouse.boxes

        # If the box positions are different, we pushed a box
        if box_positions1 != box_positions2:
            # Find which box was moved
            for i, (box1, box2) in enumerate(zip(box_positions1, box_positions2)):
                if box1 != box2:
                    # This box was moved, add its weight to the cost
                    # Use the weights from the original warehouse object
                    move_cost += current_warehouse.weights[i] 
                    break

        return c + move_cost

    def value(self, state: str):
        """
        Compute the value of the given state.
        Used for optimization problems.
        :param state: current state.
        :return: value of the given state.
        """
        # Unpack the state
        current_warehouse = sokoban.Warehouse()
        current_warehouse.from_lines(state.splitlines())
        box_positions = current_warehouse.boxes

        # For Sokoban, we can use the negative of the Manhattan distance
        # from boxes to their nearest targets as a value function
        total_distance = 0
        for box in box_positions:
            # Find the minimum Manhattan distance to any target
            min_distance = float('inf')
            # Use targets from the original warehouse object
            for target in self.warehouse_obj.targets: 
                distance = abs(box[0] - target[0]) + abs(box[1] - target[1])
                min_distance = min(min_distance, distance)
            total_distance += min_distance

        return -total_distance  # Negative because we want to maximize value

    def goal_test(self, state):
        """
        Check if the current state is a goal state.
        A goal state is defined as a state where all boxes are on target cells.
        :param state: current state of the warehouse (string representation).
        :return: True if the state is a goal state, False otherwise.
        """
        # Unpack the state
        current_warehouse = sokoban.Warehouse()
        current_warehouse.from_lines(state.splitlines())
        box_positions = current_warehouse.boxes

        # Check if all boxes are on target cells
        # Use targets from the original warehouse object
        target_set = set(self.warehouse_obj.targets) 
        for box in box_positions:
            if box not in target_set:
                return False

        return True

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Problem domains addressed by AI have *hard* and *soft* constraints
# Identify the hard constraints in this problem's definition

# Defining check functions, returns True if action legal, False if action illegal

# Direction deltas: (dx, dy)

def is_legal_action(warehouse_init, new_worker_pos: tuple[int,int], new_boxes_pos: list[tuple[int,int]]):
    """
    Check if an action is legal:
        1. The worker cannot move into a wall.
        2. A box cannot be pushed into a wall.
        3. A box cannot be pushed into another box.
    Does not check for taboo cells.
    :param warehouse_init: the initial warehouse state to be checked against.
    :param new_worker_pos: the destination of the worker.
    :param new_boxes_pos: the destinations of all the boxes.
    """
    # Check if the worker's destination is a wall
    if new_worker_pos in warehouse_init.walls:
        return False
    
    # Check if the worker's destination has a box
    if new_worker_pos in warehouse_init.boxes:
        # Find the box being pushed
        new_box_pos = None
        for box in new_boxes_pos:
            if box != warehouse_init.boxes:
                new_box_pos = box

                break

        # Check if the box's destination is valid (no walls or other boxes)
        if new_box_pos in warehouse_init.walls or new_box_pos in warehouse_init.boxes:
            return False

        # Box can be pushed, action is legal
        return True
    else:
        # Player is moving to an empty space, action is legal
        return True

def check_elem_action_seq(warehouse, action_seq) -> str:
    """
    Validate and execute a sequence of actions.
    :param warehouse: a Warehouse object.
    :param action_seq: a list of actions.
    :return: a string representation of the updated warehouse.
    """
    current_warehouse = warehouse
    
    for action in action_seq:
        # Calculate new positions
        next_warehouse = move_warehouse(current_warehouse, action)
        worker_pos, boxes_pos = next_warehouse.worker, next_warehouse.boxes
        
        # Check if action is legal
        if not is_legal_action(current_warehouse, worker_pos, boxes_pos):
            return "Impossible"
            
        # Update warehouse
        current_warehouse = next_warehouse
    
    return current_warehouse.__str__()

# TESTING
def run_tests(path):
    warehouse = intialise_warehouse(path)
    print(warehouse.__str__())
    
    # Testing legal actions
    print(f"Legal action 'R': {is_legal_action(warehouse, 'Right')}")
    print(f"Legal action 'U': {is_legal_action(warehouse, 'Up')}")
    
    # Testing action sequence
    print(check_elem_action_seq(warehouse, ["Down","Right","Left"]))

# Uncomment to run tests
#run_tests("./warehouses/warehouse_6n.txt")



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
        # Simple admissible heuristic: Sum of Manhattan distances from each box to its nearest target.
        # This ignores weights, ensuring admissibility as weights >= 0.
        total_distance = 0
        # Unpack the state
        current_warehouse = sokoban.Warehouse()
        current_warehouse.from_lines(node.state.splitlines()) 
        box_positions = current_warehouse.boxes
        targets = problem.warehouse_obj.targets # Use targets from the problem instance

        if not targets: # Handle case with no targets
             return 0
        
        # Calculate the sum of minimum Manhattan distances for each box to any target
        for box in box_positions:
            min_distance_for_box = float('inf')
            for target in targets: 
                distance = abs(box[0] - target[0]) + abs(box[1] - target[1])
                min_distance_for_box = min(min_distance_for_box, distance)
            
            # If a box cannot reach any target (e.g., targets list is empty, though checked above), 
            # handle appropriately. Here we add 0 if min_distance remains inf.
            if min_distance_for_box != float('inf'):
                 total_distance += min_distance_for_box

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

wh = intialise_warehouse("./Assigment1/warehouses/warehouse_008a.txt")
# print(check_elem_action_seq(wh, ['Left', 'Left', 'Up', 'Up', 'Left', 'Down', 'Right', 'Right', 'Right', 'Right', 'Up', 'Right', 'Down', 'Left', 'Down', 'Right', 'Right', 'Right', 'Left', 'Left', 'Left', 'Left', 'Left', 'Left', 'Left']))

ware = sokoban.Warehouse()
ware.from_lines(['1 99', '   ######    ', '###      ### ', '#  $ $      #', '# .   @    .#', '############ '])
print(ware.__str__())
