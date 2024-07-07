### ATM Functionality

1. **create_account@password**
    - Boundary Conditions: Password length and complexity (e.g., minimum of 8 characters, including uppercase letters, lowercase letters, and numbers).
    - Constraints: Check for duplicate account IDs or usernames.

2. **close_account**
    - Boundary Conditions: Ensure the account has sufficient balance to cover any outstanding fees.
    - Constraints: User identity verification (e.g., through password) should be performed before closing the account.

3. **insert_card@id**
    - Boundary Conditions: Validity of the card number (e.g., length and checksum).
    - Constraints: Check if the card is blacklisted or frozen.

4. **return_card**
    - Boundary Conditions: Check for any unfinished transactions before the card is returned.
    - Constraints: Ensure the card is safely ejected before returning.

5. **deposit_cash@num**
    - Boundary Conditions: Minimum and maximum values for the deposit amount.
    - Constraints: Check if the cash capacity of the ATM is sufficient to store the new cash.

6. **withdraw_cash@num@password**
    - Boundary Conditions: Sufficient account balance for withdrawal.
    - Constraints: Password verification, availability of cash inventory in the ATM.

### APP Functionality

1. **log_in@id@password#app_id**
    - Boundary Conditions: Correct format for user ID and password.
    - Constraints: Limit on the number of login attempts (to prevent brute-force attacks), multi-factor authentication.

2. **log_out#app_id**
    - Boundary Conditions: Check if the user is logged in.
    - Constraints: Ensure all session data is cleared upon logout.

3. **close_app#app_id**
    - Boundary Conditions: Check if the application is in use.
    - Constraints: Ensure all unsaved data is saved before closing.

### Both (Shared Functionality)

1. **change_password@new_password(#app_id)**
    - Boundary Conditions: Length and complexity of the new password.
    - Constraints: Avoid using the old password as the new password, multi-factor authentication.

2. **transfer_money@receiver_id@num(#app_id)**
    - Boundary Conditions: Minimum and maximum values for the transfer amount.
    - Constraints: Ensure sufficient account balance, validity of the receiver's account, prevent duplicate transfers.

3. **query(#app_id)**
    - Boundary Conditions: Limit on query frequency (to prevent excessive querying).
    - Constraints: Ensure real-time and accurate query data.

### Event Logging

1. **logged_in@id#app_id**
    - Boundary Conditions: Check if the user is already logged in.
    - Constraints: Prevent multiple logins for the same account.

2. **logged_out@id#app_id**
    - Boundary Conditions: Check if the user is logged in.
    - Constraints: Ensure all session data is cleared upon logout.

3. **app_closed#app_id**
    - Boundary Conditions: Check if the application is in use.
    - Constraints: Ensure all unsaved data is saved before closing.

4. **password_changed(#app_id)**
    - Boundary Conditions: Length and complexity of the new password.
    - Constraints: Avoid using the old password as the new password.

5. **money_transferred@num(#app_id)**
    - Boundary Conditions: Minimum and maximum values for the transfer amount.
    - Constraints: Ensure sufficient account balance, validity of the receiver's account, prevent duplicate transfers.

6. **query_showed(#app_id)**
    - Boundary Conditions: Limit on query frequency (to prevent excessive querying).
    - Constraints: Ensure real-time and accurate query data.

### Failure Cases (Errors)

**"failed":** Consider the following tests when these operations fail:
- Provide clear error messages to help users understand the issue.
- Ensure system consistency after the error occurs (e.g., transaction rollback).
- Log all failed attempts for future analysis and improvement.

