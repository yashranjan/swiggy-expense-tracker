import requests
import json
import sys
from rich import print
from datetime import datetime
import xlwt

HEADERS = {
    'Host': 'www.swiggy.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.swiggy.com/my-account/orders',
    'Content-Type': 'application/json'
}

GET_ORDERS_URL = 'https://www.swiggy.com/dapi/order/all?order_id='


class InfoPoint():
    def __init__(self, name='', address='', mobile='') -> None:
        self.name = name
        self.address = address
        self.mobile = mobile

    def __getitem__(self, key):
        return self.__dict__[key]


class Person(InfoPoint):
    pass


class Restaurant(InfoPoint):
    pass


class Dish():
    def __init__(self, name='', is_veg=True, quantity=1, base_price=1, discount=0) -> None:
        self.name = name
        self.is_veg = is_veg
        self.quantity = quantity
        self.base_price = base_price
        self.discount = discount


class CleanDataPoint:
    def __init__(self, price=0, person=Person(), restaurant=Restaurant(), date_time=datetime.now(), dishes=[], charges=0.0, discount=0.0, delivery_time=0, raining=False) -> None:
        self.price = price
        self.person = person
        self.restaurant = restaurant
        self.date_time = date_time
        self.dishes = dishes
        self.charges = charges
        self.discount = discount
        self.delivery_time = delivery_time//60
        self.raining = raining

    def addDish(self, name, is_veg, quantity, base_price, discount):
        self.dishes.append(Dish(name, is_veg, quantity, base_price, discount))

    def __repr__(self) -> str:
        data_to_print = 'Swiggy ordered on {date_time} from {restaurant.name} by {person.name} for Rs. {price} while it was {raining_cond} raining!!'.format(
            **self.__dict__, raining_cond="not" if not self.raining else "")
        return data_to_print

    def __getitem__(self, key):
        return self.__dict__[key]


def getCleanData(orders):
    def getDishes(order_items):
        tmp_dishes = []
        for item in order_items:
            dish = Dish(item['name'], item['is_veg'], item['quantity'],
                        item['base_price'], item['item_total_discount'])
            tmp_dishes.append(dish)
        return tmp_dishes

    ret_lst = []
    for order in orders:
        person = Person(
            order['delivery_address']['name'], order['delivery_address']['address_line1']+order['delivery_address']['address_line2']+order['delivery_address']['address'], order['delivery_address']['mobile'])
        dishes = getDishes(order['order_items'])
        charges = sum([float(i) for j, i in order['charges'].items()])
        restaurant = Restaurant(
            order['restaurant_name'], order['restaurant_address'])
        delivery_time = int(order['delivery_time_in_seconds'])
        price = order['order_total']
        discount = order['order_discount_effective']
        date_time = order['updated_at']
        raining = order['free_del_break_up']['rainFee']

        ret_lst.append(CleanDataPoint(price, person, restaurant, date_time,
                       dishes, charges, discount, delivery_time, raining))

    return ret_lst


def getOrders(cookies):
    print("Retrieving...")
    orders_lst = []
    spent = 0
    s = requests.Session()
    last_order_id = ''
    num_of_orders = 0
    while 1:
        # 10 orders retrieved in each api call
        URL = ''
        if last_order_id != '':
            URL = GET_ORDERS_URL+str(last_order_id).strip()
        else:
            URL = GET_ORDERS_URL

        r = s.get(URL, headers=HEADERS, cookies=cookies)
        resp = json.loads(r.text)
        if resp['statusCode'] == 1:
            print("[red][-] Status Code is 1, exiting[/red]")
            break

        if len(resp['data']['orders']) == 0:
            print("Reached end of orders")
            break

        for order in resp['data']['orders']:
            orders_lst.append(order)
            order_id = order['order_id']
            order_total = order['order_total']
            num_of_orders += 1
            spent += order_total

        last_order_id = resp['data']['orders'][-1]['order_id']

    average_spent = spent//num_of_orders
    print()
    print(
        f"[green]Total money spent on swiggy.com : [bold]INR {spent:,}[/bold][/green]")
    print(
        f"[green]Total number of orders placed : [bold]{num_of_orders:,}[/bold][/green]")
    print(
        f"[green]Average money spent on each order : [bold]INR {average_spent:,}[/bold][/green]")
    return orders_lst


def cookiesToDict():
    print("[green][+][/green] Getting cookies from [u]cookies.json[/u]")
    data = None
    cookies = {}
    try:
        with open("cookies.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        print("[red][-] [u]cookies.json[/u] not found in the path[/red]")
        print(str(e))
        return None

    try:
        for i in data:
            cookies[i['name']] = i['value']
    except Exception as e:
        print("[red][-] Cookies are not in proper format[/red]")
        print(str(e))
        return None

    return cookies


def checkLogin(cookies):
    # First check if logged in
    print("[green][+][/green] Checking if session is valid")
    r = requests.get(GET_ORDERS_URL, headers=HEADERS, cookies=cookies)
    resp = None
    try:
        resp = json.loads(r.text)
    except Exception as e:
        print("[red][-] Unexpected Response received[/red]")
        return False

    if 'statusCode' not in resp or 'data' not in resp:
        print("[red][-] Unexpected Response received[/red]")
        return False
    if resp['statusCode'] == 1:
        print("[red][-] Not logged in, check cookies and try again[/red]")
        return False

    return True


def generateXLS(cleaned_data):

    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('Sheet 1')

    keys = ['person[name]', 'restaurant[name]', 'date_time',
            'price', 'discount', 'delivery_time', 'raining', 'veg/non-veg']

    for idx, key in enumerate(keys):
        worksheet.write(0, idx, key)

    for row, data_point in enumerate(cleaned_data):
        for col, key in enumerate(keys):
            val = None
            if 'veg' in key:
                val = str((sum([1 for i in data_point['dishes'] if i.is_veg]), sum(
                    [1 for i in data_point['dishes'] if not i.is_veg])))
            elif '[' in key:
                first_key = key[:key.index('[')]
                second_key = key[key.index('[')+1:-1]
                val = data_point[first_key][second_key]
            else:
                val = data_point[key]
            worksheet.write(row+1, col, val)

    workbook.save('example.xls')


if __name__ == "__main__":
    print("Started Script..:vampire:")
    cookies = cookiesToDict()
    if cookies is None:
        sys.exit()
    if checkLogin(cookies):
        orders = getOrders(cookies)
        cleaned_order_data = getCleanData(orders)
        generateXLS(cleaned_order_data)
