## 1. Setup the Environment 
python 3.10+
pip install pyzmq

## 2. Code Structure
/frontend/NetClient.py - This file is responsible for communicating with the server in the test cases.
/frontend/Controller.py - This file contains the entire front-end controller, which sends information to the back-end based on actions taken on the UI, and displays the processing information returned by the back-end on the UI.
/frontend/APP_UI.py - This file contains the implementation of the APP_UI.
/frontend/ATM_UI.py - This file contains the implementation of the ATM_UI.
/frontend/functionalTest.py - This file contains the testing cases of the bank system.
/backend/main.py - The file is responsible for processing the information from the system and sending the return information to the system. At the same time connecting to the database.
/backend/Server.py - This file is responsible for communicating with the client in the student code.
/backend/bank.py - database function

## 3. How to Run the Code
First, run /backend/main.py in Terminal to setup the judger.
Then, run /frontend/Controller.py.py in ANOTHER Terminal to set up UI.

## 4. available operation/event
  For this part, you can refer to the requirement and user manual document to learn about details.
  For our implementation, we only allow click in the UI, but can not go on api testing because of our framework building

## 5. Banking system initial assumption
Assume that there is an account in the initial database,  and the account id is 2023123456, password is 123456, with 500 Yuan deposit in it.