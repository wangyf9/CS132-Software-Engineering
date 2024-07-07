import unittest
from tests.functional.scheduling_test import SchedulingFunctionalTest
from tests.functional.door_test import DoorFunctionalTest

if __name__ == "__main__":
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # add scheduling functional tests
    scheduling_tests = test_loader.loadTestsFromTestCase(SchedulingFunctionalTest)
    test_suite.addTests(scheduling_tests)

    # add door functional tests
    door_tests = test_loader.loadTestsFromTestCase(DoorFunctionalTest)
    test_suite.addTests(door_tests)

    # run the test suite
    test_runner = unittest.TextTestRunner()
    test_runner.run(test_suite)
