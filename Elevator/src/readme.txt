1. Setup the Environment 
python 3.10+
pip install pyzmq

2.available operation/event

    //available user operation

    "open_door"
    "close_door"
    "call_up": ["-1", "1", "2"], //For example, call_up@1 means a user on the first floor presses the button to call the elevator to go upwards.
    "call_down": ["3", "2", "1"], //For instance, call_down@3 signifies a user on the third floor pressing the button to call the elevator to go downwards.
    "select_floor": ["-1#1", "-1#2", "1#1", "1#2", "2#1", "2#2", "3#1", "3#2"], //For example, select_floor@2#1 means a user in elevator #1 selects to go to the second floor.
    "reset": When your elevator system receives a reset signal, it should reset the elevator's state machine to its initial state

    //available system event

    "door_opened": ["#1", "#2"], door_opened#1 means the doors of elevator #1 have opened.
    "door_closed": ["#1", "#2"], door_closed#1 means the doors of elevator #1 have closed.
    "floor_arrived":["up","down",""],["-1","1","2","3"],["#1", "#2"] //"up_floor_1_arrived#1"， indicating that elevator #1 has arrived at the first floor while moving upwards. "floor_1_arrived#1",indicating that elevator #1 has stopped at the first floor.

3.Elevator system initial assumption
Assume that both elevators(#1, #2) initially stop on the first floor and the doors are closed.