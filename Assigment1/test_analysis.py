import os
import glob
import re

"""
    This file reads a test.txt report and summarises the results.

    The purpose of this script is to provide an overview of the test results and to indicate whether changes 
    to solve_weight_sokoban() have improved its performance.
"""

def create_summary():
    """ Create a report file for the batch of warehouses. Returns path to report."""
    # Create a testing directory if it doesn't exist
    summary_dir = os.path.join(os.getcwd(), 'testing_summary')
    if not os.path.exists(summary_dir):
        os.makedirs(summary_dir)

    next_sum_num = 1

    # Find the next test number
    summary_files = glob.glob(os.path.join(summary_dir, 'Summary*.txt'))
    if summary_files:
        # Extract test numbers from filenames and find the maximum
        summary_num = [int(os.path.basename(f).replace('Summary', '').replace('.txt', '')) 
                    for f in summary_files]
        next_sum_num = max(summary_num) + 1 if summary_num else 1

    # Create the new test file
    summary_file_path = os.path.join(summary_dir, f'Summary{next_sum_num}.txt')
    with open(summary_file_path, 'w') as f:
        f.write(f"Summary {next_sum_num}\n\n")

    return summary_file_path 

def edit_report(path, line, header=False):
    """ Edit the report file with the given line. """
    if header:
        with open(path, 'a') as f:
            f.write(line + '\n\n')
    else:
        with open(path, 'a') as f:
            f.write('\t' + line + '\n\n')

"""
    Dictiionary to store the results of the test cases.

    warehouse = {
    'boxes': 0,
    'walls': 0,
    'density': 0.0,
    'taboo_count': 0,
    'weights': [],
    'solved': None,
    'time': 0.0,
    'cost': 0
}
"""

def read_test_file(file_path, summary_path):
    """ Read the test file and return its contents. """

    warehouses = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    solved_with_cost_count = 0

    for i, line in enumerate(lines):
        if "Loaded" in line:
            # warehouse_name = re.search(r'.\/warehouses\\(.+.txt)', line) -- Don't think I need this

            warehouse = {}

            details_line = lines[i + 2].strip()
            result_line = lines[i + 4].strip()

            details_match = re.search(
            r'Boxes:\s*(\d+), Walls:\s*(\d+), Density:\s*([\d.]+), Taboo Count:\s*(\d+), Weights:\s*\[(.*?)\]',
            details_line)

            if details_match:
                warehouse['boxes'] = int(details_match.group(1))
                warehouse['walls'] = int(details_match.group(2))
                warehouse['density'] = float(details_match.group(3))
                warehouse['taboo_count'] = int(details_match.group(4))
                warehouse['weights'] = list(map(int, details_match.group(5).split(',')))

            result_match = re.search(
                r'Result:\s*Solved\?\s*=\s*(\w+), Time:\s*([\d.]+|Timeout)\s*seconds, Cost:\s*(\d+|None|N\/A)',
                result_line
            )

            print(result_match)
            if result_match:
                warehouse['solved'] = result_match.group(1)
                time_value = result_match.group(2)
                cost_value = result_match.group(3)
                
                # Handle time
                if time_value == "Timeout":
                    warehouse['time'] = float('inf')  # Representing timeout as infinity
                else:
                    warehouse['time'] = float(time_value)
                
                # Handle cost
                if cost_value == "None" or cost_value == "N/A":
                    warehouse['cost'] = None
                else:
                    warehouse['cost'] = int(cost_value)

            warehouses.append(warehouse)

    solved_count = 0
    unsolved_count = 0
    impossible_count = 0

    sum_solve_time = 0
    sum_cost = 0

    solved_sum_boxes = 0
    solved_sum_walls = 0
    solved_sum_density = 0
    solved_sum_taboo_count = 0
    solved_sum_weights = 0

    not_solved_sum_boxes = 0
    not_solved_sum_walls = 0
    not_solved_sum_density = 0
    not_solved_sum_taboo_count = 0
    not_solved_sum_weights = 0

    for warehouse in warehouses:
        if warehouse['solved'] == 'Solved':
            solved_count += 1
            sum_solve_time += warehouse['time']
            if warehouse['cost'] is not None:
                sum_cost += warehouse['cost']
                solved_with_cost_count += 1
            solved_sum_boxes += warehouse['boxes']
            solved_sum_walls += warehouse['walls']
            solved_sum_density += warehouse['density']
            solved_sum_taboo_count += warehouse['taboo_count']
            solved_sum_weights += len(warehouse['weights'])

        elif warehouse['solved'] == 'Not Solved':
            unsolved_count += 1
            not_solved_sum_boxes += warehouse['boxes']
            not_solved_sum_walls += warehouse['walls']
            not_solved_sum_density += warehouse['density']
            not_solved_sum_taboo_count += warehouse['taboo_count']
            not_solved_sum_weights += len(warehouse['weights'])

        else:
            impossible_count += 1

    edit_report(summary_path, f"Total Warehouses: {len(warehouses)}")
    edit_report(summary_path, f"Solved: {solved_count}, Unsolved: {unsolved_count}, Impossible: {impossible_count}")
    
    avg_solve_time = f"{sum_solve_time / solved_count:.2f} seconds" if solved_count > 0 else "cannot be calculated"
    edit_report(summary_path, f"Average Solve Time: {avg_solve_time}")
    
    avg_cost = f"{sum_cost / solved_with_cost_count:.2f}" if solved_with_cost_count > 0 else "cannot be calculated"
    edit_report(summary_path, f"Average Solve Cost: {avg_cost}")
    
    avg_solved_boxes = f"{solved_sum_boxes / solved_count:.2f}" if solved_count > 0 else "cannot be calculated"
    avg_not_solved_boxes = f"{not_solved_sum_boxes / unsolved_count:.2f}" if unsolved_count > 0 else "cannot be calculated"
    edit_report(summary_path, f"Average Solved Boxes: {avg_solved_boxes}; Average Not Solved Boxes: {avg_not_solved_boxes}")
    
    avg_solved_walls = f"{solved_sum_walls / solved_count:.2f}" if solved_count > 0 else "cannot be calculated"
    avg_not_solved_walls = f"{not_solved_sum_walls / unsolved_count:.2f}" if unsolved_count > 0 else "cannot be calculated"
    edit_report(summary_path, f"Average Solved Walls: {avg_solved_walls}; Average Not Solved Walls: {avg_not_solved_walls}")
    
    avg_solved_density = f"{solved_sum_density / solved_count:.2f}" if solved_count > 0 else "cannot be calculated"
    avg_not_solved_density = f"{not_solved_sum_density / unsolved_count:.2f}" if unsolved_count > 0 else "cannot be calculated"
    edit_report(summary_path, f"Average Solved Density: {avg_solved_density}; Average Not Solved Density: {avg_not_solved_density}")
    
    avg_solved_taboo_count = f"{solved_sum_taboo_count / solved_count:.2f}" if solved_count > 0 else "cannot be calculated"
    avg_not_solved_taboo_count = f"{not_solved_sum_taboo_count / unsolved_count:.2f}" if unsolved_count > 0 else "cannot be calculated"
    edit_report(summary_path, f"Average Solved Taboo Count: {avg_solved_taboo_count}; Average Not Solved Taboo Count: {avg_not_solved_taboo_count}")
    
    avg_solved_weights = f"{solved_sum_weights / solved_count:.2f}" if solved_count > 0 else "cannot be calculated"
    avg_not_solved_weights = f"{not_solved_sum_weights / unsolved_count:.2f}" if unsolved_count > 0 else "cannot be calculated"
    edit_report(summary_path, f"Average Solved Weights: {avg_solved_weights}; Average Not Solved Weights: {avg_not_solved_weights}")
    
def summary_main(test_path):
    """ Main function to create a summary of the test results. """
    summary_path = create_summary()
    read_test_file(test_path, summary_path)

summary_main("testing/Test37.txt")

