from models import Product, Category
from typing import List
from observers import StockObserver

# Inventory class

class Inventory:

    CHANNELS = ("in_store", "online")

    def __init__(self, low_stock_limit: int = 5):

        if not isinstance(low_stock_limit, int) or low_stock_limit < 0:
            raise ValueError("Low stock limit cannot be negative.")

        # Store products, categories and stock quantities
        self.__products = []
        self.__categories = []
        self.__stock = {}

        # Low-stock notification settings
        self.__low_stock_limit = low_stock_limit
        self.__observers = []

    # Add a category to inventory
    def add_category(self, category: Category) -> None:

        if not isinstance(category, Category):
            raise TypeError("A valid Category is required.")

        # Check for duplicate category IDs
        for existing_category in self.__categories:
            if existing_category.get_id() == category.get_id():
                raise ValueError("Category ID already exists.")

        self.__categories.append(category)

    # Find a category using its ID
    def get_category(self, category_id: int) -> Category:
        for category in self.__categories:
            if category.get_id() == category_id:
                return category
        raise KeyError("Category not found.")

    # Add a product with separate stock for each channel
    def add_product(self, product: Product, quantity: int, online_quantity: int = 0) -> None:

        if not isinstance(product, Product):
            raise TypeError("A valid Product is required.")

        if type(quantity) is not int or quantity < 0:
            raise ValueError("In-store quantity must be a non-negative integer.")
        if type(online_quantity) is not int or online_quantity < 0:
            raise ValueError("Online quantity must be a non-negative integer.")

        # Check that the product category exists
        if product.get_category() not in self.__categories:
            raise ValueError("Product category must be added first.")

        # Check for duplicate product IDs
        for existing_product in self.__products:
            if existing_product.get_id() == product.get_id():
                raise ValueError("Product ID already exists.")

        self.__products.append(product)
        self.__stock[product.get_id()] = {
            "in_store": quantity,
            "online": online_quantity
        }

    # Find a product using its ID
    def get_product(self, product_id: int) -> Product:
        for product in self.__products:
            if product.get_id() == product_id:
                return product
        raise KeyError("Product not found in inventory.")

    # Get stock for one channel, or the combined total
    def get_stock(self, product_id: int, channel=None) -> int:

        if product_id not in self.__stock:
            raise KeyError("Product not found in inventory.")

        if channel is None:
            return sum(self.__stock[product_id].values())
        if channel not in self.CHANNELS:
            raise ValueError("Channel must be 'in_store' or 'online'.")
        return self.__stock[product_id][channel]

    # Increase or decrease stock in one channel
    def update_stock(self, product_id: int, change: int, channel: str = "in_store") -> None:

        if type(change) is not int:
            raise ValueError("Stock change must be an integer.")
        if channel not in self.CHANNELS:
            raise ValueError("Channel must be 'in_store' or 'online'.")

        current_stock = self.get_stock(product_id, channel)
        new_stock = current_stock + change

        if new_stock < 0:
            raise ValueError("Not enough {} stock available.".format(channel.replace("_", "-")))

        self.__stock[product_id][channel] = new_stock

        # Alert only when this channel reaches the low limit
        if change < 0 and current_stock > self.__low_stock_limit and new_stock <= self.__low_stock_limit:
            self.notify_observers(self.get_product(product_id), channel)

    # Attach an observer to receive low stock alerts
    def attach(self, observer: StockObserver) -> None:

        if not isinstance(observer, StockObserver):
            raise TypeError("A valid StockObserver is required.")

        if observer not in self.__observers:
            self.__observers.append(observer)

    # Tell all observers which channel is low
    def notify_observers(self, product: Product, channel: str = "in_store") -> None:
        for observer in self.__observers:
            observer.update(product, channel)

    # Remove a category if no products use it
    def remove_category(self, category_id: int) -> None:

        for product in self.__products:
            if product.get_category().get_id() == category_id:
                raise ValueError("Cannot remove a category that has products.")

        for category in self.__categories:
            if category.get_id() == category_id:
                self.__categories.remove(category)
                return

        raise KeyError("Category not found.")

    # Update product name and price
    def update_product(self, product_id: int, name: str, price: float) -> None:

        for product in self.__products:
            if product.get_id() == product_id:
                product.update_details(name, price)
                return

        raise KeyError("Product not found in inventory.")

    # Remove a product and its stock record
    def remove_product(self, product_id: int) -> None:

        for product in self.__products:
            if product.get_id() == product_id:
                self.__products.remove(product)
                del self.__stock[product_id]
                return

        raise KeyError("Product not found in inventory.")

    # Search products by name
    def search_product(self, name: str) -> List[Product]:

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Search name cannot be empty.")

        matches = []
        for product in self.__products:
            if name.strip().lower() in product.get_name().lower():
                matches.append(product)
        return matches

    # Check which channels need restocking
    def get_low_stock_channels(self, product_id: int) -> List[str]:
        return [channel for channel in self.CHANNELS
                if self.get_stock(product_id, channel) <= self.__low_stock_limit]

    # Search categories by name
    def search_category(self, name: str) -> List[Category]:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Search name cannot be empty.")
        return [category for category in self.__categories
                if name.strip().lower() in category.get_name().lower()]

    # Find products with low stock in either channel
    def get_low_stock(self) -> List[Product]:
        return [product for product in self.__products
                if self.get_low_stock_channels(product.get_id())]

    # Generate a detailed inventory report
    def inventory_report(self) -> str:
        report = "INVENTORY REPORT\n----------------\n"

        category_list = ", ".join("{} (ID: {})".format(category.get_name(), category.get_id())
                                  for category in self.__categories) or "None"
        if not self.__products:
            return report + "No products in inventory.\nCategories: " + category_list

        store_total = 0
        online_total = 0
        stock_value = 0.0

        for product in self.__products:
            product_id = product.get_id()
            store = self.get_stock(product_id, "in_store")
            online = self.get_stock(product_id, "online")
            total = store + online
            value = total * product.get_price()
            low_channels = self.get_low_stock_channels(product_id)
            low_status = ", ".join(channel.replace("_", "-") for channel in low_channels) if low_channels else "None"

            store_total += store
            online_total += online
            stock_value += value

            report += (
                f"ID: {product_id} | "
                f"Name: {product.get_name()} | "
                f"Category: {product.get_category().get_name()} | "
                f"Price: {product.get_price():.2f} | "
                f"In-store: {store} | Online: {online} | Stock: {total} | "
                f"Stock value: {value:.2f} | Low stock: {low_status}\n"
            )

        report += (
            f"\nProducts: {len(self.__products)} | Categories: {len(self.__categories)}\n"
            f"Category list: {category_list}\n"
            f"Total in-store stock: {store_total}\n"
            f"Total online stock: {online_total}\n"
            f"Total stock: {store_total + online_total}\n"
            f"Total stock value: {stock_value:.2f}"
        )
        return report
