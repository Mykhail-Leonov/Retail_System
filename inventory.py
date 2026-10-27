
from models import Product, Category


# Inventory class

class Inventory:

    def __init__(self, low_stock_limit: int = 5):

        if not isinstance(low_stock_limit, int) or low_stock_limit < 0:
            raise ValueError("Low stock limit cannot be negative.")

        # Store products, categories and stock quantities
        self.__products = []
        self.__categories = []
        self.__stock = {}

        
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
