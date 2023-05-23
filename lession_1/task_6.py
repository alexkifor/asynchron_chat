import locale
print(f"локальная кодировка по умолчанию {locale.getpreferredencoding()}")

strs = ('сетевое программирование', 'сокет', 'декоратор')

file = open("test_file.txt", "w")

for i in strs:
    file.write(f"{i}\n")
print(f"кодировка файла по умолчанию {file.encoding}")
file.close()

with open('test_file.txt', 'r', encoding='utf-8') as file:
    for line in file:
        print(line, end='')

