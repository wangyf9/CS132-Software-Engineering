## Usage

### Running the Main Program

To run the main program, navigate to the project's root directory and execute the following command:

```bash
python -m main
```

### Running Tests

To run the tests, follow the steps below:

1. Open a terminal and navigate to the project's root directory.

2. Use the following command to run the desired test. Replace `test_type` with one of the following options: `main`, `door`, `passenger`, `scheduling`, `control_unit`, `elevator_unit`, `sync`.

   ```bash
   python -m main --test test_type
   ```

   For example, to run the `elevator` module's unit test, use:

   ```bash
   python -m main --test elevator_unit
   ```

   Or to run the system's door functional test, use:

   ```bash
   python -m main --test door
   ```
