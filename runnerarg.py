import subprocess
import csv
import os
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def execute_commands(hbi_csv, ival_location, result_csv):
    results = []

    try:
        logging.debug("Starting TOS...")
        start_result = subprocess.run([r'D:\Users\arastu\hdmtOS_3.23.0.0_BUILD39045_Release\Runtime\Release\HdmtSupervisorService\HdmtTosCtrl.exe', 'starttos'], capture_output=True, text=True)
        results.append(['starttos', start_result.returncode, start_result.stdout.strip(), start_result.stderr.strip()])
        logging.debug("TOS started.")
    except Exception as e:
        logging.error(f"Error starting TOS: {e}")
        results.append(['starttos', -1, '', str(e)])

    # Group test cases by recipe
    recipes = defaultdict(list)

    with open(hbi_csv, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip the header row
        for row in csvreader:
            if len(row) < 2:
                logging.warning("Skipping row with insufficient columns")
                continue
            recipe = row[2].strip()
            recipes[recipe].append(row)

    for recipe, rows in recipes.items():
        logging.debug(f"Processing recipe: {recipe}")
        parts = recipe.split(',')
        if parts[0].lower() == 'ival' or parts[0].lower() == '#ival':
            parts.pop(0)
        modified_line = ' '.join(parts)

        load_tp_command = [r'D:\Users\arastu\hdmtOS_3.23.0.0_BUILD39045_Release\Runtime\Release\SingleScriptCmd.exe', 'loadTP', ival_location] + modified_line.split()
        try:
            logging.debug(f"Executing command: {' '.join(load_tp_command)}")
            load_tp_result = subprocess.run(load_tp_command, capture_output=True, text=True, shell=True)
            stpl_file = next((part for part in modified_line.split() if part.endswith('.stpl')), '')
            results.append([stpl_file, load_tp_result.returncode, load_tp_result.stdout.strip(), load_tp_result.stderr.strip()])
            logging.debug("loadTP command executed.")
        except Exception as e:
            logging.error(f"Error executing loadTP: {e}")
            results.append([stpl_file, -1, '', str(e)])

        try:
            logging.debug("Executing init command...")
            init_result = subprocess.run([r'D:\Users\arastu\hdmtOS_3.23.0.0_BUILD39045_Release\Runtime\Release\SingleScriptCmd.exe', 'init'], capture_output=True, text=True, shell=True)
            results.append(['init', init_result.returncode, init_result.stdout.strip(), init_result.stderr.strip()])
            logging.debug("init command executed.")
        except Exception as e:
            logging.error(f"Error executing init: {e}")
            results.append(['init', -1, '', str(e)])

        try:
            logging.debug("Executing Lot Start Command...")
            lot_result = subprocess.run([r'D:\Users\arastu\hdmtOS_3.23.0.0_BUILD39045_Release\Runtime\Release\SingleScriptCmd.exe', 'lotStart'], capture_output=True, text=True, shell=True)
            results.append(['Lot Start', lot_result.returncode, lot_result.stdout.strip(), lot_result.stderr.strip()])
            logging.debug("Lot Start command executed.")
        except Exception as e:
            logging.error(f"Error executing Lot Start: {e}")
            results.append(['lotStart', -1, '', str(e)])

        # Execute all test cases for the current recipe
        for row in rows:
            try:
                module_name = row[0].strip().split('.')[0]  # Extract module name without extension
                test_name = row[1].strip()  # Extract test name
                executeTestInstance = [
                    r'D:\Users\arastu\hdmtOS_3.23.0.0_BUILD39045_Release\Runtime\Release\SingleScriptCmd.exe', 
                    'executeNamedFlow',
                    f"{module_name}::{test_name}"
                ]
                logging.debug(f"Executing test instance: {' '.join(executeTestInstance)}")
                executeTestInstance_result = subprocess.run(executeTestInstance, capture_output=True, text=True, shell=True)
                results.append(['executeTestInstance', executeTestInstance_result.returncode, executeTestInstance_result.stdout.strip(), executeTestInstance_result.stderr.strip()])
                logging.debug(f"executeTestInstance result: {executeTestInstance_result}")
            except Exception as e:
                results.append(['executeTestInstance', -1, '', str(e)])
                logging.error(f"Failed to execute test instance: {e}")

        try:
            logging.debug("Executing endLot Command...")
            endLot_result = subprocess.run([r'D:\Users\arastu\hdmtOS_3.23.0.0_BUILD39045_Release\Runtime\Release\SingleScriptCmd.exe', 'endLot'], capture_output=True, text=True, shell=True)
            results.append(['endLot', endLot_result.returncode, endLot_result.stdout.strip(), endLot_result.stderr.strip()])
            logging.debug("endLot command executed.")
        except Exception as e:
            logging.error(f"Error executing endLot: {e}")
            results.append(['endLot', -1, '', str(e)])

        try:
            logging.debug("Executing unloadTP command...")
            unload_tp_result = subprocess.run([r'D:\Users\arastu\hdmtOS_3.23.0.0_BUILD39045_Release\Runtime\Release\SingleScriptCmd.exe', 'unloadTP'], capture_output=True, text=True, shell=True)
            results.append(['unloadTP', unload_tp_result.returncode, unload_tp_result.stdout.strip(), unload_tp_result.stderr.strip()])
            logging.debug("unloadTP command executed.")
        except Exception as e:
            logging.error(f"Error executing unloadTP: {e}")
            results.append(['unloadTP', -1, '', str(e)])

    try:
        logging.debug("Stopping TOS...")
        stop_result = subprocess.run([r'D:\Users\arastu\hdmtOS_3.23.0.0_BUILD39045_Release\Runtime\Release\HdmtSupervisorService\HdmtTosCtrl.exe', 'stoptos'], capture_output=True, text=True, shell=True)
        results.append(['stoptos', stop_result.returncode, stop_result.stdout.strip(), stop_result.stderr.strip()])
        logging.debug("TOS stopped.")
    except Exception as e:
        logging.error(f"Error stopping TOS: {e}")
        results.append(['stoptos', -1, '', str(e)])

    # Write results to CSV
    with open(result_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Command', 'Return Code', 'Output', 'Error'])
        for result in results:
            csvwriter.writerow(result)

    logging.info(f"Results saved to {result_csv}")

def main():
    hbi_csv = r'Chasis\hbi.csv'
    ival_location = r'D:\Users\arastu\HDMTOS\Validation\iVal'
    result_csv = r'Result\results.csv'

    execute_commands(hbi_csv, ival_location, result_csv)

if __name__ == '__main__':
    main()