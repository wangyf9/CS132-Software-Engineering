# CS132 - Software - Engineering - Final Project

## Introduction

- Final Project for Software Engineering class(CS132) in Shanghaitech, spring, 2024.
- It consists of three independent projects, those are elevator system, banking system, and painkiller-injection system respectively.
- The project coding task is based on Python, and the model checking task is mainly verified by Uppaal.
- Group members: 祝宇航, 王芸飞, 贾舜康
- I mainly take responsibility for the requirement part of the elevator system, the development part of the banking system, and the validation part of the painkiller-injection system.

## Elevator system

- A building with 3 floors and a basement (-1 1 2 3 floor)
- 2 elevators(should be coordinated)
- Interfaces:
  - Button panels and display inside each elevator
  - Button panels and display on each floor
- System Events:
  - Door open, door closed
  - Elevator arrive at each floor
![elevator](/Image/elevator.png)

## Banking system

- A database containing all account data
  - Checking & saving accounts
- An interface for APP
  - transfer money to other people
  - open/close account
- An interface for ATM
  - deposit & withdraw cash
  - query account details
![bank](/Image/bank.png)

## Painkiller-Injection system

- Patients need painkiller after surgery
- There are limits on
  - The total amount per day 3ml 
  - Amount in a short period 1ml/hr
- Baseline
  - 0.01-0.1ml/min
- Bolus
  - 0.2-0.5ml/shot
- Interface
  - For physician
  - Patient button
![painkiller](/Image/painkiller.png)

For more details, you can view the subfolder readme to learn more about these projects.