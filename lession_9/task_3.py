from tabulate import tabulate
from task_2 import HostRangePing

class HostRangePingTab(HostRangePing):
    def __init__(self):
        super().__init__()

    def host_range_ping_tab(self, host):
        res_dict = super().host_range_ping(host)
        print()
        print(tabulate([res_dict], headers='keys', tablefmt="pipe", stralign="center"))



if __name__ == '__main__':
    ip_addr = '192.168.0.100'
    ping_obj = HostRangePingTab()
    ping_obj.host_range_ping_tab(ip_addr)
