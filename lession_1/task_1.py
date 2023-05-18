str_1 = 'разработка'
str_2 = 'сокет'
str_3  = 'декоратор'
strs = (str_1, str_2, str_3)

un_str_1 = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
un_str_2 = '\u0441\u043e\u043a\u0435\u0442'
un_str_3 =  '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'
un_strs = (un_str_1, un_str_2, un_str_3)

def my_func(arg:tuple):
    for i in arg:
        print(type(i), i)

my_func(strs)
my_func(un_strs)
