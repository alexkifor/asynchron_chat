from chardet import detect
import re
import csv

def get_data():
    main_data = []
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []

    for i in range(1,4):
        with open(f"info_{i}.txt", 'rb') as file:
            content_bytes = file.read()
        detected = detect(content_bytes)
        encoding = detected['encoding']
        content_text = content_bytes.decode(encoding)
        with open(f"info_{i}.txt", 'w', encoding='utf-8') as file:
            file.write(content_text)
        with open(f"info_{i}.txt", 'r', encoding='utf-8') as file:    
            data = file.read()
            os_prod_reg = re.compile(r'Изготовитель системы:\s*\S*')
            os_prod_list.append(os_prod_reg.findall(data)[0].split()[2])
            os_name_reg = re.compile(r'Название ОС:\s*\S*\s*\S*\s*\S*')
            os_name_list.append(" ".join(os_name_reg.findall(data)[0].split()[3:5]))
            os_code_reg = re.compile(r'Код продукта:\s*\S*')
            os_code_list.append(os_code_reg.findall(data)[0].split()[2])
            os_type_reg = re.compile(r'Тип системы:\s*\S*')
            os_type_list.append(os_type_reg.findall(data)[0].split()[2])
    headers  = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data.append(headers)
    
    for i in range(3):
        main_data.append([])
        main_data[i + 1].append(i + 1)
        main_data[i + 1].append(os_prod_list[i])
        main_data[i + 1].append(os_name_list[i])
        main_data[i + 1].append(os_code_list[i])
        main_data[i + 1].append(os_type_list[i])
        
    return main_data                     

def write_to_csv(name_out_file:str):
    main_data = get_data()
    with open(name_out_file, 'w') as file:
        file_writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        file_writer.writerows(main_data)

write_to_csv('report_task_1.csv')
