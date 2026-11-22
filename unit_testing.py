import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import date, timedelta
from unittest.mock import patch

from models import Category, Product, Customer, Staff
from inventory import Inventory
from sales import SalesTransaction, SalesManager, SalesFactory, InStoreSale, OnlineSale
from observers import LowStockNotifier
from prediction_data import FEATURE_COLUMNS, VALID_LABELS, load_sales_data, clean_sales_data, build_features
from prediction_service import DemandPredictionService
from main import choose_product


class TestProducts(unittest.TestCase):

    def setUp(self):
        self.category = Category(1, "Electronics")
        self.product = Product(101, "Wireless Mouse", 19.99, self.category)
        self.inventory = Inventory()
        self.inventory.add_category(self.category)
        self.inventory.add_product(self.product, 10, 10)

    def test_product_created(self):
        self.assertEqual(self.product.get_id(), 101)
        self.assertEqual(self.product.get_name(), "Wireless Mouse")
        self.assertEqual(self.product.get_price(), 19.99)
        self.assertIs(self.product.get_category(), self.category)

    def test_invalid_product_details(self):
        with self.assertRaises(ValueError):
            Product(102, "", 10, self.category)
        with self.assertRaises(ValueError):
            Product(102, "Keyboard", -1, self.category)

    def test_update_product(self):
        self.inventory.update_product(101, "Gaming Mouse", 24.99)
        self.assertEqual(self.product.get_name(), "Gaming Mouse")
        self.assertEqual(self.product.get_price(), 24.99)

    def test_search_ignores_capitals(self):
        result = self.inventory.search_product("MOUSE")
        self.assertEqual(result, [self.product])

    def test_empty_search_rejected(self):
        with self.assertRaises(ValueError):
            self.inventory.search_product("   ")

    def test_duplicate_product_rejected(self):
        another = Product(101, "Keyboard", 35, self.category)
        with self.assertRaises(ValueError):
            self.inventory.add_product(another, 5)
    def test_name_search_with_multiple_matches(self):
        pad = Product(103, "Mouse Pad", 5, self.category)
        self.inventory.add_product(pad, 3, 3)
        with patch("builtins.input", side_effect=["mouse", "2"]), redirect_stdout(StringIO()):
            result = choose_product(self.inventory)
        self.assertIs(result, pad)



class TestInventory(unittest.TestCase):

    def setUp(self):
        self.category = Category(1, "Electronics")
        self.product = Product(101, "Wireless Mouse", 19.99, self.category)
        self.inventory = Inventory(low_stock_limit=5)
        self.inventory.add_category(self.category)
        self.inventory.add_product(self.product, 10, 10)

    def test_stock_goes_up_and_down(self):
        self.inventory.update_stock(101, -3)
        self.inventory.update_stock(101, 5)
        self.assertEqual(self.inventory.get_stock(101, "in_store"), 12)

    def test_cannot_sell_more_than_stock(self):
        with self.assertRaises(ValueError):
            self.inventory.update_stock(101, -11)
        self.assertEqual(self.inventory.get_stock(101, "in_store"), 10)

    def test_negative_starting_stock_rejected(self):
        extra = Product(102, "Keyboard", 30, self.category)
        with self.assertRaises(ValueError):
            self.inventory.add_product(extra, -1)

    def test_unknown_product_rejected(self):
        with self.assertRaises(KeyError):
            self.inventory.get_stock(999)

    def test_low_stock_boundary(self):
        self.inventory.update_stock(101, -4)
        self.assertNotIn(self.product, self.inventory.get_low_stock())

        self.inventory.update_stock(101, -1)
        self.assertIn(self.product, self.inventory.get_low_stock())

    def test_stock_alert_only_on_crossing_limit(self):
        self.inventory.attach(LowStockNotifier())
        output = StringIO()
        with redirect_stdout(output):
            self.inventory.update_stock(101, -5)  # 10 to 5
            self.inventory.update_stock(101, -1)  # 5 to 4
            self.inventory.update_stock(101, 4)   # 4 to 8
            self.inventory.update_stock(101, -3)  # 8 to 5

        self.assertEqual(output.getvalue().count("LOW STOCK ALERT"), 2)

    def test_cannot_remove_category_in_use(self):
        with self.assertRaises(ValueError):
            self.inventory.remove_category(1)
    def test_separate_stock_and_inventory_report(self):
        self.inventory.update_stock(101, -3, "online")
        self.assertEqual(self.inventory.get_stock(101, "in_store"), 10)
        self.assertEqual(self.inventory.get_stock(101, "online"), 7)
        self.assertEqual(self.inventory.get_stock(101), 17)
        report = self.inventory.inventory_report()
        self.assertIn("Category: Electronics", report)
        self.assertIn("In-store: 10 | Online: 7 | Stock: 17", report)
        self.assertIn("Total stock: 17", report)

    def test_online_low_stock_alert(self):
        self.inventory.attach(LowStockNotifier())
        output = StringIO()
        with redirect_stdout(output):
            self.inventory.update_stock(101, -5, "online")
        self.assertIn("online", output.getvalue())
        self.assertEqual(self.inventory.get_low_stock_channels(101), ["online"])



class TestSales(unittest.TestCase):

    def setUp(self):
        category = Category(1, "Electronics")
        self.mouse = Product(101, "Mouse", 20, category)
        self.keyboard = Product(102, "Keyboard", 30, category)
        self.inventory = Inventory()
        self.inventory.add_category(category)
        self.inventory.add_product(self.mouse, 10, 6)
        self.inventory.add_product(self.keyboard, 5, 5)
        self.customer = Customer(1, "Jordan")
        self.staff = Staff(1, "Alex")
        self.manager = SalesManager(self.inventory)

    def test_sale_total_keeps_original_price(self):
        sale = SalesTransaction(1, self.customer, self.staff)
        sale.add_item(self.mouse, 2)
        sale.add_item(self.keyboard, 1)
        self.mouse.update_details("Mouse", 50)
        self.assertEqual(sale.calculate_total(), 70)

    def test_invalid_sale_quantity(self):
        sale = SalesTransaction(1, self.customer, self.staff)
        with self.assertRaises(ValueError):
            sale.add_item(self.mouse, 0)

    def test_factory_creates_correct_sales(self):
        store = SalesFactory.create_sale("in_store", 1, self.customer, self.staff)
        online = SalesFactory.create_sale("online", 2, self.customer, self.staff)
        self.assertIsInstance(store, InStoreSale)
        self.assertIsInstance(online, OnlineSale)
        with self.assertRaises(ValueError):
            SalesFactory.create_sale("phone", 3, self.customer, self.staff)

    def test_both_channels_share_stock(self):
        store = SalesFactory.create_sale("in_store", 1, self.customer, self.staff)
        store.add_item(self.mouse, 2)
        self.manager.record_sale(store)

        online = SalesFactory.create_sale("online", 2, self.customer, self.staff)
        online.add_item(self.mouse, 3)
        self.manager.record_sale(online)

        self.assertEqual(self.inventory.get_stock(101, "in_store"), 8)
        self.assertEqual(self.inventory.get_stock(101, "online"), 3)
        self.assertEqual(self.inventory.get_stock(101), 11)
        self.assertEqual(self.manager.get_sales_data(101), [2, 3])
        report = self.manager.sales_report()
        self.assertIn("Channel: In-Store", report)
        self.assertIn("Channel: Online", report)
        self.assertIn("Total transactions: 2", report)

    def test_empty_sale_rejected(self):
        sale = SalesTransaction(1, self.customer, self.staff)
        with self.assertRaises(ValueError):
            self.manager.record_sale(sale)
        self.assertEqual(self.inventory.get_stock(101, "in_store"), 10)

    def test_failed_sale_leaves_all_stock_unchanged(self):
        sale = SalesTransaction(1, self.customer, self.staff)
        sale.add_item(self.mouse, 2)
        sale.add_item(self.keyboard, 6)

        with self.assertRaises(ValueError):
            self.manager.record_sale(sale)

        self.assertEqual(self.inventory.get_stock(101, "in_store"), 10)
        self.assertEqual(self.inventory.get_stock(102, "in_store"), 5)

    def test_duplicate_transaction_rejected(self):
        first = SalesTransaction(1, self.customer, self.staff)
        first.add_item(self.mouse, 2)
        self.manager.record_sale(first)

        duplicate = SalesTransaction(1, self.customer, self.staff)
        duplicate.add_item(self.mouse, 1)
        with self.assertRaises(ValueError):
            self.manager.record_sale(duplicate)
        self.assertEqual(self.inventory.get_stock(101, "in_store"), 8)

    def test_recorded_sale_cannot_be_reused(self):
        sale = SalesTransaction(1, self.customer, self.staff)
        sale.add_item(self.mouse, 1)
        self.manager.record_sale(sale)

        with self.assertRaises(ValueError):
            self.manager.record_sale(sale)
        with self.assertRaises(ValueError):
            sale.add_item(self.mouse, 1)
    def test_online_sale_cannot_use_store_stock(self):
        online = SalesFactory.create_sale("online", 1, self.customer, self.staff)
        online.add_item(self.mouse, 7)
        with self.assertRaises(ValueError):
            self.manager.record_sale(online)
        self.assertEqual(self.inventory.get_stock(101, "in_store"), 10)
        self.assertEqual(self.inventory.get_stock(101, "online"), 6)

    def test_detailed_sales_report(self):
        sale = SalesFactory.create_sale("in_store", 1, self.customer, self.staff)
        sale.add_item(self.mouse, 2)
        sale.add_item(self.keyboard, 1)
        self.manager.record_sale(sale)

        report = self.manager.sales_report()
        self.assertIn("ID: 1 | Date:", report)
        self.assertIn("Channel: In-Store", report)
        self.assertIn("Customer: Jordan (ID: 1)", report)
        self.assertIn("Product ID: 101 | Name: Mouse | Quantity: 2", report)
        self.assertIn("Unit price: 20.00 | Line total: 40.00", report)
        self.assertIn("Product ID: 102 | Name: Keyboard | Quantity: 1", report)
        self.assertIn("Unit price: 30.00 | Line total: 30.00", report)
        self.assertIn("Transaction total: 70.00", report)
        self.assertIn("Total transactions: 1", report)
        self.assertIn("Total units sold: 3", report)
        self.assertIn("Total revenue: 70.00", report)

    def test_report_keeps_original_product_details(self):
        sale = SalesFactory.create_sale("in_store", 1, self.customer, self.staff)
        sale.add_item(self.mouse, 2)
        self.manager.record_sale(sale)
        self.mouse.update_details("Gaming Mouse", 50)
        report = self.manager.sales_report()
        self.assertIn("Name: Mouse | Quantity: 2 | Unit price: 20.00", report)
        self.assertNotIn("Gaming Mouse", report)
        self.assertIn("Transaction total: 40.00", report)

    def test_detailed_report_respects_filters(self):
        store = SalesFactory.create_sale("in_store", 1, self.customer, self.staff)
        store.add_item(self.mouse, 1)
        self.manager.record_sale(store)
        other_customer = Customer(2, "Sam")
        online = SalesFactory.create_sale("online", 2, other_customer, self.staff)
        online.add_item(self.keyboard, 2)
        self.manager.record_sale(online)

        report = self.manager.sales_report(date.today(), date.today(), "online")
        self.assertIn("Customer: Sam (ID: 2)", report)
        self.assertIn("Name: Keyboard", report)
        self.assertNotIn("Customer: Jordan", report)
        self.assertNotIn("Name: Mouse", report)
        self.assertIn("Total transactions: 1", report)
        self.assertIn("Total revenue: 60.00", report)

    def test_sales_report_filters(self):
        store = SalesFactory.create_sale("in_store", 1, self.customer, self.staff)
        store.add_item(self.mouse, 2)
        self.manager.record_sale(store)
        online = SalesFactory.create_sale("online", 2, self.customer, self.staff)
        online.add_item(self.mouse, 1)
        self.manager.record_sale(online)

        today = date.today()
        report = self.manager.sales_report(today, today, "online")
        self.assertIn("Total transactions: 1", report)
        self.assertIn("Total units sold: 1", report)
        self.assertIn("Total revenue: 20.00", report)
        self.assertNotIn("Channel: In-Store", report)

        empty = self.manager.sales_report(today + timedelta(days=1),
                                          today + timedelta(days=1))
        self.assertIn("No sales recorded", empty)
        with self.assertRaises(ValueError):
            self.manager.sales_report(today, today - timedelta(days=1))



class TestPrediction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.clean, cls.summary = clean_sales_data(load_sales_data())

    def test_sales_data_cleaned(self):
        self.assertEqual(self.summary["clean"], 432)
        self.assertFalse(self.clean.isnull().any().any())
        self.assertFalse(self.clean.duplicated(["product_id", "month"]).any())

    def test_missing_sales_column_rejected(self):
        data = load_sales_data().drop(columns=["product_id"])
        with self.assertRaises(KeyError):
            clean_sales_data(data)

    def test_missing_csv_file_rejected(self):
        with TemporaryDirectory() as folder:
            missing = Path(folder) / "missing.csv"
            with self.assertRaises(FileNotFoundError):
                load_sales_data(missing)

    def test_prediction_features_12_month_boundary(self):
        history = self.clean[self.clean["product_id"] == 101]
        features = build_features(101, history, "2027-10")
        self.assertEqual(features["months_ahead"], 12)
        self.assertTrue(all(name in features for name in FEATURE_COLUMNS))

        with self.assertRaises(ValueError):
            build_features(101, history, "2027-11")

    def test_predict_first_and_last_month(self):
        service = DemandPredictionService()
        for month, year, months_ahead in [(11, 2026, 1), (10, 2027, 12)]:
            with self.subTest(month=month, year=year):
                result = service.predict_product(101, month, year)
                self.assertEqual(result["product_id"], 101)
                self.assertEqual(result["months_ahead"], months_ahead)
                self.assertNotIn("overall", result)
                for channel in ["in_store", "online"]:
                    self.assertIn(result[channel], VALID_LABELS)

    def test_search_prediction_products_by_name(self):
        service = DemandPredictionService()
        matches = service.search_products("mouse")
        self.assertEqual({item["product_id"] for item in matches}, {101, 103})
        one = service.search_products("101")
        self.assertEqual(one[0]["product_name"], "Wireless Mouse")

    def test_unknown_product_rejected(self):
        service = DemandPredictionService()
        with self.assertRaises(KeyError):
            service.predict_product(999, 11, 2026)

    def test_invalid_prediction_dates_rejected(self):
        service = DemandPredictionService()
        for month, year in [(10, 2026), (11, 2027), (13, 2026)]:
            with self.subTest(month=month, year=year):
                with self.assertRaises(ValueError):
                    service.predict_product(101, month, year)

    def test_missing_model_file_rejected(self):
        with TemporaryDirectory() as folder:
            missing = Path(folder) / "missing.joblib"
            with self.assertRaises(FileNotFoundError):
                DemandPredictionService(model_file=missing)


if __name__ == "__main__":
    unittest.main()
