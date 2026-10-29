
from models import Category, Product, User, Staff, Manager
from inventory import Inventory


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

    print("\nTesting completed.")


if __name__ == "__main__":
    main()
