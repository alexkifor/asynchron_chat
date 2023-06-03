import unittest
import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
from main.client import create_msg, handler_server_msg


class TestClass(unittest.TestCase):
    def test_create_msg(self):
        test = create_msg()
        test['time'] = 123.123
        test_dict = {'action': 'presence',
                     'time': 123.123,
                     'type': 'status',
                     'user': {
                         'account_name': 'Guest'
                     }}
        self.assertEqual(test, test_dict)

    def test_answer_200(self):
        self.assertEqual(handler_server_msg({'response': 200}), '200: OK')

    def test_answer_400(self):
        self.assertEqual(handler_server_msg({'response': 400, 'error': 'Bad request'}), '400: Bad request')

    def test_no_response(self):
        self.assertRaises(ValueError, handler_server_msg, {'error': 'Bad request'})

if __name__ == '__main__':
    unittest.main()