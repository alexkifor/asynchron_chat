from ipaddress import ip_address
from task_1 import HostPing

class HostRangePing(HostPing):
    def __init__(self):
          self.ip_addr = None


    def host_range_ping(self, host):
        try:
            start_ip = host
            last_oct = int(start_ip.split('.')[3])
        except Exception as e:
                print(e)
        else:
            if last_oct <= 0 or last_oct >= 254:
                 print('incorrectly entered host')
                 exit(1)
                
        while True:
            end_ip = input('enter value ip_adress to check: ')
            if not end_ip.isnumeric():
                print('you need enter int')
            else:
                if (last_oct + int(end_ip)) > 254:
                      print(f"maximum number of hosts to check: {254 - last_oct}")
                else:
                     break
        host_list = []
        [host_list.append(str(ip_address(start_ip) + x))for x in range(int(end_ip))]
        self.ip_addr = host_list
        return super().host_ping()

if __name__ == '__main__':
    ip_addr = '192.168.0.110'
    ping_obj = HostRangePing()
    ping_obj.host_range_ping(ip_addr)

                
           