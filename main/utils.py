import json

def get_msg(client):
    encode_resp = client.recv(1024)
    if isinstance(encode_resp, bytes):
        json_resp = encode_resp.decode('utf-8')
        resp = json.loads(json_resp)
        if isinstance(resp, dict):
            return resp
        raise ValueError
    raise ValueError

def send_msg(socket, msg):
    json_msg = json.dumps(msg)
    msg_bytes = json_msg.encode('utf-8')
    socket.send(msg_bytes)