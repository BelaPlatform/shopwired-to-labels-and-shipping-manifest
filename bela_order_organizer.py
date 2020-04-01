# coding: utf-8

import sys
import getopt
import os
import csv
import copy

input_file_name = ''
try:
    opts, args = getopt.getopt(sys.argv[1:],"hf:")
except getopt.GetoptError:
    print 'bela_order_organizer.py -f <inputfile>'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print 'bela_order_organizer.py -f <inputfile>'
        sys.exit()
    elif opt == '-f':
        input_file_name = arg
        print(input_file_name)
        if not os.path.exists(input_file_name):
            print 'Filepath does not exist'
            sys.exit()

print("File to be processed: %s " % input_file_name)
print("2 csv files will be created: \n\tMANIFEST.csv to be uploaded to drop 'n go\n\tNEW_ORDER.csv to be used by the tex file that creates the labels")
print("2 txt files will be created: \n\titems_to_ship.txt: all items to be shipped today \n\torder_info.txt: includes id, address, shipping method, items to be shipped and comments")

intl_DHL_value_limit = 270;
eu_DHL_value_limit = 300;

shipping_methods_translate_GB = {
    'Tracked and signed shipping': 'Special Delivery 1pm',
    'Tracked and Signed': 'Special Delivery 1pm',
    'First Class (untracked)': '1st Class Delivery',
    'Delivery cost for Bela': '1st Class Delivery'
}

shipping_methods_translate_World = {
    'Tracked and signed shipping': 'Int. Tr. and Signed',
    'Tracked and Signed': 'Int. Tr. and Signed',
    'First Class (untracked)': 'Int. Standard',
    'Delivery cost for Bela': 'Int. Standard'
}

items_dictionary = {
    '16GB SD card flashed with Bela software': '16GB Flashed SD Card',
}

EU_country_codes = [
    'BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR',
    'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT',
    'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE', 'UK'
]

class Item():
    def __init__(self, name, quantity, sku=None):
        self.name = name
        self.quantity = quantity
        self.sku = sku


    def update_quantity(self, value):
        self.quantity += value

class Order():
    def __init__(self, order_id, shipping_method, shipping_address, value, items=None, extras=None, comments=None):
        self.order_id = order_id
        self.shipping_method = shipping_method
        self.shipping_address = shipping_address
        self.value = value
        self.items = items or []
        self.extras = extras or []
        self.comments = comments or ''

    # Decode and Print Address Method
    # (it assumes that the address elements are in the same order every time!!!)
    def print_address(self):
        address_string = ''

        for i, address_element in enumerate(self.shipping_address):
            if i == 0:
                address_string = address_string + address_element + '\n'
            elif i == 1 and address_element:
                address_string = address_string + ' ('+address_element+')\n'
            elif i in (2,3,4) and address_element:
                address_string = address_string + address_element + '\n'
            elif i in (7,8):
                if not address_element:
                    address_element = '?????'
                address_string = address_string + address_element + '\n'
            elif i in (5, 6) and address_element:
                    address_string = address_string + address_element + ", "
        print(address_string)

    # Update shipping method based on country of origin
    def update_shipping_method(self):
        country_code = self.shipping_address[-1]
        method = self.shipping_method.rstrip()

        if country_code.rstrip() == 'GB':
            if method in shipping_methods_translate_GB:
                self.shipping_method = shipping_methods_translate_GB[method]
        elif country_code.rstrip() in EU_country_codes:
            if float(self.value) >= eu_DHL_value_limit:
                self.shipping_method = 'DHL'
            elif method in shipping_methods_translate_World:
                self.shipping_method = shipping_methods_translate_World[method]
        else:
            if float(self.value) >= intl_DHL_value_limit:
                self.shipping_method = 'DHL'
            elif method in shipping_methods_translate_World:
                self.shipping_method = shipping_methods_translate_World[method]

        print(self.shipping_method)

    def add_item(self, name, quantity, sku=None):
        filtered_items = [x for x in self.items if x.name == name]

        if not filtered_items:
            self.items.append(Item(name, quantity, sku))
        else:
            filtered_items[0].update_quantity(quantity)

    def add_extras(self, name, quantity, sku=None):
        filtered_extras = [x for x in self.extras if x.name == name]
        if not filtered_extras:
            self.extras.append(Item(name, quantity, sku))
        else:
            filtered_extras[0].update_quantity(quantity)

    def print_items(self):
        for i in self.items+self.extras:
            item_string = str(i.quantity) + ' ' + i.name
            if i.sku:
                item_string = item_string + ' ('+i.sku+')'
            print(item_string)


class Address():
    def __init__(self, name, company, address1, address2, city, province, zipcode, country, t='shipping'):
        self.name = name
        self.company = company
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.province = province
        self.zipcode = zipcode
        self.country = country
        self.t = t


# Parse extras string into different items
def parse_extras(extras):
    extras_list = extras.split(',')
    parsed_extras = []
    for extra in extras_list:
        if extra:
            extra_num = None
            extra_name = None
            extra_info = extra.split(' x ')
            if len(extra_info) == 2:
                extra_num = int(extra_info[0])
                extra_name = extra_info[1].lstrip().rstrip()
            else:
                extra_num = 1
                extra_name = extra_info[0].lstrip().rstrip()
            parsed_extras.append([extra_name, extra_num])
    return parsed_extras


orders = []
items = []

# Read input file
with open(input_file_name, 'r') as in_file:
    # Declar csv reader
    reader = csv.reader(in_file)
    # Extract header
    header = next(reader)

#     print(header)


    id_index = header.index('Name')
    ship_method_index = header.index('Shipping Method')
    val_index = header.index('Total')

    address_indices = [
        header.index('Shipping Name'),
        header.index('Shipping Company'),
        header.index('Shipping Address1'),
        header.index('Shipping Address2'),
        header.index('Shipping City'),
        header.index('Shipping Province'),
        header.index('Shipping Zip'),
        header.index('Shipping Country'),
    ]

    SKU_index = header.index('Lineitem sku')
    item_index = header.index('Lineitem name')
    num_index = header.index('Lineitem quantity')
#     extras_index = header.index('Product Extras')

    comments_index = header.index('Notes')


    for row in reader:

        ## Create new item
        new_item_name = row[item_index]
        if new_item_name in items_dictionary:
            new_item_name = items_dictionary[new_item_name]

        num_items = int(row[num_index])
        new_item = Item(new_item_name, num_items, row[SKU_index])

        filtered_items = [x for x in items if x.name == new_item.name]

        if not filtered_items:
            items.append(new_item)
        else:
            filtered_items[0].update_quantity(new_item.quantity)

#         ## Parse extras
#         parsed_extras = parse_extras(row[extras_index])
#         new_extras = []
#         if parsed_extras:
#             for pe in parsed_extras:
#                 new_extra_name = pe[0]
#                 if new_extra_name in items_dictionary:
#                     new_extra_name = items_dictionary[new_extra_name]
#                 new_extra = Item(new_extra_name, num_items * int(pe[1]))

#                 filtered_items = [x for x in items if x.name == new_extra_name]
#                 filtered_extras = [x for x in new_extras if x.name == new_extra_name]

#                 if not filtered_items:
#                     items.append(copy.deepcopy(new_extra))
#                 else:
#                     filtered_items[0].update_quantity(new_extra.quantity)
#                 new_extras.append(new_extra)


        ## Filter orders
        filtered_orders = [x for x in orders if x.order_id == row[id_index]]
        # Alternatively:
            # filtered_orders = filter(lambda x: x.order_id == row[id_index],  orders)

        current_order = None
        if not filtered_orders:
            # Compose Address
            full_address = []
            for i in address_indices:
                full_address.append(row[i])

            current_order = Order (
                row[id_index],
                row[ship_method_index],
                full_address,
                row[val_index],
                None,
                None,
                row[comments_index]
            )
            orders.append(current_order)
        else:
            current_order = filtered_orders[0].order_id
        orders[-1].add_item(new_item.name, new_item.quantity, new_item.sku)
#         for ne in new_extras:
#             orders[-1].add_extras(ne.name, ne.quantity)

#   stdoutput = sys.stdout
    sys.stdout = open('items_to_ship.txt', 'w')
    for i in items:
        print('\n....................\n')
        print(str(i.quantity)+' '+i.name)

    sys.stdout = open('order_info.txt', 'w')
    for o in orders:
        print('\n--------------------\n')
        print(o.order_id + '\n')
        o.print_address()
        o.update_shipping_method()
        print('\n')
        o.print_items()
        if o.comments:
            print('\n')
            print(o.comments)
#    sys.stdout = stdoutput
    sys.stdout = sys.__stdout__


##WRITTING BACK TO CSV
# Manifest csv
manifest_header = ['Item ', 'Country', 'Shipping Service', 'Ship to Zip', 'Ship To Address 1', 'Sale Price', 'Currency']
manifest_data = []
for o in orders:
    if o.shipping_method is not 'DHL':
        order_data = []
        order_data.append(o.order_id)
        order_data.append(o.shipping_address[-1])
        order_data.append(o.shipping_method)
        order_data.append(o.shipping_address[-2])
        order_data.append(o.shipping_address[2])
        order_data.append('£'+ str(int(round(float(o.value)))))
        order_data.append('GBP')

        manifest_data.append(order_data)

with open('MANIFEST.csv', 'w') as manifest_file:
    writer = csv.writer(manifest_file)
    # Print header
    writer.writerow(manifest_header)
    # Print data
    writer.writerows(manifest_data)

# Labels csv
labels_header = [
    'Delivery Name', 'Delivery Company Name', 'Delivery Address Line 1',
    'Delivery Address Line 2', 'Delivery Address Line 3', 'Delivery Town/City',
    'Delivery State/County', 'Delivery Postcode', 'Delivery Country'
]
labels_data = []
for o in orders:
    order_data = []
    for shipping_data in o.shipping_address:
        order_data.append(shipping_data)
    order_data.insert(4, '') #insert empty string for Delivery Address Line 3

    labels_data.append(order_data)

with open('NEW_ORDER.csv', 'w') as labels_file:
    writer = csv.writer(labels_file)
    # Print header
    writer.writerow(labels_header)
    # Print data
    writer.writerows(labels_data)
