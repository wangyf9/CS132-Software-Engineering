1. Setup the Environment 
python 3.10+
pip install pyzmq

2. Code Structure
/YourCodeExample/NetClient.py - This file is responsible for communicating with the server in the test cases.
/YourCodeExample/main.py - This file contains a sample student code, which you can modify to be the main file of your own designed system.
/TestCase/main.py - This file is responsible for sending test cases to your system and will interact based on the data sent by your system, including a very simple test case.
/TestCase/Server.py - This file is responsible for communicating with the client in the student code.

3.How to Run the Code
First, run /TestCase/main.py in Terminal to setup the judger.
Then, run /YourCodeExample/main.py in ANOTHER Terminal.
Finally, input 'y' to run the naive testcase.


4.available operation/event

    //available user operation

    ON ATM:
    "create_acount@password":  // E.g. create_acount@123456
    "close_acount"   
    "insert_card@id":  // E.g. insert_card@2024132789
    "return_card"  
    "deposit_cash@num":  // E.g. deposit_cash@2000
    "withdraw_cash@num@password"  // E.g. withdraw_cash@1000@123456
    
    ON APP:
    "log_in@id@password#app_id":  // E.g. log_in@2024132789@123456#1
    "log_out#app_id":  // E.g. log_out#1
    "close_app#app_id":  // E.g. close_app#1

    Both:
    "change_password@new_password(#app_id)":  // E.g. change_password@654321(#1)
    "transfer_money@receiver_id@num(#app_id)"  // E.g. transfer_money@2023123456@500(#1)
    "query(#app_id)":  // E.g. query(#1)
    note: () means optional, if (#app_id) exists, it means the query is for the corresponding app, otherwise it is for the ATM.

    Other:
    "open_app"
    "reset"
    

    //available system event
    "acount_created@id":  // E.g. acount_created@2024132789
    "acount_closed@id":  // E.g. acount_closed@2024132789
    "card_inserted@id":  // E.g. card_inserted@2024132789
    "card_returned@id":  // E.g. card_returned@2024132789
    "cash_deposited@num":  // E.g. cash_deposited@2000
    "cash_withdrawn@num":  // E.g. cash_withdrawn@1000

    "logged_in@id#app_id":  // E.g. logged_in@2024132789#1
    "logged_out@id#app_id":  // E.g. logged_out@2024132789#1
    "app_closed#app_id":  // E.g. app_closed#1

    "password_changed(#app_id)":  // E.g. password_changed(#1)
    "money_transfered@num(#app_id)":  // E.g. money_transfered@500(#1)
    "query_showed(#app_id)":  // E.g. query_showed(#1)

    "app_opened#app_id":  // E.g. app_opened#2
    
    "failed": ["create_acount", "close_acount", "insert_card", "return_card", "deposit_cash", "withdraw_cash", 
                "log_in#app_id", "log_out#app_id", "close_app#app_id", "change_password(#app_id)", "transfer_money(#app_id)", "query(#app_id)", "open_app]

    

    Example Case:
    "create_acount@123456"             ->   acount_created@2024132789(a random id in this case) 
    "deposit_cash@2000"                ->   cash_deposited@2000
    
    "open_app"                         ->   app_opened#1
    "log_in@2024132789@123456#1"       ->   logged_in@2024132789#1
    "transfer_money@2023123456@500#1"  ->   money_transfered@500#1

    "withdraw_cash@1000@987654"        ->   failed@withdraw_cash
    "withdraw_cash@1000@123456"        ->   cash_withdrawn@1000#1
    "query"                            ->   query_showed
    "return_card"                      ->   card_returned@2024132789




5.Banking system initial assumption
Assume that there is an account in the initial database,  and the account id is 2023123456, with 500 Yuan deposit in it.