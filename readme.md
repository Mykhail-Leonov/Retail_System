
# Smart Retail Analytics and Inventory Management System

This project is a Python retail management system. It allows users to manage products, inventory and sales for both in-store and online shopping.

## Description

The Smart Retail system is built with Python and Object-Oriented Programming (OOP). It has a Tkinter interface with separate tabs for managing categories, products, inventory, sales, reports and demand prediction.

The system keeps track of in-store and online stock separately, while managing everything within the same inventory. It also allows users to record sales, update stock automatically and generate detailed reports.

A machine learning component was also added using Decision Tree models to predict Low, Medium or High demand for in-store and online sales based on historical data.

**Note:** Products, inventory and recorded transactions are currently stored in memory. This means they reset every time the application is closed. Demand predictions use the separate historical CSV file.

## System Features

- Add, update, remove and search products.
- Manage product categories.
- Search products by name or ID, including partial-name matching.
- Keep separate in-store and online stock for each product.
- Increase or decrease stock quantities.
- Low-stock notifications when stock reaches 5 units or fewer.
- Record in-store and online sales with multiple products.
- Automatically update the correct stock when a sale is recorded.
- View detailed inventory reports with categories, prices and stock quantities.
- View sales reports with customer details, products, quantities and prices.
- Filter sales reports by date, month and sales channel.
- View sales history for individual products.
- Predict Low, Medium or High demand up to 12 months ahead.
- Input validation and error handling.
- Tkinter interface for accessing all system features.

## Technologies Used

### Programming Language
- Python 3.8

### User Interface
- Tkinter (Desktop GUI)

### Data Processing and Machine Learning
- Pandas (Loading and cleaning sales data)
- NumPy (Numerical operations)
- Scikit-learn (Decision Tree classification)
- Joblib (Saving and loading trained models)

### Programming Concepts
- Encapsulation
- Inheritance
- Polymorphism
- Composition
- Factory Design Pattern
- Observer Design Pattern

### Testing
- Python unittest

### Version Control
- Git & GitHub

## Getting Started

### Dependencies

Ensure that you have installed:

- Python 3.8
- pip (Python package manager)
- Tkinter (Included with the standard Python installation on Windows)

### Installing

1. Clone or download the project repository.

2. Open the project folder in Visual Studio or another Python IDE.

3. Open the terminal and navigate to the project directory.

5. In the terminal, set up virtual environment:
    - python -m venv venv //Creates a virtual environment within directory
    - venv\Scripts\activate //Activating ensures all pip installs go into your local venv, not your global system Python.

6. Install required dependencies:
    - pip install -r requirements.txt

### Executing Program

1. Run the main application:
    - python main.py

2. The Smart Retail window will open with the tabs:
   - Categories
   - Products
   - Inventory
   - Sales
   - Reports
   - Prediction

3. Start by adding categories and products.

4. Use the Inventory tab to manage stock for in-store and online sales.

5. Use the Sales tab to record transactions. Stock will update automatically.

6. Use the Reports tab to view inventory and sales information.

7. Use the Prediction tab to predict future product demand.

### Machine Learning

The demand prediction system uses historical sales data from `smart_retail_sales.csv`.

Two Decision Tree models are used to predict in-store and online demand. The models use info such as the latest sales quantities and average sales over the last 3 and 12 months.

The trained models are saved in `retail_demand_models.joblib`.

If the saved model is missing or needs to be trained again, run:

- python train_prediction_model.py

The prediction system uses only historical data from csv. New sales recorded in the app do not affect it.

### Running Tests

The project aslo has unit tests for products, inventory, sales and demand prediction.

To run the tests:

- python unit_testing.py -v

The tests check valid and invalid inputs, stock management, sales transactions, reports and functionality of prediction.

## Version History

- **22 November 2026**
  - Improved inventory, sales reports and demand prediction.
  - Added full Tkinter interface and readme.md.

- **16 November 2026**
  - Added unit tests.

- **15 November 2026**
  - Improved demand prediction with averages of yearly sales.
  - Added demand prediction GUI.

- **14 November 2026**
  - Added demand prediction service.

- **13 November 2026**
  - Trained and evaluated demand prediction models.

- **11 November 2026**
  - Prepared historical sales data for demand prediction.
  - Implemented historical sales data loading and cleaning.

- **10 November 2026**
  - Implemented combined sales reporting.

- **2 November 2026**
  - Implemented main menu.

- **1 November 2026**
  - Implemented Observer Pattern for low-stock notifications.

- **31 October 2026**
  - Implemented in-store and online sales using Factory Pattern.
  - Implemented SalesManager and stock integration.

- **30 October 2026**
  - Implemented sales transactions.

- **29 October 2026**
  - Completed inventory management.

- **27 October 2026**
  - Implemented basic inventory and stock management.

- **26 October 2026**
  - Added User, Staff and Manager classes.
  - Added Product class.
  - Initial project setup.

## Acknowledgments

The template for readme.md was taken from DomPizzie (https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc)

The dataset with historical sales was generated by ChatGPT (2026)
