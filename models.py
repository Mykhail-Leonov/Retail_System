

# Category class

class Category:

    def __init__(self, category_id: int, name: str):

        # Validate category info
        if not isinstance(category_id, int) or category_id <= 0:
            raise ValueError("Category ID must be a positive integer.")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Category name cannot be empty.")

        # Store category info
        self.__category_id = category_id
        self.__name = name.strip()

    def get_id(self) -> int:
        return self.__category_id

    # Update category name
    def update_name(self, name: str) -> None:

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Category name cannot be empty.")

        self.__name = name.strip()





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

    # Return product ID
    def get_id(self) -> int:
        return self.__product_id

    # Return product category
    def get_category(self) -> Category:
        return self.__category

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


# User class

class User:

    def __init__(self, user_id: int, name: str):

        # Validate user info
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive number.")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("User name cannot be empty.")

        # Store user info
        self.__user_id = user_id
        self.__name = name.strip()

    # Return the user role
    def get_role(self) -> str:
        return "User"

    # Check inventory management permission
    def can_manage_inventory(self) -> bool:
        return False


# Staff class

class Staff(User):

    def get_role(self) -> str:
        return "Staff"

    def can_manage_inventory(self) -> bool:
        return False


# Manager class

class Manager(User):

    def get_role(self) -> str:
        return "Manager"

    def can_manage_inventory(self) -> bool:
        return True
