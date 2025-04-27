import os
import glob
import sokoban
# importing functions individually for sanity_check
import mySokobanSolver as solver
import re
import random
import time
import multiprocessing
from functools import partial
from tqdm import tqdm 


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
    taboo_count = len(re.findall(r'X', solver.taboo_cells(wh)))
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
    try: 
        """ Test a warehouse by loading it and classifying it. """
        wh = load_warehouse(file_path, report_path)
        classify_warehouse(wh, report_path)

        solution = "Solved"     # Placeholder: expects solved, not solved, or impossible.
        cost = "N/A"               # Placeholder: cost of the solution.

        # Measure the time taken to solve the warehouse
        start_time = time.time()
        result = solver.solve_weighted_sokoban(wh)  # Call the solver function to solve the warehouse.
        time_taken = time.time() - start_time
        

        if result == "Impossible":
            solution = "Impossible"
        else:
            action, cost = result
        # Reassign the solution, time, and cost variables with actual values.

        return solution, time_taken, cost
    except Exception as e:
        return f"Error: {str(e)}", 0, "N/A"
    

def test_batch(start_warehouse, num_warehouses):
    """ Test a batch of warehouses. """
    # Create a report file for the batch
    report_path = create_report(f"Started with warehouse: {start_warehouse}", f"Number of warehouses tested: {num_warehouses}")

    # Get the list of warehouse files 
    wh_files = sorted(os.listdir("./Assigment1/warehouses"))  # Get the list of files in the warehouses directory
    start_index = wh_files.index(start_warehouse)

    # Select the batch of warehouses to test
    batch_files = wh_files[start_index:start_index + num_warehouses]

    # Display progress bar for the batch
    for file_path in tqdm(batch_files, desc="Testing warehouses", unit="warehouse"):
        full_file_path = os.path.join("./Assigment1/warehouses", file_path)  # Construct full path
        func = partial(test_warehouse, full_file_path, report_path)
        result = run_with_timeout(func, 60)  # 10 seconds timeout
        if result is None:  # Timeout occurred
            solution, time, cost = "Not Solved", "Timeout", "N/A"
        else:
            solution, time, cost = result
        edit_report(report_path, f"Result: Solved? = {solution}, Time: {time} seconds, Cost: {cost}")

    return print(f"Batch test completed. Report saved to {report_path}.")

## Timeout & Other Testing Functions

def fake_test():
    """ Fake test function to simulate the testing process. """
    # Simulate some testing process
    wait_time = random.randint(1, 30)
    time.sleep(wait_time)
    
def _worker(func, queue):
    try:
        result = func()
        queue.put(result)
    except Exception as e:
        queue.put(e)

def run_with_timeout(func, timeout=10):
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=_worker, args=(func, queue))
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        return None

    result = queue.get()
    if isinstance(result, Exception):
        raise result
    return result
        

# Test Solve_Weighted_Sokoban

if __name__ == '__main__':
    test_batch("warehouse_001.txt", 108) # Seems to work as expected, should retest after updating mySokobanSolver.py from github.