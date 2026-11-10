
from datetime import datetime
from typing import List
from models import Product, Customer, User
from inventory import Inventory


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

    # Return the product in this sale item
    def get_product(self) -> Product:
        return self.__product

    # Return the sold quantity
    def get_quantity(self) -> int:
        return self.__quantity

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
        self.__recorded = False

    # Return transaction ID
    def get_id(self) -> int:
        return self.__transaction_id

    # Return the date of the transaction
    def get_date(self) -> datetime:
        return self.__date

    # Identify the type of transaction
    def get_channel(self) -> str:
        return "Unspecified"

    # Return a copy of the sale items list
    def get_items(self) -> List[SaleItem]:
        return self.__items.copy()

    # Check if the sale was already recorded
    def is_recorded(self) -> bool:
        return self.__recorded

    # Mark successfull transaction as recorded
    def mark_recorded(self) -> None:
        self.__recorded = True

    # Create and add a SaleItem to this transaction
    def add_item(self, product: Product, quantity: int) -> None:
        if self.__recorded:
            raise ValueError("Cannot change a recorded sale.")

        item = SaleItem(product, quantity)
        self.__items.append(item)

    # Calculate the cost of the entire transaction
    def calculate_total(self) -> float:
        total = 0.0

        for item in self.__items:
            total += item.line_total()

        return total


# Sale recorded in a physical store
class InStoreSale(SalesTransaction):

    def get_channel(self) -> str:
        return "In-Store"


# Sale recorded through the online store
class OnlineSale(SalesTransaction):

    def get_channel(self) -> str:
        return "Online"


# Factory creates the appropriate type of sale
class SalesFactory:

    @staticmethod
    def create_sale(sale_type: str, transaction_id: int,
                    customer: Customer, user: User) -> SalesTransaction:

        if not isinstance(sale_type, str):
            raise ValueError("Sale type must be 'in_store' or 'online'.")

        sale_type = sale_type.strip().lower()

        if sale_type == "in_store":
            return InStoreSale(transaction_id, customer, user)

        if sale_type == "online":
            return OnlineSale(transaction_id, customer, user)

        raise ValueError("Sale type must be 'in_store' or 'online'.")


# Manage sales history and shared inventory
class SalesManager:

    def __init__(self, inventory: Inventory):
        if not isinstance(inventory, Inventory):
            raise TypeError("A valid Inventory is required.")

        self.__inventory = inventory
        self.__transactions = []

    # Record a sale and decrease the shared stock
    def record_sale(self, transaction: SalesTransaction) -> None:
        if not isinstance(transaction, SalesTransaction):
            raise TypeError("A valid SalesTransaction is required.")

        if transaction.is_recorded():
            raise ValueError("Sale has already been recorded.")

        for existing in self.__transactions:
            if existing.get_id() == transaction.get_id():
                raise ValueError("Transaction ID already exists.")

        items = transaction.get_items()
        if not items:
            raise ValueError("Cannot record an empty sale.")

        # Add quantities together if a product appears more than once
        quantities = {}
        for item in items:
            product_id = item.get_product().get_id()
            quantities[product_id] = quantities.get(product_id, 0) + item.get_quantity()

        # Check all products before changing any stock
        for product_id, quantity in quantities.items():
            if self.__inventory.get_stock(product_id) < quantity:
                raise ValueError("Not enough stock for product ID " + str(product_id) + ".")

        # Only record the transaction after the stock checks pass
        for product_id, quantity in quantities.items():
            self.__inventory.update_stock(product_id, -quantity)

        transaction.mark_recorded()
        self.__transactions.append(transaction)

    # Return quantities sold in each recorded sale for a product
    def get_sales_data(self, product_id: int) -> List[int]:
        quantities = []

        for transaction in self.__transactions:
            total_quantity = 0

            for item in transaction.get_items():
                if item.get_product().get_id() == product_id:
                    total_quantity += item.get_quantity()

            if total_quantity > 0:
                quantities.append(total_quantity)

        return quantities

    # Generate a combined report of recorded sales
    def sales_report(self) -> str:
        report = "SALES REPORT\n------------\n"

        if not self.__transactions:
            return report + "No sales recorded."

        total_revenue = 0.0
        total_units = 0

        for transaction in self.__transactions:
            sale_total = transaction.calculate_total()
            total_revenue += sale_total

            for item in transaction.get_items():
                total_units += item.get_quantity()

            report += (
                f"ID: {transaction.get_id()} | "
                f"Date: {transaction.get_date().strftime('%Y-%m-%d')} | "
                f"Channel: {transaction.get_channel()} | "
                f"Total: {sale_total:.2f}\n"
            )

        report += (
            f"\nTotal transactions: {len(self.__transactions)}\n"
            f"Total units sold: {total_units}\n"
            f"Total revenue: {total_revenue:.2f}"
        )

        return report
