import calendar
import tkinter as tk
from tkinter import ttk, messagebox
from prediction_service import DemandPredictionService


class PredictionWindow:

    def __init__(self, window):
        self.window = window
        self.window.title("Smart Retail - Demand Prediction")
        self.window.geometry("490x600")
        self.window.resizable(False, False)

        self.service = DemandPredictionService()
        first, last = self.service.available_months()
        first_year, first_month = map(int, first.split("-"))

        self.product_id = tk.StringVar()
        self.product_name = tk.StringVar(value="Enter a product name or ID")
        self.product_choice = tk.StringVar()
        self.product_options = {}
        self.selected_product_id = None
        self.month = tk.StringVar(value=calendar.month_name[first_month])
        self.year = tk.StringVar(value=str(first_year))
        self.available_range = "Available months: {} to {}".format(first, last)
        self.status = tk.StringVar(value=self.available_range)
        self.results = {
            "in_store": tk.StringVar(value="—"),
            "online": tk.StringVar(value="—")
        }

        frame = ttk.Frame(window, padding=22)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Demand Prediction",
                  font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(0, 8))
        ttk.Label(frame, text="Choose a product and month to predict demand.").pack(
            anchor="w", pady=(0, 18))

        ttk.Label(frame, text="Product name (or ID)").pack(anchor="w")
        id_entry = ttk.Entry(frame, textvariable=self.product_id)
        id_entry.pack(fill="x", pady=(4, 6))
        ttk.Label(frame, textvariable=self.product_name).pack(anchor="w", pady=(0, 8))

        # Only show this when the name matches multiple products
        self.choice_box = ttk.Combobox(frame, textvariable=self.product_choice, state="readonly")
        self.choice_box.bind("<<ComboboxSelected>>", self.on_choice_changed)

        fields = ttk.Frame(frame)
        self.fields = fields
        fields.pack(fill="x", pady=(12, 0))
        fields.columnconfigure(0, weight=1)
        fields.columnconfigure(1, weight=1)

        ttk.Label(fields, text="Month").grid(row=0, column=0, sticky="w")
        ttk.Label(fields, text="Year").grid(row=0, column=1, sticky="w", padx=(16, 0))
        ttk.Combobox(fields, textvariable=self.month,
                     values=list(calendar.month_name)[1:], state="readonly").grid(
            row=1, column=0, sticky="ew", pady=(4, 16))

        last_year = int(last.split("-")[0])
        ttk.Combobox(
            fields,
            textvariable=self.year,
            values=[str(y) for y in range(first_year, last_year + 1)],
            state="readonly"
        ).grid(row=1, column=1, sticky="ew", padx=(16, 0), pady=(4, 16))

        ttk.Button(frame, text="Predict Demand", command=self.predict).pack(
            fill="x", pady=(0, 20))

        ttk.Label(frame, text="Demand Prediction Report",
                  font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))

        for key, name in [("in_store", "In-store"), ("online", "Online")]:
            line = ttk.Frame(frame)
            line.pack(fill="x", pady=5)
            ttk.Label(line, text=name, width=16).pack(side="left")
            ttk.Label(line, textvariable=self.results[key],
                      font=("Segoe UI", 11, "bold")).pack(side="left")

        ttk.Label(frame, textvariable=self.status).pack(anchor="w", pady=(18, 0))

        # Update the name when the search changes
        self.product_id.trace_add("write", self.on_product_changed)
        self.month.trace_add("write", self.clear_results)
        self.year.trace_add("write", self.clear_results)
        id_entry.focus_set()

    # Clear old predictions
    def clear_results(self, *args):
        for value in self.results.values():
            value.set("—")
        self.status.set(self.available_range)

    # Search by product name or ID
    def on_product_changed(self, *args):
        query = self.product_id.get().strip()
        self.selected_product_id = None
        self.product_options = {}
        self.product_choice.set("")
        self.choice_box.pack_forget()

        if not query:
            self.product_name.set("Enter a product name or ID")
        else:
            try:
                matches = self.service.search_products(query)
            except ValueError:
                matches = []

            # Prefer a full-name match over partial matches
            exact = [item for item in matches
                     if item["product_name"].lower() == query.lower()]
            if len(exact) == 1:
                matches = exact

            if not matches:
                self.product_name.set("No matching product in sales history")
            elif len(matches) == 1:
                self.selected_product_id = matches[0]["product_id"]
                self.product_name.set(matches[0]["product_name"])
            else:
                self.product_name.set("Multiple matches - choose one:")
                self.product_options = {
                    "{} (ID: {})".format(item["product_name"], item["product_id"]): item["product_id"]
                    for item in matches
                }
                self.choice_box["values"] = list(self.product_options)
                self.choice_box.pack(fill="x", pady=(0, 8), before=self.fields)

        self.clear_results()

    # Use the product selected from the matches
    def on_choice_changed(self, *args):
        choice = self.product_choice.get()
        self.selected_product_id = self.product_options.get(choice)
        if self.selected_product_id is not None:
            self.product_name.set(self.service.get_product_name(self.selected_product_id))
        self.clear_results()

    # Get the two predictions
    def predict(self):
        try:
            if self.selected_product_id is None:
                raise ValueError("Enter or select a matching product.")

            month = list(calendar.month_name).index(self.month.get())
            try:
                year = int(self.year.get().strip())
            except ValueError:
                raise ValueError("Enter a valid year.")

            result = self.service.predict_product(self.selected_product_id, month, year)
            for channel in self.results:
                self.results[channel].set(result[channel] + " Demand")

            unit = "month" if result["months_ahead"] == 1 else "months"
            self.status.set("{} | {} | {} {} ahead".format(
                result["product_name"], result["month"], result["months_ahead"], unit))

        except (ValueError, KeyError) as error:
            self.clear_results()
            message = str(error.args[0]) if isinstance(error, KeyError) else str(error)
            messagebox.showerror("Prediction error", message, parent=self.window)


def launch_prediction_window():
    window = tk.Tk()
    try:
        PredictionWindow(window)
    except (FileNotFoundError, ValueError, KeyError) as error:
        messagebox.showerror("Prediction error", str(error), parent=window)
        window.destroy()
        return
    window.mainloop()


if __name__ == "__main__":
    launch_prediction_window()
