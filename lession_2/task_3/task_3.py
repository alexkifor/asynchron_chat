import yaml

data_in = {
    'item': ['pen', 'pencil', 'workbook'],
    'quantity': 10,
    'price': {'pen': '7\u20ac - 10\u20ac',
              'pencil': '5\u20ac - 8\u20ac',
              'workbook': '1\u20ac - 5\u20ac'
              }
    }
with open('report_task_3.yaml', 'w', encoding='utf-8')  as file:
    yaml.dump(data_in, file, default_flow_style=False, allow_unicode=True, sort_keys=False)

with open('report_task_3.yaml', 'r', encoding='utf-8') as file:
    data__out = yaml.load(file, Loader=yaml.SafeLoader)

print(data_in == data__out)

