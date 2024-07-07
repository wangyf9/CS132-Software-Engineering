import unittest
from unittest.mock import MagicMock, patch
import sqlite3
from src.backend.Server import ZmqServerThread
def create_test_account(account_id, password, balance):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO accounts (id, password, balance) VALUES (?, ?, ?)
    ''', (account_id, password, balance))
    
    conn.commit()
    conn.close()
class TestZmqServerThread(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a test database and table
        cls.conn = sqlite3.connect('bank.db')
        cls.cursor = cls.conn.cursor()
        cls.cursor.execute('DROP TABLE IF EXISTS accounts')
        cls.cursor.execute('DROP TABLE IF EXISTS transactions')
        cls.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                balance REAL NOT NULL
            )
            ''')
    
        cls.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            starting_balance REAL NOT NULL,
            ending_balance REAL NOT NULL
        )
        ''')
        
        cls.conn.commit()
        cls.conn.close()
            # Create two accounts
        create_test_account('2024888888', '000000', 10000.0)
        create_test_account('2024000000', '000000', 10000.0)
        cls.zmq_server = ZmqServerThread()
        cls.zmq_server.run = MagicMock()


    @classmethod
    def tearDownClass(cls):
        # Close the test database connection
        cls.conn.close()
        # TestZmqServerThread.zmq_server.socket.close()
        # TestZmqServerThread.zmq_server.context.term()

    def setUp(self):
        self.zmq_server = TestZmqServerThread.zmq_server

    def tearDown(self):
        pass

    def test_001_process_request_create_account_success(self):
        address = "client1"
        message = "create_account@1234567890#000000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "success@Account created successfully")
    def test_002_process_request_create_account_idLessThan10(self):
        address = "client1"
        message = "create_account@145670#000000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@A@Account ID must consist of 10 digits")
    def test_003_process_request_create_account_passwordLessThan6(self):
        address = "client1"
        message = "create_account@5876476543#00000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@B@Password must consist of 6 digits")
    def test_004_process_request_create_account_idExists(self):
        address = "client1"
        message = "create_account@2024888888#000000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@A@Account already exists")
    def test_005_process_request_log_in_success(self):
        address = "client1"
        message = "log_in@2024888888#000000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "success@Log in successful")
    def test_006_process_request_log_in_accountDoesNotExist(self):
        address = "client1"
        message = "log_in@2024888889#000000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@A@Invalid account ID")
    def test_007_process_request_log_in_passwordIncorrect(self):
        address = "client1"
        message = "log_in@2024888888#000001"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@B@Invalid password")
    def test_008_process_request_insert_card_success(self):
        address = "client1"
        message = "insert_card@2024888888#000000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "success@Insert card successful")
    def test_009_process_request_insert_card_accountDoesNotExist(self):
        address = "client1"
        message = "insert_card@2024888889#000000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@A@Invalid account ID")
    def test_010_process_request_insert_card_passwordIncorrect(self):
        address = "client1"
        message = "insert_card@2024888888#000001"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@B@Invalid password")
    def test_011_process_request_deposit_cash_success(self):
        address = "client1"
        message = "deposit_cash@2024888888#200"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "success@$200.00 deposited successfully. Balance: 10000.0 -> 10200.0")
    def test_012_process_request_deposit_cash_accountDoesNotExist(self):
        address = "client1"
        message = "deposit_cash@2024888889#200"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Invalid account ID")
    def test_013_process_request_deposit_cash_invalidAmount1(self):
        address = "client1"
        message = "deposit_cash@2024888888#50001"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Deposit amount must be between $0.01 and $50000.00")
    def test_014_process_request_deposit_cash_invalidAmount2(self):
        address = "client1"
        message = "deposit_cash@2024888888#-78.90"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Deposit amount must be between $0.01 and $50000.00")
    def test_015_process_request_return_card_success(self):
        address = "client1"
        message = "return_card"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "success@Card returned successfully")
    def test_016_process_request_log_out_success(self):
        address = "client1"
        message = "log_out"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "success@Logged out successfully")
    def test_017_process_request_change_password_sameAsOld(self):
        address = "client1"
        message = "change_password@2024888888#000000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@New password cannot be the same as the old password")
    def test_018_process_request_change_password_success_notDigit(self):
        address = "client1"
        message = "change_password@2024888888#abcefg"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Password must consist of 6 digits")
    def test_019_process_request_change_password_lessthan6(self):
        address = "client1"
        message = "change_password@2024888888#12345"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Password must consist of 6 digits")
    def test_020_process_request_change_password_success(self):
        address = "client1"
        message = "change_password@2024888888#123456"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "success@Password changed successfully")
    def test_021_process_request_transfer_money_success(self):
        address = "client1"
        message = "transfer_money@2024888888#2024000000#5000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "success@$5000.00 transferred successfully. Sender balance: 10200.0 -> 5200.0")
    def test_022_process_request_transfer_money_accountDoesNotExist(self):
        address = "client1"
        message = "transfer_money@2024888888#2024000001#5000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Invalid receiver account ID")
    def test_023_1_process_request_transfer_money_invalidAmount1(self):
        address = "client1"
        message = "transfer_money@2024888888#2024000000#50000.01"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Transfer amount must be between $0.01 and $50000.00")
    def test_023_2_process_request_transfer_money_invalidAmount2(self):
        address = "client1"
        message = "transfer_money@2024888888#2024000000#-78.90"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Transfer amount must be between $0.01 and $50000.00")
    def test_024_1_process_request_transfer_money_toitself(self):
        address = "client1"
        message = "transfer_money@2024888888#2024888888#5000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Can't tranfer to your own")
    def test_024_2_process_request_transfer_money_accountIdLessThan10(self):
        address = "client1"
        message = "transfer_money@2024888888#2024#5000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Receiver's account ID must consist of 10 digits")
    def test_024_3_process_request_transfer_money_notSufficientBalance(self):
        address = "client1"
        message = "transfer_money@2024888888#2024000000#40000.0"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Insufficient account balance for transfer")
    def test_025_process_request_withdraw_cash_success(self):
        address = "client1"
        message = "withdraw_cash@2024888888#5200"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "success@$5200.00 withdrawn successfully. Balance: 5200.0 -> 0.0")
    def test_027_process_request_withdraw_cash_insufficientBalance(self):
        address = "client1"
        message = "withdraw_cash@2024888888#50000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Insufficient account balance for withdrawal")
    def test_028_process_request_withdraw_cash_invalidAmount2(self):
        address = "client1"
        message = "withdraw_cash@2024888888#-78.90"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Withdrawal amount must be between $0.01 and $50000.00")
    def test_029_process_request_cancel_account_success(self):
        address = "client1"
        message = "cancel_account@2024888888"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "success@Account canceled successfully")
    def test_030_process_request_cancel_account_notZeroBalance(self):
        address = "client1"
        message = "cancel_account@2024000000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "failed@Account balance must be zero to cancel the account")
    def test_031_process_request_get_balance_success(self):
        address = "client1"
        message = "get_balance@2024000000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
        self.zmq_server.send_string.assert_called_with(address, "balance@15000.0")
    def test_032_process_request_query(self):
        address = "client1"
        message = "query@2024000000"
        self.zmq_server.send_string = MagicMock()
        self.zmq_server.process_request(address, message)
    def test_033_account_exists(self):
        self.assertTrue(self.zmq_server.account_exists("2024000000"))
        self.assertFalse(self.zmq_server.account_exists("2024000001"))
    def test_034_verfiy_password(self):
        self.assertTrue(self.zmq_server.verify_password("2024000000", "000000"))
        self.assertFalse(self.zmq_server.verify_password("2024000000", "000001"))
    def test_035_get_balance(self):
        self.assertEqual(self.zmq_server.get_balance("2024000000"), 15000.0)
    def test_036_has_sufficient_balance(self):
        self.assertTrue(self.zmq_server.has_sufficient_balance("2024000000", 10000.0))
        self.assertFalse(self.zmq_server.has_sufficient_balance("2024000000", 20000.0))
    def test_037_deposit_cash(self):
        self.zmq_server.deposit_cash("2024000000", 5000.0)
        self.assertEqual(self.zmq_server.get_balance("2024000000"), 20000.0)
    def test_038_get_password(self):
        self.assertEqual(self.zmq_server.get_password("2024000000"), "000000")
    def test_039_change_password(self):
        self.zmq_server.change_password("2024000000", "123456")
        self.assertTrue(self.zmq_server.verify_password("2024000000", "123456"))
    def test_040_create_account(self):
        self.assertFalse(self.zmq_server.account_exists("2024888889"))
        self.zmq_server.create_account("2024888889", "000000")
        self.assertTrue(self.zmq_server.account_exists("2024888889"))
    def test_041_transfer_money(self):
        self.zmq_server.transfer_money("2024000000", "2024888889", 5000.0)
        self.assertEqual(self.zmq_server.get_balance("2024000000"), 15000.0)
        self.assertEqual(self.zmq_server.get_balance("2024888889"), 5000.0)
    def test_042_withdraw_cash(self):
        self.zmq_server.withdraw_cash("2024000000", 5000.0)
        self.assertEqual(self.zmq_server.get_balance("2024000000"), 10000.0)
    def test_043_cancel_account(self):
        self.zmq_server.transfer_money("2024888889","2024000000", 5000.0)
        self.zmq_server.cancel_account("2024888889")
        self.assertFalse(self.zmq_server.account_exists("2024888889"))
    def test_044_query(self):
        self.zmq_server.query_account("2024000000")

if __name__ == "__main__":
    unittest.main()