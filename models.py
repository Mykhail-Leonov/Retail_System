

# Category class

class Category:
    def __init__(self, category_id: int, name: str):
        self.__category_id = category_id
        self.__name = name




# Product class


class Product:

    def __init__(self, product_id: int, name: str,
                 price: float, category: Category):

        # Validate product info
        if not isinstance(product_id, int) or product_id <= 0:
            raise ValueError("Product ID must be a positive number.")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Product name cannot be empty.")

        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError("Product price cannot be negative.")

        if not isinstance(category, Category):
            raise TypeError("A valid Category is required.")

        # Store product info
        self.__product_id = product_id
        self.__name = name.strip()
        self.__price = float(price)
        self.__category = category

    # Return price
    def get_price(self) -> float:
        return self.__price

    # Update product name and price
    def update_details(self, name: str, price: float) -> None:

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Product name cannot be empty.")

        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError("Product price cannot be negative.")

        self.__name = name.strip()
        self.__price = float(price)
