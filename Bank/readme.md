## 1. Setup the Environment 
python 3.10+
pip install pyzmq

## 2. Code Structure

- /frontend/NetClient.py - This file is responsible for communicating with the server in the test cases.
- /frontend/Controller.py - This file contains the entire front-end controller, which sends information to the back-end based on actions taken on the UI, and displays the processing information returned by the back-end on the UI.
- /frontend/APP_UI.py - This file contains the implementation of the APP_UI.
- /frontend/ATM_UI.py - This file contains the implementation of the ATM_UI.
- /frontend/functionalTest.py - This file contains the testing cases of the bank system.
- /backend/main.py - The file is responsible for processing the information from the system and sending the return information  to the system. At the same time connecting to the database.
- /backend/Server.py - This file is responsible for communicating with the client in the student code.
- /backend/bank.py - database function

## 3. How to Run the Code

First, run /backend/main.py in Terminal to setup the judger.
Then, run /frontend/Controller.py in ANOTHER Terminal to set up UI.(There exists some problems in Controller.py, therefore, you should delete the `from . ` when you want to run the program code to start the app. But if you want to run the test, this part should not be deleted !!!)

## 4. Available operation/event
  For this part, you can refer to the requirement and user manual document to learn about details.
  For our implementation, we only allow click in the UI, but can not go on api testing because of our framework building

## 5. Running Unit Tests

To run unit tests, use the following command:

```bash
# e.g for the `controller` module
python -m src.test.unittest_controller
```
```bash
# e.g for the `server` module
python -m src.test.unittest_server
```


## 6. Running Functional Tests

To run functional tests, edit src/test/run_functionalTest.py at 10th line
```python
# Copy the following test you want to run
#   functionalTestATM.py
#   functionalTestApp.py
#   functionalTestMultipleUser.py
test_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'functionalTestMultipleUser.py'))

```
And then run
```bash
# e.g for the functionalTest
python -m src.test.run_functionalTest
```