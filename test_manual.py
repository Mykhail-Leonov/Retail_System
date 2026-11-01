
from models import Category, Product, User, Staff, Manager, Customer
from inventory import Inventory
from sales import SaleItem, SalesTransaction, SalesManager, InStoreSale, OnlineSale, SalesFactory
from observers import LowStockNotifier
from io import StringIO
from contextlib import redirect_stdout


def main():

    print("SMART RETAIL SYSTEM - TESTING")
    print("=============================")


    # TEST 1: CATEGORY

    print("\nTEST 1: Category")
    print("----------------")

    category = Category(1, "Electronics")
    print("Category created successfully.")

    category.update_name("Computer Accessories")
    print("Category name updated successfully.")


    # TEST 2: PRODUCT

    print("\nTEST 2: Product")
    print("---------------")

    product = Product(101, "Wireless Mouse", 19.99, category)

    print("Original price:", product.get_price())

    product.update_details("Gaming Mouse", 24.99)

    print("Updated price:", product.get_price())


    # TEST 3: INVALID PRODUCT PRICE

    print("\nTEST 3: Product Validation")
    print("--------------------------")

    try:
        product.update_details("Gaming Mouse", -10)

    except ValueError as error:
        print("Validation error:", error)


    # TEST 4: USER, STAFF AND MANAGER

    print("\nTEST 4: User Roles")
    print("------------------")

    staff = Staff(1, "Alex")
    manager = Manager(2, "Taylor")

    users = [staff, manager]

    for user in users:
        print("Role:", user.get_role())
        print("Can manage inventory:", user.can_manage_inventory())
        print()


    # TEST 5: INHERITANCE

    print("TEST 5: Inheritance")
    print("-------------------")

    print("Staff is a User:", isinstance(staff, User))
    print("Manager is a User:", isinstance(manager, User))


    # TEST 6: INVALID USER NAME

    print("\nTEST 6: User Validation")
    print("-----------------------")

    try:
        invalid_user = Staff(3, "")

    except ValueError as error:
        print("Validation error:", error)


    # TEST 7: CREATE INVENTORY

    print("\nTEST 7: Create Inventory")
    print("------------------------")

    inventory = Inventory()
    inventory.add_category(category)

    print("Inventory and category added successfully.")


    # TEST 8: ADD PRODUCT

    print("\nTEST 8: Add Product")
    print("-------------------")

    inventory.add_product(product, 10)

    assert inventory.get_stock(101) == 10
    print("Product added with 10 units in stock.")


    # TEST 9: DECREASE STOCK

    print("\nTEST 9: Decrease Stock")
    print("----------------------")

    inventory.update_stock(101, -3)

    assert inventory.get_stock(101) == 7
    print("Remaining stock:", inventory.get_stock(101))


    # TEST 10: INCREASE STOCK

    print("\nTEST 10: Increase Stock")
    print("-----------------------")

    inventory.update_stock(101, 5)

    assert inventory.get_stock(101) == 12
    print("Updated stock:", inventory.get_stock(101))


    # TEST 11: INVALID STOCK

    print("\nTEST 11: Invalid Stock")
    print("----------------------")

    try:
        inventory.update_stock(101, -20)

    except ValueError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Invalid stock change was accepted.")

    assert inventory.get_stock(101) == 12


    # TEST 12: DUPLICATE PRODUCT

    print("\nTEST 12: Duplicate Product")
    print("--------------------------")

    try:
        duplicate = Product(101, "Keyboard", 39.99, category)
        inventory.add_product(duplicate, 5)

    except ValueError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Duplicate product was accepted.")


    # TEST 13: MISSING PRODUCT

    print("\nTEST 13: Missing Product")
    print("------------------------")

    try:
        inventory.get_stock(999)

    except KeyError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Missing product was accepted.")


    # TEST 14: SEARCH PRODUCT

    print("\nTEST 14: Search Product")
    print("-----------------------")

    results = inventory.search_product("gaming")

    assert len(results) == 1
    assert results[0] is product

    print("Found product:", results[0].get_name())


    # TEST 15: UPDATE PRODUCT

    print("\nTEST 15: Update Product")
    print("-----------------------")

    inventory.update_product(101, "Gaming Mouse Pro", 29.99)

    assert product.get_name() == "Gaming Mouse Pro"
    assert product.get_price() == 29.99

    print("Updated:", product.get_name(), product.get_price())


    # TEST 16: LOW-STOCK PRODUCTS

    print("\nTEST 16: Low Stock")
    print("------------------")

    keyboard = Product(102, "Keyboard", 39.99, category)
    inventory.add_product(keyboard, 3)

    low_stock = inventory.get_low_stock()

    assert keyboard in low_stock
    assert product not in low_stock

    print("Low-stock product:", keyboard.get_name())


    # TEST 17: INVENTORY REPORT

    print("\nTEST 17: Inventory Report")
    print("-------------------------")

    report = inventory.inventory_report()

    assert "Gaming Mouse Pro" in report
    assert "Keyboard" in report
    assert "Stock: 12" in report
    assert "Stock: 3" in report

    print(report)


    # TEST 18: REMOVE PRODUCT

    print("\nTEST 18: Remove Product")
    print("-----------------------")

    inventory.remove_product(102)

    assert inventory.search_product("Keyboard") == []

    try:
        inventory.get_stock(102)

    except KeyError:
        print("Keyboard removed from inventory and stock.")

    else:
        raise AssertionError("Removed product still has a stock record.")


    # TEST 19: CANNOT REMOVE CATEGORY IN USE

    print("\nTEST 19: Category In Use")
    print("------------------------")

    try:
        inventory.remove_category(1)

    except ValueError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Category with products was removed.")


    # TEST 20: REMOVE UNUSED CATEGORY

    print("\nTEST 20: Remove Unused Category")
    print("-------------------------------")

    spare_category = Category(2, "Accessories")
    inventory.add_category(spare_category)
    inventory.remove_category(2)

    try:
        inventory.remove_category(2)

    except KeyError:
        print("Unused category removed successfully.")

    else:
        raise AssertionError("Removed category still exists.")


    # TEST 21: INVALID SEARCH

    print("\nTEST 21: Invalid Search")
    print("-----------------------")

    try:
        inventory.search_product("   ")

    except ValueError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Empty search was accepted.")


    # TEST 22: INVALID PRODUCT UPDATE

    print("\nTEST 22: Invalid Product Update")
    print("-------------------------------")

    try:
        inventory.update_product(101, "", 40)

    except ValueError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Invalid product update was accepted.")

    assert product.get_name() == "Gaming Mouse Pro"
    assert product.get_price() == 29.99

    # TEST 23: CREATE CUSTOMER

    print("\nTEST 23: Create Customer")
    print("------------------------")

    customer = Customer(1, "Jordan")
    assert isinstance(customer, Customer)
    print("Customer created successfully.")


    # TEST 24: SALE ITEM CALCULATION

    print("\nTEST 24: Sale Item")
    print("------------------")

    sale_item = SaleItem(product, 2)

    assert round(sale_item.line_total(), 2) == 59.98
    print("Line total:", round(sale_item.line_total(), 2))


    # TEST 25: CREATE TRANSACTION

    print("\nTEST 25: Create Transaction")
    print("---------------------------")

    transaction = SalesTransaction(1001, customer, staff)
    assert isinstance(transaction, SalesTransaction)
    print("Transaction created successfully.")


    # TEST 26: ADD ITEM AND CALCULATE TOTAL

    print("\nTEST 26: Transaction Total")
    print("--------------------------")

    transaction.add_item(product, 2)

    assert round(transaction.calculate_total(), 2) == 59.98
    print("Transaction total:", round(transaction.calculate_total(), 2))


    # TEST 27: MULTIPLE PRODUCTS

    print("\nTEST 27: Multiple Products")
    print("--------------------------")

    mouse_pad = Product(103, "Mouse Pad", 4.99, category)
    inventory.add_product(mouse_pad, 8)
    transaction.add_item(mouse_pad, 3)

    assert round(transaction.calculate_total(), 2) == 74.95
    assert inventory.get_stock(101) == 12
    assert inventory.get_stock(103) == 8
    print("Total for two products:", round(transaction.calculate_total(), 2))
    print("Stock unchanged until sale is recorded.")


    # TEST 28: INVALID SALE QUANTITY

    print("\nTEST 28: Invalid Sale Quantity")
    print("------------------------------")

    try:
        transaction.add_item(product, 0)

    except ValueError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Invalid quantity was accepted.")

    assert round(transaction.calculate_total(), 2) == 74.95


    # TEST 29: INVALID CUSTOMER NAME

    print("\nTEST 29: Invalid Customer")
    print("-------------------------")

    try:
        Customer(2, "")

    except ValueError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Invalid customer was accepted.")


    # TEST 30: INVALID TRANSACTION CUSTOMER

    print("\nTEST 30: Invalid Transaction")
    print("----------------------------")

    try:
        SalesTransaction(1002, "Jordan", staff)

    except TypeError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Invalid transaction was accepted.")


    # TEST 31: ORIGINAL SALE PRICE

    print("\nTEST 31: Original Sale Price")
    print("----------------------------")

    temporary_product = Product(104, "Webcam", 20.00, category)
    saved_item = SaleItem(temporary_product, 2)
    temporary_product.update_details("Webcam", 30.00)

    assert saved_item.line_total() == 40.00
    print("Original line total:", saved_item.line_total())

    # TEST 32: CREATE SALES MANAGER

    print("\nTEST 32: Create Sales Manager")
    print("-----------------------------")

    sales_manager = SalesManager(inventory)
    print("Sales manager created successfully.")


    # TEST 33: RECORD SALE AND UPDATE STOCK

    print("\nTEST 33: Record Sale")
    print("--------------------")

    sales_manager.record_sale(transaction)

    assert inventory.get_stock(101) == 10
    assert inventory.get_stock(103) == 5
    assert sales_manager.get_sales_data(101) == [2]
    assert sales_manager.get_sales_data(103) == [3]
    print("Mouse stock:", inventory.get_stock(101))
    print("Mouse Pad stock:", inventory.get_stock(103))


    # TEST 34: DUPLICATE TRANSACTION ID

    print("\nTEST 34: Duplicate Transaction")
    print("------------------------------")

    duplicate_sale = SalesTransaction(1001, customer, staff)
    duplicate_sale.add_item(product, 1)

    try:
        sales_manager.record_sale(duplicate_sale)
    except ValueError as error:
        print("Validation error:", error)
    else:
        raise AssertionError("Duplicate transaction was accepted.")

    assert inventory.get_stock(101) == 10


    # TEST 35: CANNOT RECORD OR EDIT A RECORDED SALE

    print("\nTEST 35: Recorded Sale Protection")
    print("---------------------------------")

    try:
        sales_manager.record_sale(transaction)
    except ValueError as error:
        print("Validation error:", error)
    else:
        raise AssertionError("Recorded sale was accepted again.")

    try:
        transaction.add_item(product, 1)
    except ValueError as error:
        print("Validation error:", error)
    else:
        raise AssertionError("Recorded sale was changed.")

    assert inventory.get_stock(101) == 10


    # TEST 36: NOT ENOUGH STOCK

    print("\nTEST 36: Insufficient Stock")
    print("---------------------------")

    too_large_sale = SalesTransaction(1002, customer, staff)
    too_large_sale.add_item(product, 11)

    try:
        sales_manager.record_sale(too_large_sale)
    except ValueError as error:
        print("Validation error:", error)
    else:
        raise AssertionError("Sale exceeded available stock.")

    assert inventory.get_stock(101) == 10


    # TEST 37: CHECK ALL STOCK BEFORE SELLING

    print("\nTEST 37: Multiple Product Stock Check")
    print("------------------------------------")

    mixed_sale = SalesTransaction(1003, customer, staff)
    mixed_sale.add_item(product, 2)
    mixed_sale.add_item(mouse_pad, 6)

    try:
        sales_manager.record_sale(mixed_sale)
    except ValueError as error:
        print("Validation error:", error)
    else:
        raise AssertionError("Sale with insufficient stock was accepted.")

    assert inventory.get_stock(101) == 10
    assert inventory.get_stock(103) == 5
    print("Both stock quantities are unchanged.")


    # TEST 38: MISSING INVENTORY PRODUCT

    print("\nTEST 38: Missing Sale Product")
    print("-----------------------------")

    unknown_product = Product(999, "Unknown Product", 5.00, category)
    missing_sale = SalesTransaction(1004, customer, staff)
    missing_sale.add_item(unknown_product, 1)

    try:
        sales_manager.record_sale(missing_sale)
    except KeyError as error:
        print("Validation error:", error)
    else:
        raise AssertionError("Sale with missing product was accepted.")

    assert inventory.get_stock(101) == 10


    # TEST 39: EMPTY SALE

    print("\nTEST 39: Empty Sale")
    print("-------------------")

    empty_sale = SalesTransaction(1005, customer, staff)

    try:
        sales_manager.record_sale(empty_sale)
    except ValueError as error:
        print("Validation error:", error)
    else:
        raise AssertionError("Empty sale was accepted.")


    # TEST 40: REPEATED PRODUCT QUANTITIES

    print("\nTEST 40: Repeated Product")
    print("-------------------------")

    repeated_sale = SalesTransaction(1006, customer, staff)
    repeated_sale.add_item(product, 6)
    repeated_sale.add_item(product, 6)

    try:
        sales_manager.record_sale(repeated_sale)
    except ValueError as error:
        print("Validation error:", error)
    else:
        raise AssertionError("Combined quantities exceeded stock.")

    assert inventory.get_stock(101) == 10


    # TEST 41: SECOND SUCCESSFUL SALE AND HISTORY

    print("\nTEST 41: Sales History")
    print("----------------------")

    second_sale = SalesTransaction(1007, customer, manager)
    second_sale.add_item(product, 1)
    second_sale.add_item(mouse_pad, 2)

    sales_manager.record_sale(second_sale)

    assert inventory.get_stock(101) == 9
    assert inventory.get_stock(103) == 3
    assert sales_manager.get_sales_data(101) == [2, 1]
    assert sales_manager.get_sales_data(103) == [3, 2]
    assert sales_manager.get_sales_data(999) == []
    print("Mouse sales history:", sales_manager.get_sales_data(101))
    print("Mouse Pad sales history:", sales_manager.get_sales_data(103))
    print("Stock after second sale:", inventory.get_stock(101), inventory.get_stock(103))

    # TEST 42: CREATE IN-STORE SALE USING FACTORY

    print("\nTEST 42: In-Store Sale Factory")
    print("------------------------------")

    in_store_sale = SalesFactory.create_sale("in_store", 1008, customer, staff)

    assert isinstance(in_store_sale, InStoreSale)
    assert isinstance(in_store_sale, SalesTransaction)
    assert in_store_sale.get_channel() == "In-Store"
    print("Created:", in_store_sale.get_channel())


    # TEST 43: CREATE ONLINE SALE USING FACTORY

    print("\nTEST 43: Online Sale Factory")
    print("----------------------------")

    online_sale = SalesFactory.create_sale("online", 1009, customer, staff)

    assert isinstance(online_sale, OnlineSale)
    assert isinstance(online_sale, SalesTransaction)
    assert online_sale.get_channel() == "Online"
    print("Created:", online_sale.get_channel())


    # TEST 44: POLYMORPHISM

    print("\nTEST 44: Sale Channels")
    print("----------------------")

    sales = [in_store_sale, online_sale]

    for sale in sales:
        print("Sale channel:", sale.get_channel())

    assert [sale.get_channel() for sale in sales] == ["In-Store", "Online"]
    assert transaction.get_channel() == "Unspecified"


    # TEST 45: IN-STORE SALE UPDATES SHARED INVENTORY

    print("\nTEST 45: Record In-Store Sale")
    print("-----------------------------")

    in_store_sale.add_item(product, 1)
    sales_manager.record_sale(in_store_sale)

    assert inventory.get_stock(101) == 8
    assert sales_manager.get_sales_data(101) == [2, 1, 1]
    print("Mouse stock after in-store sale:", inventory.get_stock(101))


    # TEST 46: ONLINE SALE UPDATES THE SAME INVENTORY

    print("\nTEST 46: Record Online Sale")
    print("---------------------------")

    online_sale.add_item(product, 2)
    online_sale.add_item(mouse_pad, 1)
    sales_manager.record_sale(online_sale)

    assert inventory.get_stock(101) == 6
    assert inventory.get_stock(103) == 2
    assert sales_manager.get_sales_data(101) == [2, 1, 1, 2]
    assert sales_manager.get_sales_data(103) == [3, 2, 1]
    print("Mouse stock after online sale:", inventory.get_stock(101))
    print("Mouse Pad stock after online sale:", inventory.get_stock(103))
    print("Combined mouse sales history:", sales_manager.get_sales_data(101))


    # TEST 47: INVALID SALE TYPE

    print("\nTEST 47: Invalid Sale Type")
    print("--------------------------")

    try:
        SalesFactory.create_sale("phone", 1010, customer, staff)

    except ValueError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Invalid sale type was accepted.")


    # TEST 48: INVALID ONLINE SALE QUANTITY

    print("\nTEST 48: Invalid Online Quantity")
    print("--------------------------------")

    invalid_online_sale = SalesFactory.create_sale("online", 1011, customer, staff)

    try:
        invalid_online_sale.add_item(product, 0)

    except ValueError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Invalid online quantity was accepted.")


    # TEST 49: ONLINE SALE CANNOT EXCEED STOCK

    print("\nTEST 49: Online Stock Validation")
    print("--------------------------------")

    too_large_online_sale = SalesFactory.create_sale("online", 1012, customer, staff)
    too_large_online_sale.add_item(product, 7)

    try:
        sales_manager.record_sale(too_large_online_sale)

    except ValueError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Online sale exceeded stock.")

    assert inventory.get_stock(101) == 6
    assert sales_manager.get_sales_data(101) == [2, 1, 1, 2]


    # TEST 50: DUPLICATE ID ACROSS SALES CHANNELS

    print("\nTEST 50: Duplicate Sale Across Channels")
    print("----------------------------------------")

    duplicate_online_sale = SalesFactory.create_sale("online", 1008, customer, staff)
    duplicate_online_sale.add_item(product, 1)

    try:
        sales_manager.record_sale(duplicate_online_sale)

    except ValueError as error:
        print("Validation error:", error)

    else:
        raise AssertionError("Duplicate transaction ID across channels accepted.")

    assert inventory.get_stock(101) == 6
    assert inventory.get_stock(103) == 2

    # TEST 51: REGISTER A LOW-STOCK OBSERVER

    print("\nTEST 51: Attach Stock Observer")
    print("------------------------------")

    alert_inventory = Inventory(low_stock_limit=5)
    alert_inventory.add_category(category)
    alert_product = Product(201, "USB Hub", 14.99, category)
    alert_inventory.add_product(alert_product, 7)

    notifier = LowStockNotifier()
    alert_inventory.attach(notifier)
    alert_inventory.attach(notifier)  # Registering the same observer twice has no effect
    print("Low-stock observer attached successfully.")


    # TEST 52: NO ALERT ABOVE THE LOW-STOCK LIMIT

    print("\nTEST 52: Stock Above Limit")
    print("--------------------------")

    output = StringIO()
    with redirect_stdout(output):
        alert_inventory.update_stock(201, -1)

    assert alert_inventory.get_stock(201) == 6
    assert output.getvalue() == ""
    print("Stock is 6: no alert sent.")


    # TEST 53: ALERT WHEN STOCK REACHES THE LIMIT

    print("\nTEST 53: Low-Stock Alert")
    print("------------------------")

    output = StringIO()
    with redirect_stdout(output):
        alert_inventory.update_stock(201, -1)

    assert alert_inventory.get_stock(201) == 5
    assert output.getvalue().count("LOW STOCK ALERT") == 1
    assert "USB Hub (ID: 201)" in output.getvalue()
    print(output.getvalue().strip())


    # TEST 54: NO REPEATED ALERT WHILE STOCK REMAINS LOW

    print("\nTEST 54: No Repeated Alert")
    print("--------------------------")

    output = StringIO()
    with redirect_stdout(output):
        alert_inventory.update_stock(201, -1)

    assert alert_inventory.get_stock(201) == 4
    assert output.getvalue() == ""
    assert alert_product in alert_inventory.get_low_stock()
    print("Stock is 4: no duplicate alert sent.")


    # TEST 55: ALERT AGAIN AFTER RESTOCKING

    print("\nTEST 55: Alert After Restocking")
    print("--------------------------------")

    output = StringIO()
    with redirect_stdout(output):
        alert_inventory.update_stock(201, 4)  # 4 to 8
        alert_inventory.update_stock(201, -3)  # 8 to 5

    assert alert_inventory.get_stock(201) == 5
    assert output.getvalue().count("LOW STOCK ALERT") == 1
    print(output.getvalue().strip())


    # TEST 56: REJECT INVALID OBSERVER

    print("\nTEST 56: Invalid Observer")
    print("-------------------------")

    try:
        alert_inventory.attach("not an observer")
    except TypeError as error:
        print("Validation error:", error)
    else:
        raise AssertionError("Invalid observer was accepted.")


    # TEST 57: ONLINE SALE AUTOMATICALLY TRIGGERS ALERT

    print("\nTEST 57: Sale Triggers Low-Stock Alert")
    print("--------------------------------------")

    inventory.attach(LowStockNotifier())
    notification_sale = SalesFactory.create_sale("online", 1013, customer, staff)
    notification_sale.add_item(product, 1)

    output = StringIO()
    with redirect_stdout(output):
        sales_manager.record_sale(notification_sale)

    assert inventory.get_stock(101) == 5
    assert sales_manager.get_sales_data(101) == [2, 1, 1, 2, 1]
    assert "Gaming Mouse Pro (ID: 101)" in output.getvalue()
    assert output.getvalue().count("LOW STOCK ALERT") == 1
    print(output.getvalue().strip())
    print("Mouse stock after sale:", inventory.get_stock(101))


    # TEST 58: MULTIPLE OBSERVERS RECEIVE NOTIFICATIONS

    print("\nTEST 58: Multiple Observers")
    print("---------------------------")

    alert_inventory.attach(LowStockNotifier())
    output = StringIO()
    with redirect_stdout(output):
        alert_inventory.update_stock(201, 2)  # 5 to 7
        alert_inventory.update_stock(201, -2)  # 7 to 5

    assert output.getvalue().count("LOW STOCK ALERT") == 2
    print("Both registered observers received the alert.")


    print("\nTesting completed.")


if __name__ == "__main__":
    main()

