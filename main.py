
from models import Category, Product, Customer, Staff
from inventory import Inventory
from sales import SalesManager, SalesFactory
from observers import LowStockNotifier
from prediction_gui import launch_prediction_window


# Show the options available to the user
def show_menu() -> None:
    print("\nSMART RETAIL MANAGEMENT SYSTEM")
    print("------------------------------")
    print("1. Add category")
    print("2. Rename category")
    print("3. Remove category")
    print("4. Add product")
    print("5. Update product")
    print("6. Remove product")
    print("7. Search products")
    print("8. Update stock")
    print("9. Inventory report")
    print("10. Low-stock products")
    print("11. Record sale")
    print("12. Product sales history")
    print("13. Combined sales report")
    print("14. Predict demand")
    print("0. Exit")


# Run the menu and connect the existing classes
def main() -> None:
    inventory = Inventory()
    inventory.attach(LowStockNotifier())
    sales_manager = SalesManager(inventory)
    staff = Staff(1, "Store Staff")  # Example user recording sales

    print("Welcome to the Smart Retail Management System!")

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Bye!")
            break

        try:
            if choice == "1":
                category_id = int(input("Category ID: "))
                name = input("Category name: ")
                inventory.add_category(Category(category_id, name))
                print("Category added successfully.")

            elif choice == "2":
                category_id = int(input("Category ID: "))
                name = input("New category name: ")
                inventory.get_category(category_id).update_name(name)
                print("Category updated successfully.")

            elif choice == "3":
                category_id = int(input("Category ID: "))
                inventory.remove_category(category_id)
                print("Category removed successfully.")

            elif choice == "4":
                product_id = int(input("Product ID: "))
                name = input("Product name: ")
                price = float(input("Product price: "))
                category_id = int(input("Category ID: "))
                quantity = int(input("Starting stock quantity: "))
                category = inventory.get_category(category_id)
                product = Product(product_id, name, price, category)
                inventory.add_product(product, quantity)
                print("Product added successfully.")

            elif choice == "5":
                product_id = int(input("Product ID: "))
                name = input("New product name: ")
                price = float(input("New product price: "))
                inventory.update_product(product_id, name, price)
                print("Product updated successfully.")

            elif choice == "6":
                product_id = int(input("Product ID: "))
                inventory.remove_product(product_id)
                print("Product removed successfully.")

            elif choice == "7":
                name = input("Search by product name: ")
                products = inventory.search_product(name)
                if not products:
                    print("No matching products found.")
                for product in products:
                    print("ID: {} | Name: {} | Price: {:.2f} | Stock: {}".format(
                        product.get_id(), product.get_name(),
                        product.get_price(), inventory.get_stock(product.get_id())))

            elif choice == "8":
                product_id = int(input("Product ID: "))
                change = int(input("Stock change (e.g. 5 or -2): "))
                inventory.update_stock(product_id, change)
                print("New stock:", inventory.get_stock(product_id))

            elif choice == "9":
                print(inventory.inventory_report())

            elif choice == "10":
                low_stock_products = inventory.get_low_stock()
                if not low_stock_products:
                    print("No low-stock products.")
                for product in low_stock_products:
                    print("{} (ID: {}) - {} remaining".format(
                        product.get_name(), product.get_id(),
                        inventory.get_stock(product.get_id())))

            elif choice == "11":
                sale_type = input("Sale type (in_store/online): ")
                transaction_id = int(input("Transaction ID: "))
                customer_id = int(input("Customer ID: "))
                customer_name = input("Customer name: ")
                item_count = int(input("Number of different items: "))
                if item_count <= 0:
                    raise ValueError("Sale must contain at least one item.")

                customer = Customer(customer_id, customer_name)
                sale = SalesFactory.create_sale(
                    sale_type, transaction_id, customer, staff)

                for number in range(item_count):
                    print("Item", number + 1)
                    product_id = int(input("Product ID: "))
                    quantity = int(input("Quantity: "))
                    product = inventory.get_product(product_id)
                    sale.add_item(product, quantity)

                sales_manager.record_sale(sale)
                print("{} sale recorded. Total: {:.2f}".format(
                    sale.get_channel(), sale.calculate_total()))

            elif choice == "12":
                product_id = int(input("Product ID: "))
                inventory.get_product(product_id)
                print("Sales history:", sales_manager.get_sales_data(product_id))

            elif choice == "13":
                print(sales_manager.sales_report())

            elif choice == "14":
                launch_prediction_window()

            else:
                print("Invalid menu option.")

        except (ValueError, TypeError, KeyError) as error:
            print("Error:", error)


if __name__ == "__main__":
    main()
