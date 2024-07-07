# Weekly Report - Week 15

This week, we focused on transitioning testing responsibilities, deep diving into the existing codebase, improving the elevator scheduling algorithm, and implementing model checking using UPPAAL. 

## Completed Tasks

### 1. Handover of Testing Responsibilities

**Objective:** Ensure a smooth transition of the testing responsibilities to the new assignee.

**Tasks Completed:**

- Documented the existing testing framework and procedures.
- Conducted a walkthrough of the unit tests and functional tests with the new assignee.
- Provided examples and detailed explanations on how to extend and maintain the test suite.
- Addressed any questions and provided support to ensure the new assignee is comfortable with their responsibilities.

### 2. Codebase Review

**Objective:** Gain a comprehensive understanding of the existing codebase.

**Tasks Completed:**

- Reviewed the architecture and design of the elevator system.
- Studied the implementation of key components including the elevator scheduler, state management, and communication protocols.
- Identified areas for potential improvements and optimization in the existing code.

### 3. Improving Scheduling Algorithm

**Objective:** Enhance the efficiency and accuracy of the elevator scheduling algorithm.

**Tasks Completed:**

- Refined the `tryAssignElevatorId` method to improve decision-making based on the elevator's state and position.
- Adjusted the floor range thresholds for better alignment with the system’s logic.
- Incorporated a more robust distance calculation mechanism to prioritize elevator assignments.
- Ensured that the updated algorithm was thoroughly tested using various scenarios to validate its performance.

### 4. Implementation of UPPAAL Model Checking

**Objective:** Utilize UPPAAL for model checking to verify the correctness and reliability of the elevator system.

**Tasks Completed:**

- Modeled the elevator system in UPPAAL, focusing on the states and transitions of both the elevator and passengers.
- Defined properties and constraints to be verified using UPPAAL’s query language.
- Conducted model checking to identify potential deadlocks, unreachable states, and other logical errors.
- Analyzed the results and made necessary adjustments to the model and the system to ensure compliance with the specified properties.

## Challenges and Resolutions

- **Testing Transition:** Initial confusion in understanding the existing test framework was mitigated by detailed walkthroughs and documentation.
- **Code Comprehension:** Complex logic in the scheduler required additional time to fully grasp, addressed by iterative review and testing.
- **UPPAAL Modeling:** Ensuring accurate representation of the system in UPPAAL was challenging, resolved by step-by-step verification and refinement.

## Next Steps

- Continue supporting the new testing assignee with any ongoing questions or issues.
- Monitor the performance and efficiency of the improved scheduling algorithm in real-world scenarios.
- Extend the UPPAAL model to cover additional aspects of the system for comprehensive verification.
- Document any further changes and updates to the codebase and algorithms.