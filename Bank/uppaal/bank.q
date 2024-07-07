//This file was generated from (Academic) UPPAAL 5.0.0 (rev. 714BA9DB36F49691), 2023-06-21

/*

*/
A[] Server.balance[0]>=0 and Server.balance[1]>=0 and Server.balance[2]>=0

/*

*/
A<> (UserWithApp(0).WaitForTransfer imply UserWithApp(0).Idle)

/*

*/
A[] ((UserWithApp(0).Idle and UserWithApp(1).Idle and UserWithApp(2).Idle) imply (Server.balance[0]+Server.balance[1]+Server.balance[2]+UserWithApp(0).cash+UserWithApp(1).cash+UserWithApp(2).cash+ATMachine.temp_cash == 30))

/*

*/
A[] not deadlock
