
from datetime import datetime, date
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
        self.__product_name = product.get_name()

    # Return the product in this sale item
    def get_product(self) -> Product:
        return self.__product

    # Return the sold quantity
    def get_quantity(self) -> int:
        return self.__quantity

    # Keep the original product name and price in the report
    def get_product_name(self) -> str:
        return self.__product_name

    def get_unit_price(self) -> float:
        return self.__unit_price

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

    # Return the customer for the sales report
    def get_customer(self) -> Customer:
        return self.__customer

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

        # Pick the stock channel for this sale
        if transaction.get_channel() == "Online":
            channel = "online"
        elif transaction.get_channel() in ("In-Store", "Unspecified"):
            channel = "in_store"
        else:
            raise ValueError("Unknown sales channel.")

        # Check this channel before changing any stock
        for product_id, quantity in quantities.items():
            if self.__inventory.get_stock(product_id, channel) < quantity:
                raise ValueError("Not enough " + channel.replace("_", "-") +
                                 " stock for product ID " + str(product_id) + ".")

        # Only record the transaction after all checks pass
        for product_id, quantity in quantities.items():
            self.__inventory.update_stock(product_id, -quantity, channel)

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

    # Convert a date filter to a date value
    def __report_date(self, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                pass
        raise ValueError("Enter a valid date in YYYY-MM-DD format.")

    # Generate a combined report, with optional filters
    def sales_report(self, start_date=None, end_date=None, channel=None) -> str:
        start_date = self.__report_date(start_date)
        end_date = self.__report_date(end_date)
        if start_date and end_date and start_date > end_date:
            raise ValueError("Start date cannot be after end date.")
        if channel not in (None, "in_store", "online"):
            raise ValueError("Channel must be 'in_store' or 'online'.")

        report = "SALES REPORT\n------------\n"
        if start_date or end_date:
            report += "Period: {} to {}\n".format(
                start_date.isoformat() if start_date else "Start",
                end_date.isoformat() if end_date else "Today"
            )
        else:
            report += "Period: All recorded sales\n"
        report += "Filter: {}\n".format(channel.replace("_", "-") if channel else "Both channels")

        selected = []
        for transaction in self.__transactions:
            transaction_date = transaction.get_date().date()
            transaction_channel = "online" if transaction.get_channel() == "Online" else "in_store"
            if start_date and transaction_date < start_date:
                continue
            if end_date and transaction_date > end_date:
                continue
            if channel and channel != transaction_channel:
                continue
            selected.append(transaction)

        if not selected:
            return report + "No sales recorded for the selected period."

        total_revenue = 0.0
        total_units = 0
        channel_revenue = {"in_store": 0.0, "online": 0.0}
        channel_units = {"in_store": 0, "online": 0}
        channel_transactions = {"in_store": 0, "online": 0}

        for transaction in selected:
            sale_total = transaction.calculate_total()
            sales_channel = "online" if transaction.get_channel() == "Online" else "in_store"
            total_revenue += sale_total
            channel_revenue[sales_channel] += sale_total
            channel_transactions[sales_channel] += 1

            for item in transaction.get_items():
                quantity = item.get_quantity()
                total_units += quantity
                channel_units[sales_channel] += quantity

            customer = transaction.get_customer()
            report += (
                f"\nID: {transaction.get_id()} | "
                f"Date: {transaction.get_date().strftime('%Y-%m-%d %H:%M:%S')} | "
                f"Channel: {transaction.get_channel()}\n"
                f"Customer: {customer.get_name()} (ID: {customer.get_id()})\n"
                "Items:\n"
            )
            for item in transaction.get_items():
                report += (
                    f"  Product ID: {item.get_product().get_id()} | "
                    f"Name: {item.get_product_name()} | "
                    f"Quantity: {item.get_quantity()} | "
                    f"Unit price: {item.get_unit_price():.2f} | "
                    f"Line total: {item.line_total():.2f}\n"
                )
            report += f"Transaction total: {sale_total:.2f}\n"

        report += (
            f"\nTotal transactions: {len(selected)}\n"
            f"Total units sold: {total_units}\n"
            f"Total revenue: {total_revenue:.2f}\n"
            f"In-store: {channel_transactions['in_store']} transactions, "
            f"{channel_units['in_store']} units, {channel_revenue['in_store']:.2f} revenue\n"
            f"Online: {channel_transactions['online']} transactions, "
            f"{channel_units['online']} units, {channel_revenue['online']:.2f} revenue"
        )
        return report
