
from models import Category, Product, User, Staff, Manager


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

    print("\nTesting completed.")


if __name__ == "__main__":
    main()
