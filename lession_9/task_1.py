from ipaddress import ip_address
from subprocess import Popen, PIPE

class HostPing():
    def __init__(self, lst_ip_addr):
        self.ip_addr = lst_ip_addr

    def host_ping(self, timeout=4, requests=4):
        result = {
            'Available node': '',
            'Unavailable node': '',
            } 
        for addr in self.ip_addr:
            try:
                addr = ip_address(addr)
            except ValueError:
                pass
            proc = Popen(['ping', '-c', f'{requests}', '-W', f'{timeout}', str(addr)], shell=False, stdout=PIPE)
            proc.wait()
            if proc.returncode == 0:
                result['Available node'] += f"{str(addr)}\n"
                res_str = f"{addr} - Node available"
            else:
                result['Unavailable node'] += f"{str(addr)}\n"
                res_str = f"{addr} - Node unavailable"
            print(res_str)
        return result
    
   
        

if __name__ == '__main__':
    ip_addrs = ['yandex.ru', '2.2.2.2', '192.168.0.100', '192.168.0.101']
    ping_obj = HostPing(ip_addrs)
    ping_obj.host_ping()