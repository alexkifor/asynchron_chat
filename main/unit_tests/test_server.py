import unittest
import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
from main.server import handler_client_msg

class TestServer(unittest.TestCase):
    dict_200 = {'response': 200}
    dict_400 = {
        'response': 400,
        'error': 'Bad request'
    }

    def test_no_action(self):
        self.assertEqual(handler_client_msg({'time': '1.123', 'type': 'status', \
                                             'user': {'account_name': 'Guest'}}), self.dict_400)
    
    def test_wrong_action(self):
        self.assertEqual(handler_client_msg({'action': 'Wrong', 'time': '1.123', \
                                             'type': 'status', 'user': {'account_name': 'Guest'}}), self.dict_400)
    

    def test_no_time(self):
        self.assertEqual(handler_client_msg({'action': 'presence', 'type': 'status', \
                                             'user': {'account_name': 'Guest'}}), self.dict_400)

    def test_no_type(self):
        self.assertEqual(handler_client_msg({'action': 'presence', 'time': '1.123', \
                                             'user': {'account_name': 'Guest'}}), self.dict_400)
 
    def test_no_user(self):
        self.assertEqual(handler_client_msg({'action': 'presence', 'time': '1.123', 'type': 'status'}), self.dict_400)
            
    def test_wrong_user(self):
        self.assertEqual(handler_client_msg({'action': 'presence', 'time': '1.123', \
                                             'type': 'status', 'user': {'account_name': 'Wrong'}}), self.dict_400)

    def test_check_ok(self):
        self.assertEqual(handler_client_msg({'action': 'presence', 'time': '1.123', \
                                             'type': 'status', 'user': {'account_name': 'Guest'}}), self.dict_200)    
    
    
if __name__ == '__main__':
    unittest.main()