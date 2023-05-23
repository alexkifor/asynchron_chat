str_1 = 'разработка'
str_2 = 'администрирование'
str_3 = 'protocolo'
str_4 =  'standart'

strs = (str_1, str_2, str_3, str_4)

elem_b = []
elem_str = []

for i in strs:
    el_b = i.encode('utf-8')
    elem_b.append(el_b)
    el_str = el_b.decode('utf-8')
    elem_str.append(el_str)

print(elem_b)
print(elem_str)