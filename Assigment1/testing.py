import os
import glob
import sanity_check as sc
import sokoban
# importing functions individually for sanity_check
from mySokobanSolver import taboo_cells, solve_weighted_sokoban, check_elem_action_seq 
import io
from contextlib import redirect_stdout
import re

""" 
    File for testing solve_weighted_sokoban and finding areas to optimise.

    Testing procedure is as follows:
    
    1. Run sanity_check.py and abort if it fails - i.e. check changes haven't broken anything.
    2. Batch test warehouses in groups of ~50 (about 25% of warehouses).
    3. For each warehouse, classify intial state with tags, test solve_weighted_sokoban,
       and abort if it takes more than one minute.
    4. Record results in a txt file for the batch and ask in the command line if the user wants to continue.
    5. If the user wants to continue, repeat for the next batch of warehouses.

    Optimisation approach:
    1. Then optimise, make changes to sole_weighted_sokoban and test again.
    2. Compare results with the previous batch of warehouses.

"""

## ADD OPTION TO TEST IN BATCHES OR ALL WAREHOUSES

def create_report(start_warehouse, end_warehouse):
    """ Create a report file for the batch of warehouses. Returns path to report."""
    # Create a testing directory if it doesn't exist
    testing_dir = os.path.join(os.getcwd(), 'testing')
    if not os.path.exists(testing_dir):
        os.makedirs(testing_dir)

    next_test_num = 1

    # Find the next test number
    test_files = glob.glob(os.path.join(testing_dir, 'Test*.txt'))
    if test_files:
        # Extract test numbers from filenames and find the maximum
        test_nums = [int(os.path.basename(f).replace('Test', '').replace('.txt', '')) 
                    for f in test_files]
        next_test_num = max(test_nums) + 1 if test_nums else 1

    # Create the new test file
    test_file_path = os.path.join(testing_dir, f'Test{next_test_num}.txt')
    with open(test_file_path, 'w') as f:
        f.write(f"Test{next_test_num}: {start_warehouse}, {end_warehouse}\n\n")

    return test_file_path 

def edit_report(path, line, header=False):
    """ Edit the report file with the given line. """
    if header:
        with open(path, 'a') as f:
            f.write(line + '\n\n')
    else:
        with open(path, 'a') as f:
            f.write('\t' + line + '\n\n')

# create_report(1, 50) - Tested create_report function and it works as expected.
# edit_report('testing/Test1.txt', 'Test line 1')  - Tested edit_report function and it works as expected.

def ask_to_continue():
    """ Asks the user if they want to continue after a failure. """
    while True:
        choice = input("A sanity check failed. Do you want to continue anyway? (Y/N): ").strip().upper()
        if choice == 'Y':
            print("Continuing despite failed sanity check...")
            return True
        elif choice == 'N':
            print("Aborting due to failed sanity check.")
            return False
        else:
            print("Invalid input. Please enter Y or N.")

def test_sanity():
    """ Run the sanity check and abort if it fails. """
    all_passed = True

    try:
        # Test taboo cells
        f = io.StringIO()
        with redirect_stdout(f):
            sc.test_taboo_cells()
        output = f.getvalue()
        if "passed" not in output.lower():
            print(f"Sanity check for taboo cells failed. Output:\n{output}")
            all_passed = False

        # Test action sequence
        f = io.StringIO()
        with redirect_stdout(f):
            sc.test_check_elem_action_seq()
        output = f.getvalue()
        if "passed" not in output.lower():
            print(f"Sanity check for action sequence failed. Output:\n{output}")
            all_passed = False

        # Test weighted sokoban solver
        f = io.StringIO()
        with redirect_stdout(f):
            sc.test_solve_weighted_sokoban()
        output = f.getvalue()
        # Check for the whole word "expected"
        if " expected " not in output.lower().split():
            print(f"Sanity check for weighted sokoban failed. Output:\n{output}")
            all_passed = False

        if all_passed:
            print("\nAll sanity checks passed!")
        else:
            ask_to_continue()

    except Exception as e:
        print(f"Sanity check failed with an exception: {e}")
        exit(1)

# test_sanity() Fails for now as solve_weghted_sokoban is not implemented yet. Will retest after implementation.

def test_warehouse():

    raise NotImplementedError()

def classify_warehouse(wh, report_path):

    """ Creates tags for optimisation and identifying problematic warehouses.
        Params:
            wh: Warehouse object to classify.
        Returns:
            none: writes tags to report file.
    """

    box_count = len(wh.boxes)
    wall_count = len(wh.walls)
    total_cells = wh.nrows * wh.ncols
    density_score = wall_count / total_cells
    taboo_count = len(re.findall(r'X', taboo_cells(wh)))
    weights = wh.weights if wh.weights else "No Weights"

    tag_line = f"Boxes: {box_count}, Walls: {wall_count}, Density: {density_score:.2f}, Taboo Count: {taboo_count}, Weights: {weights}"

    edit_report(report_path, tag_line)

    return


def load_warehouse(file_path, report_path):
    """ Load a warehouse from a file. Write warehouse name to report file. """
    wh = sokoban.Warehouse()
    wh.load_warehouse(file_path)
    edit_report(report_path, f"Loaded warehouse: {file_path}", header=True)
    return wh

# wh = load_warehouse("./warehouses/warehouse_01.txt", "testing/Test1.txt")
# classify_warehouse(wh, "testing/Test1.txt")

# testing load_warehouse and classify_warehouse: both work as expected.

def test_warehouse(file_path, report_path):
    """ Test a warehouse by loading it and classifying it. """
    wh = load_warehouse(file_path, report_path)
    classify_warehouse(wh, report_path)

    # Test the solver

    solution = "solved"     # Placeholder: expects solved, not solved, or impossible.
    time = 30               # Placeholder: time taken to solve the warehouse.
    cost = 100              # Placeholder: cost of the solution.

    edit_report(report_path, f"Result: Solved? = {solution}, Time: {time:.2f} seconds, Cost: {cost}")

    # Write time to solve and cost to the report file, then create a new line to seperate.

    return

def test_batch(start_warehouse, num_warehouses):
    """ Test a batch of warehouses. """
    # Create a report file for the batch
    report_path = create_report(f"Started with warehouse: {start_warehouse}", f"Number of warehouses tested: {num_warehouses}")

    # Get the list of warehouse files 
    wh_files = sorted(os.listdir("./Assigment1/warehouses"))  # Get the list of files in the warehouses directory
    start_index = wh_files.index(start_warehouse)

    # Select the batch of warehouses to test
    batch_files = wh_files[start_index:start_index + num_warehouses]

    for file_path in batch_files:
        full_file_path = os.path.join("./Assigment1/warehouses", file_path) # Construct full path
        test_warehouse(full_file_path, report_path)

    return print(f"Batch test completed. Report saved to {report_path}.")


test_batch("warehouse_001.txt", 20) # Seems to work as expected, should retest after updating mySokobanSolver.py fro github.

# WRITE A FUNCTION TO COMBINE TESTING AND CONTROL THROUGH COMMAND LINE.