import json
import unittest
import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
from main.common.utils import send_msg, get_msg




class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encod_msg = ''
        self.rec_msg = ''

    def send(self, msg):
        json_test_msg = json.dumps(self.test_dict)
        self.encod_msg = json_test_msg.encode('utf-8')
        self.rec_msg = msg                                      
        
    def recv(self, max_len):
        json_test_msg = json.dumps(self.test_dict)
        return json_test_msg.encode('utf-8')


class Tests(unittest.TestCase):
    test_dict = {
        'action': 'presence',
        'time': 123.123,
        'type': 'status',
        'user': {
            'account_name': 'test'
        }
    }

    test_dict_recv_ok = {'response': 200}
    test_dict_recv_err = {
        'response': 400,
        'error': 'Bad request'
    }
    def test_send_msg(self):
        test_socket = TestSocket(self.test_dict)
        send_msg(test_socket, self.test_dict)
        self.assertEqual(test_socket.encod_msg, test_socket.rec_msg)
        with self.assertRaises(Exception):
            send_msg(test_socket, test_socket)

    def test_get_msg(self):
        test_socket_ok = TestSocket(self.test_dict_recv_ok)
        test_socket_err = TestSocket(self.test_dict_recv_err)
        self.assertEqual(get_msg(test_socket_ok), self.test_dict_recv_ok)
        self.assertEqual(get_msg(test_socket_err), self.test_dict_recv_err)

if __name__ == '__main__':
    unittest.main()