
from datetime import datetime
from models import Product, Customer, User


# A product and its quantity in a sale
class SaleItem:

    def __init__(self, product: Product, quantity: int):

        if not isinstance(product, Product):
            raise TypeError("A valid Product is required.")

        if type(quantity) is not int or quantity <= 0:
            raise ValueError("Sale quantity must be a positive integer.")

        self.__product = product
        self.__quantity = quantity
        self.__unit_price = product.get_price()

    # Calculate the cost for this item
    def line_total(self) -> float:
        return self.__quantity * self.__unit_price


# A sale containing one or more SaleItem objects
class SalesTransaction:

    def __init__(self, transaction_id: int, customer: Customer, user: User):

        if not isinstance(transaction_id, int) or transaction_id <= 0:
            raise ValueError("Transaction ID must be a positive integer.")

        if not isinstance(customer, Customer):
            raise TypeError("A valid Customer is required.")

        if not isinstance(user, User):
            raise TypeError("A valid User is required.")

        self.__transaction_id = transaction_id
        self.__customer = customer
        self.__user = user
        self.__date = datetime.now()
        self.__items = []

    # Create and add a SaleItem to this transaction
    def add_item(self, product: Product, quantity: int) -> None:
        item = SaleItem(product, quantity)
        self.__items.append(item)

    # Calculate the cost of the entire transaction
    def calculate_total(self) -> float:
        total = 0.0

        for item in self.__items:
            total += item.line_total()

        return total
