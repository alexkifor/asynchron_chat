import subprocess



PROC = []


while True:
    
    ACTION = input('Choise command: q - exit, '
                   's - run server and clients, '
                   'x - close server and clients sessions: ')
    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROC.append(subprocess.Popen(f'python3 server.py', shell=True, stdout=subprocess.PIPE))
        n = int(input('Enter clients value: '))
        for i in range(n):
            p = subprocess.Popen(f'gnome-terminal -e "python3 client.py -n test_{i}"', shell=True, stdout=subprocess.PIPE)
            PROC.append(p)           
    elif ACTION == 'x':
        while PROC:
            proc_kill = PROC.pop()
            proc_kill.kill()

