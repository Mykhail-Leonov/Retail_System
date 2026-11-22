import calendar
from datetime import date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

from models import Category, Product, Customer, Staff
from inventory import Inventory
from sales import SalesManager, SalesFactory
from observers import LowStockNotifier, StockObserver
from prediction_gui import PredictionWindow


# Choose a product by name or ID. List if several names match.
class ProductPicker(ttk.Frame):

    def __init__(self, parent, inventory):
        super().__init__(parent)
        self.inventory = inventory
        self.query = tk.StringVar()
        self.choice = tk.StringVar()
        self.selected_id = None
        self.options = {}

        self.entry = ttk.Entry(self, textvariable=self.query, width=30)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.combo = ttk.Combobox(self, textvariable=self.choice,
                                  state="readonly", width=30)
        self.combo.pack(side="left", fill="x", expand=True)
        self.combo.bind("<<ComboboxSelected>>", self.on_choice)
        self.query.trace_add("write", self.refresh)
        self.refresh()

    def refresh(self, *args):
        query = self.query.get().strip()
        self.selected_id = None
        self.options = {}
        self.choice.set("")

        products = self.inventory.get_products()
        if not query:
            matches = []
        elif query.isdigit():
            matches = [p for p in products if p.get_id() == int(query)]
        else:
            matches = [p for p in products if query.lower() in p.get_name().lower()]
            exact = [p for p in matches if p.get_name().lower() == query.lower()]
            if len(exact) == 1:
                matches = exact

        self.options = {
            "{} (ID: {})".format(p.get_name(), p.get_id()): p.get_id()
            for p in matches
        }
        self.combo["values"] = list(self.options)
        if len(matches) == 1:
            self.selected_id = matches[0].get_id()
            self.choice.set(next(iter(self.options)))
        elif len(matches) > 1:
            self.choice.set("Select a matching product...")
        elif query:
            self.choice.set("No matching products")
        else:
            self.choice.set("Type a product name...")

    def on_choice(self, *args):
        self.selected_id = self.options.get(self.choice.get())

    def get_product(self):
        if self.selected_id is None:
            raise ValueError("Enter a product name and select a match if necessary.")
        return self.inventory.get_product(self.selected_id)

    def clear(self):
        self.query.set("")


# Display low-stock alerts inside the GUI and the console.
class GUIStockNotifier(StockObserver):

    def __init__(self, application):
        self.application = application

    def update(self, product, channel="in_store"):
        self.application.new_alerts.append(
            "Low stock: {} ({}) — {} remaining.".format(
                product.get_name(), channel.replace("_", "-"),
                self.application.inventory.get_stock(product.get_id(), channel)))


class RetailApplication:

    def __init__(self, window):
        self.window = window
        self.window.title("Smart Retail Management System")
        self.window.geometry("1080x820")
        self.window.minsize(900, 660)

        
        self.inventory = Inventory()
        self.inventory.attach(LowStockNotifier())
        self.inventory.attach(GUIStockNotifier(self))
        self.sales_manager = SalesManager(self.inventory)
        self.staff = Staff(1, "Store Staff")
        self.new_alerts = []
        self.pending_items = []
        self.next_transaction_id = 1
        self.next_customer_id = 1
        self.status = tk.StringVar(value="Ready. Data is kept only while this window is open.")

        outer = ttk.Frame(window, padding=12)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Smart Retail Management System",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Products, inventory, sales and demand prediction",
                  foreground="gray").pack(anchor="w", pady=(0, 10))

        self.tabs = ttk.Notebook(outer)
        self.tabs.pack(fill="both", expand=True)
        self.category_tab = ttk.Frame(self.tabs, padding=12)
        self.product_tab = ttk.Frame(self.tabs, padding=12)
        self.inventory_tab = ttk.Frame(self.tabs, padding=12)
        self.sales_tab = ttk.Frame(self.tabs, padding=12)
        self.report_tab = ttk.Frame(self.tabs, padding=12)
        self.prediction_tab = ttk.Frame(self.tabs, padding=12)

        for frame, name in [
            (self.category_tab, "Categories"),
            (self.product_tab, "Products"),
            (self.inventory_tab, "Inventory"),
            (self.sales_tab, "Sales"),
            (self.report_tab, "Reports"),
            (self.prediction_tab, "Prediction")
        ]:
            self.tabs.add(frame, text=name)

        self.build_categories()
        self.build_products()
        self.build_inventory()
        self.build_sales()
        self.build_reports()
        self.build_prediction()

        ttk.Separator(outer).pack(fill="x", pady=(9, 5))
        ttk.Label(outer, textvariable=self.status, wraplength=980).pack(anchor="w")
        self.refresh_all()

    # GUI helpers
    def field(self, parent, label, variable, row, column, width=17):
        ttk.Label(parent, text=label).grid(row=row, column=column * 2,
                                           sticky="w", padx=(0, 5), pady=4)
        entry = ttk.Entry(parent, textvariable=variable, width=width)
        entry.grid(row=row, column=column * 2 + 1, sticky="ew", padx=(0, 14), pady=4)
        return entry

    def table(self, parent, columns, widths, height=7):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=7)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
        for name, width in zip(columns, widths):
            tree.heading(name, text=name)
            tree.column(name, width=width, minwidth=55, anchor="w")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def display_text(self, widget, content):
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", content)
        widget.configure(state="disabled")

    def selected_id(self, tree, label):
        selection = tree.selection()
        if not selection:
            raise ValueError("Select a {} in the list first.".format(label))
        return int(selection[0])

    def run(self, operation):
        self.new_alerts.clear()
        try:
            operation()
        except (ValueError, TypeError, KeyError) as error:
            message = error.args[0] if isinstance(error, KeyError) else str(error)
            messagebox.showerror("Smart Retail", str(message), parent=self.window)
            self.status.set("Error: " + str(message))
            return

        self.refresh_all()
        if self.new_alerts:
            messagebox.showwarning("Low-stock notification", "\n".join(self.new_alerts),
                                   parent=self.window)
            self.status.set(self.status.get() + "  " + " ".join(self.new_alerts))

    def next_id(self, items, start=1):
        return max([item.get_id() for item in items], default=start - 1) + 1

    def refresh_all(self):
        self.refresh_categories()
        self.refresh_products()
        self.refresh_inventory()
        self.sale_picker.refresh()
        self.history_picker.refresh()
        self.refresh_pending()

    # Categories: add, rename, remove
    def build_categories(self):
        page = self.category_tab
        ttk.Label(page, text="Product Categories", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        self.category_tree = self.table(page, ("ID", "Category"), (110, 450))
        self.category_tree.bind("<<TreeviewSelect>>", self.on_category_selected)

        create = ttk.LabelFrame(page, text="Add category", padding=10)
        create.pack(fill="x", pady=6)
        self.cat_id = tk.StringVar()
        self.cat_name = tk.StringVar()
        self.field(create, "ID", self.cat_id, 0, 0)
        self.field(create, "Name", self.cat_name, 0, 1, width=28)
        ttk.Button(create, text="Add", command=lambda: self.run(self.add_category)).grid(
            row=0, column=4, padx=6)

        edit = ttk.LabelFrame(page, text="Edit selected category", padding=10)
        edit.pack(fill="x", pady=6)
        self.cat_edit = tk.StringVar()
        self.field(edit, "New name", self.cat_edit, 0, 0, width=30)
        ttk.Button(edit, text="Rename", command=lambda: self.run(self.rename_category)).grid(
            row=0, column=2, padx=6)
        ttk.Button(edit, text="Remove", command=lambda: self.run(self.remove_category)).grid(
            row=0, column=3, padx=6)

    def refresh_categories(self):
        self.category_tree.delete(*self.category_tree.get_children())
        for item in self.inventory.get_categories():
            self.category_tree.insert("", "end", iid=str(item.get_id()),
                                      values=(item.get_id(), item.get_name()))
        if not self.cat_id.get():
            self.cat_id.set(str(self.next_id(self.inventory.get_categories())))
        self.refresh_category_dropdown()

    def refresh_category_dropdown(self):
        categories = self.inventory.get_categories()
        self.category_options = {
            "{} (ID: {})".format(c.get_name(), c.get_id()): c.get_id()
            for c in categories
        }
        self.product_category_box["values"] = list(self.category_options)

    def on_category_selected(self, *args):
        if self.category_tree.selection():
            category = self.inventory.get_category(self.selected_id(self.category_tree, "category"))
            self.cat_edit.set(category.get_name())

    def add_category(self):
        self.inventory.add_category(Category(int(self.cat_id.get()), self.cat_name.get()))
        self.cat_name.set("")
        self.cat_id.set(str(self.next_id(self.inventory.get_categories())))
        self.status.set("Category added.")

    def rename_category(self):
        category = self.inventory.get_category(self.selected_id(self.category_tree, "category"))
        category.update_name(self.cat_edit.get())
        self.status.set("Category updated.")

    def remove_category(self):
        category_id = self.selected_id(self.category_tree, "category")
        if messagebox.askyesno("Remove category", "Remove selected category?", parent=self.window):
            self.inventory.remove_category(category_id)
            self.status.set("Category removed.")

    # Products: add, update, remove and search
    def build_products(self):
        page = self.product_tab
        ttk.Label(page, text="Products", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        top = ttk.Frame(page)
        top.pack(fill="x", pady=5)
        ttk.Label(top, text="Search by product name or ID:").pack(side="left", padx=(0, 6))
        self.product_search = tk.StringVar()
        ttk.Entry(top, textvariable=self.product_search, width=35).pack(side="left", fill="x")
        self.product_search.trace_add("write", lambda *_: self.refresh_products())
        self.product_tree = self.table(page,
            ("ID", "Product", "Category", "Price", "In-store", "Online", "Total"),
            (60, 180, 160, 85, 90, 80, 75), height=8)
        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_selected)

        create = ttk.LabelFrame(page, text="Add product", padding=10)
        create.pack(fill="x", pady=5)
        self.prod_id = tk.StringVar()
        self.prod_name = tk.StringVar()
        self.prod_price = tk.StringVar()
        self.prod_category = tk.StringVar()
        self.prod_store = tk.StringVar(value="0")
        self.prod_online = tk.StringVar(value="0")
        self.field(create, "Product ID", self.prod_id, 0, 0)
        self.field(create, "Name", self.prod_name, 0, 1, width=24)
        self.field(create, "Price (£)", self.prod_price, 0, 2)
        ttk.Label(create, text="Category").grid(row=1, column=0, sticky="w", pady=4)
        self.product_category_box = ttk.Combobox(create, textvariable=self.prod_category,
                                                 state="readonly", width=23)
        self.product_category_box.grid(row=1, column=1, sticky="ew", pady=4, padx=(0, 14))
        self.field(create, "In-store stock", self.prod_store, 1, 1)
        self.field(create, "Online stock", self.prod_online, 1, 2)
        ttk.Button(create, text="Add product", command=lambda: self.run(self.add_product)).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        edit = ttk.LabelFrame(page, text="Update or remove selected product", padding=10)
        edit.pack(fill="x", pady=6)
        self.prod_edit_name = tk.StringVar()
        self.prod_edit_price = tk.StringVar()
        self.field(edit, "Name", self.prod_edit_name, 0, 0, width=24)
        self.field(edit, "Price (£)", self.prod_edit_price, 0, 1)
        ttk.Button(edit, text="Update selected", command=lambda: self.run(self.update_product)).grid(
            row=0, column=4, padx=6)
        ttk.Button(edit, text="Remove selected", command=lambda: self.run(self.remove_product)).grid(
            row=0, column=5, padx=6)

    def refresh_products(self):
        self.product_tree.delete(*self.product_tree.get_children())
        query = self.product_search.get().strip().lower()
        for p in self.inventory.get_products():
            pid = p.get_id()
            if query and query not in p.get_name().lower() and query != str(pid):
                continue
            self.product_tree.insert("", "end", iid=str(pid), values=(
                pid, p.get_name(), p.get_category().get_name(),
                "£{:.2f}".format(p.get_price()),
                self.inventory.get_stock(pid, "in_store"),
                self.inventory.get_stock(pid, "online"),
                self.inventory.get_stock(pid)))
        if not self.prod_id.get():
            self.prod_id.set(str(self.next_id(self.inventory.get_products(), 101)))

    def on_product_selected(self, *args):
        if self.product_tree.selection():
            p = self.inventory.get_product(self.selected_id(self.product_tree, "product"))
            self.prod_edit_name.set(p.get_name())
            self.prod_edit_price.set(str(p.get_price()))

    def add_product(self):
        category_id = self.category_options.get(self.prod_category.get())
        if category_id is None:
            raise ValueError("Choose a category before adding a product.")
        category = self.inventory.get_category(category_id)
        product = Product(int(self.prod_id.get()), self.prod_name.get(),
                          float(self.prod_price.get()), category)
        self.inventory.add_product(product, int(self.prod_store.get()), int(self.prod_online.get()))
        self.prod_id.set(str(self.next_id(self.inventory.get_products(), 101)))
        self.prod_name.set("")
        self.prod_price.set("")
        self.prod_store.set("0")
        self.prod_online.set("0")
        self.status.set("Product added.")

    def update_product(self):
        pid = self.selected_id(self.product_tree, "product")
        self.inventory.update_product(pid, self.prod_edit_name.get(), float(self.prod_edit_price.get()))
        self.status.set("Product updated.")

    def remove_product(self):
        pid = self.selected_id(self.product_tree, "product")
        if messagebox.askyesno("Remove product", "Remove selected product from inventory?",
                               parent=self.window):
            self.inventory.remove_product(pid)
            self.status.set("Product removed.")

    # Inventory: channel quantities, full report and low stock
    def build_inventory(self):
        page = self.inventory_tab
        ttk.Label(page, text="Inventory", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        top = ttk.Frame(page)
        top.pack(fill="x", pady=4)
        ttk.Label(top, text="Product search:").pack(side="left", padx=(0, 6))
        self.stock_search = tk.StringVar()
        ttk.Entry(top, textvariable=self.stock_search, width=25).pack(side="left")
        self.stock_search.trace_add("write", lambda *_: self.refresh_inventory())
        self.low_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Low-stock only", variable=self.low_only,
                        command=self.refresh_inventory).pack(side="left", padx=20)
        self.inventory_tree = self.table(page,
            ("ID", "Product", "Category", "Price", "In-store", "Online", "Total", "Low stock"),
            (60, 165, 140, 80, 85, 80, 65, 150), height=8)

        edit = ttk.LabelFrame(page, text="Update selected product stock", padding=10)
        edit.pack(fill="x", pady=4)
        self.stock_channel = tk.StringVar(value="in_store")
        self.stock_change = tk.StringVar()
        ttk.Label(edit, text="Channel").grid(row=0, column=0, padx=5)
        ttk.Combobox(edit, textvariable=self.stock_channel, state="readonly",
                     values=["in_store", "online"], width=16).grid(row=0, column=1, padx=5)
        ttk.Label(edit, text="Change (+ or -)").grid(row=0, column=2, padx=5)
        ttk.Entry(edit, textvariable=self.stock_change, width=14).grid(row=0, column=3, padx=5)
        ttk.Button(edit, text="Update stock", command=lambda: self.run(self.update_stock)).grid(
            row=0, column=4, padx=10)

        report_frame = ttk.LabelFrame(page, text="Full inventory report", padding=8)
        report_frame.pack(fill="both", expand=True, pady=5)
        self.inventory_report_text = ScrolledText(report_frame, height=8, wrap="word",
                                                  font=("Consolas", 10), state="disabled")
        self.inventory_report_text.pack(fill="both", expand=True)

    def refresh_inventory(self):
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        query = self.stock_search.get().strip().lower()
        for p in self.inventory.get_products():
            pid = p.get_id()
            low_channels = self.inventory.get_low_stock_channels(pid)
            if self.low_only.get() and not low_channels:
                continue
            if query and query not in p.get_name().lower() and query != str(pid):
                continue
            self.inventory_tree.insert("", "end", iid=str(pid), values=(
                pid, p.get_name(), p.get_category().get_name(),
                "£{:.2f}".format(p.get_price()),
                self.inventory.get_stock(pid, "in_store"),
                self.inventory.get_stock(pid, "online"),
                self.inventory.get_stock(pid),
                ", ".join(c.replace("_", "-") for c in low_channels) or "None"))
        self.display_text(self.inventory_report_text, self.inventory.inventory_report())

    def update_stock(self):
        pid = self.selected_id(self.inventory_tree, "product")
        self.inventory.update_stock(pid, int(self.stock_change.get()), self.stock_channel.get())
        self.stock_change.set("")
        self.status.set("Stock updated.")

    # Sales: create transactions, enter multiple items and view history of products
    def build_sales(self):
        page = self.sales_tab
        ttk.Label(page, text="Record Sale", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        details = ttk.LabelFrame(page, text="Transaction details", padding=9)
        details.pack(fill="x", pady=5)
        self.sale_type = tk.StringVar(value="in_store")
        self.sale_id = tk.StringVar(value="1")
        self.customer_id = tk.StringVar(value="1")
        self.customer_name = tk.StringVar()
        ttk.Label(details, text="Channel").grid(row=0, column=0, padx=5, sticky="w")
        ttk.Combobox(details, textvariable=self.sale_type, state="readonly", width=15,
                     values=["in_store", "online"]).grid(row=0, column=1, sticky="w", padx=5)
        self.field(details, "Transaction ID", self.sale_id, 0, 1)
        self.field(details, "Customer ID", self.customer_id, 0, 2)
        self.field(details, "Customer name", self.customer_name, 1, 0, width=25)

        add = ttk.LabelFrame(page, text="Add products to this sale", padding=9)
        add.pack(fill="x", pady=5)
        ttk.Label(add, text="Product name or ID").grid(row=0, column=0, sticky="w", padx=5)
        self.sale_picker = ProductPicker(add, self.inventory)
        self.sale_picker.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5)
        ttk.Label(add, text="Quantity").grid(row=0, column=4, padx=5)
        self.item_quantity = tk.StringVar(value="1")
        ttk.Entry(add, textvariable=self.item_quantity, width=7).grid(row=0, column=5, padx=5)
        ttk.Button(add, text="Add item", command=lambda: self.run(self.add_sale_item)).grid(
            row=0, column=6, padx=5)
        add.columnconfigure(1, weight=1)

        self.pending_tree = self.table(page, ("Product", "Quantity", "Unit price", "Line total"),
                                       (280, 90, 115, 115), height=5)
        buttons = ttk.Frame(page)
        buttons.pack(fill="x", pady=4)
        self.pending_total = tk.StringVar(value="Pending total: £0.00")
        ttk.Label(buttons, textvariable=self.pending_total,
                  font=("Segoe UI", 11, "bold")).pack(side="left")
        ttk.Button(buttons, text="Remove selected item",
                   command=lambda: self.run(self.remove_sale_item)).pack(side="right", padx=5)
        ttk.Button(buttons, text="Record sale",
                   command=lambda: self.run(self.record_sale)).pack(side="right", padx=5)

        history = ttk.LabelFrame(page, text="Product sales history", padding=9)
        history.pack(fill="x", pady=12)
        ttk.Label(history, text="Product").pack(side="left", padx=(0, 5))
        self.history_picker = ProductPicker(history, self.inventory)
        self.history_picker.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(history, text="Show history",
                   command=lambda: self.run(self.show_sales_history)).pack(side="left", padx=5)
        self.history_result = tk.StringVar(value="")
        ttk.Label(page, textvariable=self.history_result).pack(anchor="w", pady=3)

    def add_sale_item(self):
        product = self.sale_picker.get_product()
        quantity = int(self.item_quantity.get())
        if quantity <= 0:
            raise ValueError("Sale quantity must be a positive integer.")
        self.pending_items.append((product, quantity))
        self.sale_picker.clear()
        self.item_quantity.set("1")
        self.status.set("Item added to sale.")

    def refresh_pending(self):
        self.pending_tree.delete(*self.pending_tree.get_children())
        total = 0
        for index, (product, quantity) in enumerate(self.pending_items):
            line_total = product.get_price() * quantity
            total += line_total
            self.pending_tree.insert("", "end", iid=str(index), values=(
                product.get_name(), quantity, "£{:.2f}".format(product.get_price()),
                "£{:.2f}".format(line_total)))
        self.pending_total.set("Pending total: £{:.2f}".format(total))

    def remove_sale_item(self):
        index = self.selected_id(self.pending_tree, "sale item")
        self.pending_items.pop(index)
        self.status.set("Item removed from sale.")

    def record_sale(self):
        if not self.pending_items:
            raise ValueError("Add at least one product to the sale.")
        customer = Customer(int(self.customer_id.get()), self.customer_name.get())
        sale = SalesFactory.create_sale(self.sale_type.get(), int(self.sale_id.get()),
                                        customer, self.staff)
        for product, quantity in self.pending_items:
            sale.add_item(product, quantity)
        self.sales_manager.record_sale(sale)
        self.pending_items.clear()
        self.next_transaction_id = max(self.next_transaction_id, sale.get_id() + 1)
        self.next_customer_id = max(self.next_customer_id, int(self.customer_id.get()) + 1)
        self.sale_id.set(str(self.next_transaction_id))
        self.customer_id.set(str(self.next_customer_id))
        self.customer_name.set("")
        self.status.set("{} sale recorded. Total: £{:.2f}".format(
            sale.get_channel(), sale.calculate_total()))
        messagebox.showinfo("Sale recorded", self.status.get(), parent=self.window)

    def show_sales_history(self):
        product = self.history_picker.get_product()
        history = self.sales_manager.get_sales_data(product.get_id())
        self.history_result.set("{}: quantities sold per sale: {}".format(
            product.get_name(), history if history else "No sales yet"))
        self.status.set("Product sales history displayed.")

    # Sales reports: all, today, week, month, exact date and custom range
    def build_reports(self):
        page = self.report_tab
        ttk.Label(page, text="Combined Sales Report", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        filters = ttk.LabelFrame(page, text="Report filters", padding=12)
        filters.pack(fill="x", pady=10)
        self.report_period = tk.StringVar(value="All")
        self.report_channel = tk.StringVar(value="Both")
        self.report_year = tk.StringVar(value=str(date.today().year))
        self.report_month = tk.StringVar(value=str(date.today().month))
        self.report_exact = tk.StringVar(value=date.today().isoformat())
        self.report_start = tk.StringVar(value=date.today().isoformat())
        self.report_end = tk.StringVar(value=date.today().isoformat())

        ttk.Label(filters, text="Period").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Combobox(filters, textvariable=self.report_period, state="readonly", width=17,
                     values=["All", "Today", "This week", "Month", "Exact date", "Date range"]).grid(
            row=0, column=1, padx=5, sticky="w")
        ttk.Label(filters, text="Channel").grid(row=0, column=2, padx=5, sticky="w")
        ttk.Combobox(filters, textvariable=self.report_channel, state="readonly", width=14,
                     values=["Both", "In-store", "Online"]).grid(row=0, column=3, padx=5, sticky="w")
        self.field(filters, "Year", self.report_year, 1, 0)
        ttk.Label(filters, text="Month (1–12)").grid(row=1, column=2, padx=5, sticky="w")
        ttk.Combobox(filters, textvariable=self.report_month, state="readonly", width=12,
                     values=[str(i) for i in range(1, 13)]).grid(row=1, column=3, padx=5, sticky="w")
        self.field(filters, "Exact date", self.report_exact, 2, 0, width=16)
        self.field(filters, "Start date", self.report_start, 2, 1, width=16)
        self.field(filters, "End date", self.report_end, 3, 0, width=16)
        ttk.Label(filters, text="Date format: YYYY-MM-DD (only fill fields used by the selected period)",
                  foreground="gray").grid(row=3, column=2, columnspan=2, sticky="w")
        ttk.Button(filters, text="Generate report", command=lambda: self.run(self.generate_sales_report)).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(9, 0))

        self.sales_report_text = ScrolledText(page, wrap="word", font=("Consolas", 10),
                                             state="disabled", height=18)
        self.sales_report_text.pack(fill="both", expand=True, pady=8)
        self.display_text(self.sales_report_text, self.sales_manager.sales_report())

    def generate_sales_report(self):
        period = self.report_period.get()
        today = date.today()
        start = end = None
        if period == "Today":
            start = end = today
        elif period == "This week":
            start = today - timedelta(days=today.weekday())
            end = today
        elif period == "Month":
            year = int(self.report_year.get())
            month = int(self.report_month.get())
            start = date(year, month, 1)
            end = date(year, month, calendar.monthrange(year, month)[1])
        elif period == "Exact date":
            start = end = date.fromisoformat(self.report_exact.get().strip())
        elif period == "Date range":
            start = date.fromisoformat(self.report_start.get().strip())
            end = date.fromisoformat(self.report_end.get().strip())
        elif period != "All":
            raise ValueError("Choose a valid report period.")

        channel = {"Both": None, "In-store": "in_store", "Online": "online"}[self.report_channel.get()]
        self.display_text(self.sales_report_text, self.sales_manager.sales_report(start, end, channel))
        self.status.set("Sales report generated.")

    # original prediction GUI.
    def build_prediction(self):
        try:
            self.prediction_window = PredictionWindow(self.prediction_tab, embedded=True)
        except (FileNotFoundError, ValueError, KeyError) as error:
            ttk.Label(self.prediction_tab,
                      text="Cannot load demand prediction: {}\nRun python train_prediction_model.py first.".format(error),
                      wraplength=700).pack(anchor="w", pady=20)
            self.prediction_window = None


def launch_retail_gui():
    root = tk.Tk()
    RetailApplication(root)
    root.mainloop()


if __name__ == "__main__":
    launch_retail_gui()
