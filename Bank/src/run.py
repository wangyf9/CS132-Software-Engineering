import os
import subprocess
import time
# Get the absolute path of run.py
run_path = os.path.abspath(__file__)

# Get the directory of run.py
run_dir = os.path.dirname(run_path)

# Construct the absolute paths of main.py and ../TestCase/main.py
main_path = os.path.join(run_dir, './frontend/Controller.py')
testcase_path = os.path.join(run_dir, './backend/main.py')

# Run /TestCase/main.py in a new command line window
p_testcase = subprocess.Popen(f'start cmd /k python {testcase_path} ', shell=True)

# Run main.py in another new command line window
p_main = subprocess.Popen(f'start cmd /k python {main_path}', shell=True)

#p_testcase.communicate(input='y\n'.encode())   
#this step is no use, but you can try to write a code to input 'y\n' to the command line window