from datetime import date, timedelta
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


# Let the user pick a match if more than one exists
def choose_match(matches, name):
    if not matches:
        raise KeyError("No matching {} found.".format(name))
    if len(matches) == 1:
        return matches[0]

    print("Matching {}:".format(name))
    for number, item in enumerate(matches, 1):
        print("{}. {} (ID: {})".format(number, item.get_name(), item.get_id()))

    selection = int(input("Choose number: "))
    if selection < 1 or selection > len(matches):
        raise ValueError("Invalid selection.")
    return matches[selection - 1]


# Find a product by name or ID
def choose_product(inventory, prompt="Product name (or ID): "):
    query = input(prompt).strip()
    if not query:
        raise ValueError("Enter a product name or ID.")

    if query.isdigit():
        return inventory.get_product(int(query))

    matches = inventory.search_product(query)
    exact = [product for product in matches if product.get_name().lower() == query.lower()]
    return choose_match(exact if len(exact) == 1 else matches, "products")


# Find a category by name or ID
def choose_category(inventory, prompt="Category name (or ID): "):
    query = input(prompt).strip()
    if not query:
        raise ValueError("Enter a category name or ID.")

    if query.isdigit():
        return inventory.get_category(int(query))

    matches = inventory.search_category(query)
    exact = [category for category in matches if category.get_name().lower() == query.lower()]
    return choose_match(exact if len(exact) == 1 else matches, "categories")


# Get date and channel filters for the report
def choose_report_filters():
    print("Period: 1. All  2. Today  3. This week  4. Month  5. Exact date  6. Date range")
    period = input("Choose period (1-6): ").strip()
    today = date.today()
    start = None
    end = None

    if period == "1":
        pass
    elif period == "2":
        start = end = today
    elif period == "3":
        start = today - timedelta(days=today.weekday())
        end = today
    elif period == "4":
        year = int(input("Year: "))
        month = int(input("Month (1-12): "))
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)
    elif period == "5":
        start = end = date.fromisoformat(input("Date (YYYY-MM-DD): ").strip())
    elif period == "6":
        start = date.fromisoformat(input("Start date (YYYY-MM-DD): ").strip())
        end = date.fromisoformat(input("End date (YYYY-MM-DD): ").strip())
    else:
        raise ValueError("Choose a period from 1 to 6.")

    channel = input("Channel (both/in_store/online): ").strip().lower()
    if channel == "both":
        channel = None
    elif channel not in ("in_store", "online"):
        raise ValueError("Choose both, in_store or online.")
    return start, end, channel


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
                category = choose_category(inventory)
                name = input("New category name: ")
                category.update_name(name)
                print("Category updated successfully.")

            elif choice == "3":
                category = choose_category(inventory)
                inventory.remove_category(category.get_id())
                print("Category removed successfully.")

            elif choice == "4":
                product_id = int(input("Product ID: "))
                name = input("Product name: ")
                price = float(input("Product price: "))
                category = choose_category(inventory)
                store_quantity = int(input("Starting in-store stock: "))
                online_quantity = int(input("Starting online stock: "))
                product = Product(product_id, name, price, category)
                inventory.add_product(product, store_quantity, online_quantity)
                print("Product added successfully.")

            elif choice == "5":
                product = choose_product(inventory)
                name = input("New product name: ")
                price = float(input("New product price: "))
                inventory.update_product(product.get_id(), name, price)
                print("Product updated successfully.")

            elif choice == "6":
                product = choose_product(inventory)
                inventory.remove_product(product.get_id())
                print("Product removed successfully.")

            elif choice == "7":
                name = input("Search by product name: ")
                products = inventory.search_product(name)
                if not products:
                    print("No matching products found.")
                for product in products:
                    product_id = product.get_id()
                    print("ID: {} | Name: {} | Category: {} | Price: {:.2f} | In-store: {} | Online: {} | Stock: {}".format(
                        product_id, product.get_name(), product.get_category().get_name(),
                        product.get_price(), inventory.get_stock(product_id, "in_store"),
                        inventory.get_stock(product_id, "online"), inventory.get_stock(product_id)))

            elif choice == "8":
                product = choose_product(inventory)
                channel = input("Channel (in_store/online): ").strip().lower()
                change = int(input("Stock change (e.g. 5 or -2): "))
                inventory.update_stock(product.get_id(), change, channel)
                print("New {} stock: {} | Total: {}".format(
                    channel.replace("_", "-"), inventory.get_stock(product.get_id(), channel),
                    inventory.get_stock(product.get_id())))

            elif choice == "9":
                print(inventory.inventory_report())

            elif choice == "10":
                low_stock_products = inventory.get_low_stock()
                if not low_stock_products:
                    print("No low-stock products.")
                for product in low_stock_products:
                    product_id = product.get_id()
                    channels = inventory.get_low_stock_channels(product_id)
                    for channel in channels:
                        print("{} (ID: {}) - {}: {} remaining".format(
                            product.get_name(), product_id, channel.replace("_", "-"),
                            inventory.get_stock(product_id, channel)))

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
                    product = choose_product(inventory)
                    quantity = int(input("Quantity: "))
                    sale.add_item(product, quantity)

                sales_manager.record_sale(sale)
                print("{} sale recorded. Total: {:.2f}".format(
                    sale.get_channel(), sale.calculate_total()))

            elif choice == "12":
                product = choose_product(inventory)
                print("Sales history:", sales_manager.get_sales_data(product.get_id()))

            elif choice == "13":
                start, end, channel = choose_report_filters()
                print(sales_manager.sales_report(start, end, channel))

            elif choice == "14":
                launch_prediction_window()

            else:
                print("Invalid menu option.")

        except (ValueError, TypeError, KeyError) as error:
            print("Error:", error)


if __name__ == "__main__":
    main()
