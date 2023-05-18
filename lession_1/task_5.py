import subprocess

def ping_site(arg:str):
    args = ['ping', arg]
    subproc_ping = subprocess.Popen(args, stdout = subprocess.PIPE)
    for line in subproc_ping.stdout:
        el = line.decode('utf-8')
        print(el, end='')

ping_site('yandex.ru')
ping_site('yotube.com')




