# Week 17 Report

## Overview
During Week 17, the primary focus was on completing the functional tests for the elevator system. The testing efforts were concentrated on the scheduling and door control systems.

## Completed Tasks
1. **Functional Testing**
   - Finalized the functional tests for the elevator system.
   - Ensured comprehensive coverage of both scheduling and door control functionalities.

2. **Scheduling System Tests**
   - Implemented test cases to verify the correct operation of the scheduling algorithm under various scenarios:
     - **TestCase1:** Tested elevator response to a single up request from the first floor, with additional requests during operation.
     - **TestCase2:** Verified the behavior when a request is made close to the elevator’s destination floor.
     - **TestCase3:** Ensured proper handling of simultaneous up and down requests from the same floor.
     - **TestCase4:** Checked system response to simultaneous requests from different floors.
     - **TestCase5:** Tested the handling of overlapping requests with different destinations.

3. **Door Control System Tests**
   - Developed and executed test cases to ensure the door control system operates correctly:
     - **TestCase1:** Verified door reopening when the open button is pressed during closing.
     - **TestCase2:** Ensured the door remains open when the open button is continuously pressed.
     - **TestCase3:** Tested door behavior when the close button is pressed during opening.
     - **TestCase4:** Checked system response to simultaneous open requests from inside and outside the elevator.

## Key Findings
- **Scheduling System**
  - The scheduling algorithm efficiently handled various request patterns, ensuring minimal wait times and optimal elevator usage.
  - Edge cases, such as simultaneous opposite direction requests, were managed correctly without significant delays.

- **Door Control System**
  - The door control system correctly prioritized safety, reopening doors when necessary and preventing premature closures.
  - Continuous open requests were managed effectively, ensuring the door remained open as long as required.

## Next Steps
- Address any identified issues or bugs from the functional tests.
- Begin integration testing to ensure all components work seamlessly together.
- Conduct performance testing to verify system efficiency under load.

## Conclusion
The completion of the functional tests marks a significant milestone in the elevator system project. The focus on scheduling and door control systems has ensured that these critical components operate correctly and efficiently. Moving forward, integration and performance testing will further solidify the system’s reliability and readiness for deployment.
