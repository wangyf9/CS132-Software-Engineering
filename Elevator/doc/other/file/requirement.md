# Elevator System Requirement
## 1. System goal
In this project, our goal was to develop a software to manage the operation of two elevators in a three-floor building and to improve the efficiency of this process. We not only designed button panels and UIs for each floor and each elevator so that the user can know what is going on in the elevator, but also designed the elevator control system so that the scheduling of the two elevators can be done more efficiently, thus providing a better experience for the user.

## 2. Basic requirements setting
- There are three floors, denoted as `floor_num = 3`
- There are two elevators, denoted as `elevator_num = 2`
- Setting limits on elevators:
  - Elevator Move speed is fixed at $0.05 floor/s$, denoted as `current_speed = 0.05`
  - Time to open and close the door is $10s$, denoted as `door_close_time = 1.0; door_open_time=1.0;doorSpeed=0.1`
  - Default Time to stop when the door open is $30s$, denoted as `elevator_wait_time=3.0;doorSpeed=0.1`

## 3. Basic use case
### 3.1 Use case diagram
<div align=center><img src=../diagram_image/new_use_case.png width = "65%" ></div>
<center style="font-size:14px;color:#C0C0C0;text-decoration:underline">Elevator system normal use case diagram</center>  
This is a preliminary overview of the normal use case diagram for the elevator system. Specific details and requirements are discussed in the following sections.

### 3.2 Sequence diagram
<div align=center><img src=../diagram_image/basic_sequence.png width = "70%" ></div>
<center style="font-size:14px;color:#C0C0C0;text-decoration:underline">Elevator system basic sequence diagram</center> 
This is a preliminary overview of the basic sequence diagram for the elevator system while using. Specific details and requirements are discussed in the following sections.

### 3.3 Class diagram
<div align=center><img src=../diagram_image/class_diagram.png width = "70%" ></div>
<center style="font-size:14px;color:#C0C0C0;text-decoration:underline">Elevator system physical consists class diagram</center> 
This is an intact overview of the class diagram for the elevator system physical consists.

## 4. Normal requirements
1. Requirement1: Elevator_UI  
- R1.1: The passengers should be able to know elevator's position and moving direction.
- R1.2: The passengers should be able to control the elevator's door, including open and close while the elevator is stopping.
- R1.3: The passengers should be able to select the certain floor they want to go.
- R1.4: The elevator controller system should be able to get the information when passengers press the buttons.

1. Requirement2: Floor_UI
- R2.1: The passengers should be able to know two elevators' position and moving direction.
- R2.2: The passengers should be able to select and press the direction button they want to go.
- R2.3: The passengers should be able to know which floor they are on.
- R2.4: The elevator controller system should be able to know how buttons are pressed on each floor.

1. Requirement3: Elevator_controller_system
- R3.1: The controller system should be able to schedule the two elevators
  - R3.1.1: The controller system should assign a close or not in used elevator to pick users up if there is a need.
    - R3.1.1.1: If both elevators are not in used, assign the closer one to pick users.
    - R3.1.1.2: If one elevator is using and another one is not, assign the free elevator to go.
    - R3.1.1.3: If both are working, users should wait for one to be free.
  - R3.1.2: The controller system should not assign two elevators at the same time to take users on a certain floor.
  - R3.1.3: The controller system should allow the elevator to deliver users to the target floor and not stop at non-target floors.
- R3.2: The controller system should be able to control the door of the elevator
  - R3.2.1: While moving, the controller system should hold the door closed.
  - R3.2.2: Every time, the controller system should open and close the door for a fixed time `door_open_time = 1.0; door_close_time = 1.0`.
  - R3.2.3: After arriving, the controller system should open the door and wait for a fixed time  `elevator_wait_time=3.0`.
  - R3.2.4: If someone press the close button, the controller system should close the door in advance. But if there's someone getting on the elevator, the controller system should not close the door.
  - R3.2.5: If someone press the open button, the controller system should open the door for an additional time.
- R3.3: The controller system should be able to receive the commands from the button panels and information about the elevator
- R3.4: The controller system should allow the elevators to operate in a safe condition, including operating at a speed less than the maximum speed and not open elevator door while the elevator is moving.

## 5. Special cases in discussion
- The elevator on the first floor only goes up.
- The third floor elevator only goes down. 
- Open the door and close it at the same time. It won't close.
- Press any key to see if there is an elevator bug.
- When the elevator goes up, the first floor is pressed and when it reaches the third floor/ the second floor(Depends on the top floor being pressed), the 1st floor button is canceled.
- No one presses the button on the third floor. At this point, the second floor goes up, but people press the button to go to the first floor, and the elevator closes, then opens, then closes again and goes down to the first floor.
- Two elevators on the 1st floor initially.
- People need to press the button in advance or they can't get to the target floor.