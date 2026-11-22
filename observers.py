from abc import ABC, abstractmethod
from models import Product


# Interface for objects that receive stock notifications
class StockObserver(ABC):

    @abstractmethod
    def update(self, product: Product, channel: str = "in_store") -> None:
        pass


# Shows alert when product becomes low on stock
class LowStockNotifier(StockObserver):

    def update(self, product: Product, channel: str = "in_store") -> None:
        print("LOW STOCK ALERT: " + product.get_name() +
              " (ID: " + str(product.get_id()) + ") needs restocking (" +
              channel.replace("_", "-") + ").")
