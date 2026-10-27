
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


    print("\nTesting completed.")


if __name__ == "__main__":
    main()
