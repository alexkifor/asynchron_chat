import json

def writer_order_to_json(item, quantity, price, buyer, date):
    with open('orders.json') as file:
        obj = json.load(file)

    with open('orders.json', 'w', encoding='utf-8') as file:
        add_order = {
            'item': item, 
            'quantity': quantity, 
            'price': price, 
            'buyer': buyer, 
            'date': date 
            }
        obj['orders'].append(add_order)
        json.dump(obj,file, indent=4)

writer_order_to_json('printer', '10', '12500', 'Ivanov I.P.', '23.05.2023')
writer_order_to_json('router', '7', '4300', 'Petrov I.I.', '20.05.2023')
writer_order_to_json('iphone', '1', '72500', 'Sidorov P.P.', '13.05.2023')
        