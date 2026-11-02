
from models import Product, Category
from typing import List
from observers import StockObserver

# Inventory class

class Inventory:

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


    # Add a product with its starting stock quantity
    def add_product(self, product: Product, quantity: int) -> None:

        if not isinstance(product, Product):
            raise TypeError("A valid Product is required.")

        if type(quantity) is not int or quantity < 0:
            raise ValueError("Stock quantity must be a non-negative integer.")

        # Check that the product category exists
        if product.get_category() not in self.__categories:
            raise ValueError("Product category must be added first.")

        # Check for duplicate product IDs
        for existing_product in self.__products:
            if existing_product.get_id() == product.get_id():
                raise ValueError("Product ID already exists.")

        self.__products.append(product)
        self.__stock[product.get_id()] = quantity

    
    # Find a product using its ID
    def get_product(self, product_id: int) -> Product:
        for product in self.__products:
            if product.get_id() == product_id:
                return product
        raise KeyError("Product not found in inventory.")


    # Return stock quantity for a product
    def get_stock(self, product_id: int) -> int:

        if product_id not in self.__stock:
            raise KeyError("Product not found in inventory.")

        return self.__stock[product_id]

    # Increase or decrease stock quantity
    def update_stock(self, product_id: int, change: int) -> None:

        if type(change) is not int:
            raise ValueError("Stock change must be an integer.")

        current_stock = self.get_stock(product_id)
        new_stock = current_stock + change

        if new_stock < 0:
            raise ValueError("Not enough stock available.")

        self.__stock[product_id] = new_stock

        # Notify observers when stock gets to the low-stock range
        if change < 0 and current_stock > self.__low_stock_limit and new_stock <= self.__low_stock_limit:
            for product in self.__products:
                if product.get_id() == product_id:
                    self.notify_observers(product)
                    break

    # Attach an observer to receive low stock alerts
    def attach(self, observer: StockObserver) -> None:

        if not isinstance(observer, StockObserver):
            raise TypeError("A valid StockObserver is required.")

        if observer not in self.__observers:
            self.__observers.append(observer)

    # Tell all registered observers which product is low stock
    def notify_observers(self, product: Product) -> None:

        for observer in self.__observers:
            observer.update(product)

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

    # Find products at or below low-stock limit
    def get_low_stock(self) -> List[Product]:

        low_stock_products = []

        for product in self.__products:
            if self.get_stock(product.get_id()) <= self.__low_stock_limit:
                low_stock_products.append(product)

        return low_stock_products

    # Generate a simple report
    def inventory_report(self) -> str:

        report = "INVENTORY REPORT\n----------------\n"

        if not self.__products:
            return report + "No products in inventory."

        for product in self.__products:
            report += (
                f"ID: {product.get_id()} | "
                f"Name: {product.get_name()} | "
                f"Price: {product.get_price():.2f} | "
                f"Stock: {self.get_stock(product.get_id())}\n"
            )

        return report.rstrip()
