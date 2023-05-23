str_1 = 'attribute'
str_2 = 'класс'
str_3 = 'функция'
str_4 = 'type'

strs = (str_1, str_2, str_3, str_4)

for i in strs:
    el = i.encode('ascii', 'ignore')
    if len(el) == 0:
        print(f"слово {i} невозможно записать в байтовом типе")