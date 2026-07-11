

import csv
import os
import logging
from datetime import datetime
from statistics import mean


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    "data_dir": os.path.join(BASE_DIR, "data"),
    "output_dir": os.path.join(BASE_DIR, "output"),
    "log_dir": os.path.join(BASE_DIR, "logs"),
    "input_file": "sales_data.csv",       # source file, inside data_dir
    "export_csv": "processed_sales.csv",  # inside output_dir
    "summary_txt": "summary_report.txt",  # inside output_dir
    "log_file": "activity.log",           # inside log_dir
}

# Columns expected in the sales CSV file
FIELDNAMES = ["ProductID", "ProductName", "Category", "Region",
              "Quantity", "UnitPrice", "Date"]

NUMERIC_FIELDS = {"Quantity", "UnitPrice"}


def ensure_directories():
    """Create data/output/log directories if they don't already exist."""
    for key in ("data_dir", "output_dir", "log_dir"):
        os.makedirs(CONFIG[key], exist_ok=True)


def setup_logging():
    """Configure logging so every file operation is recorded with a timestamp."""
    log_path = os.path.join(CONFIG["log_dir"], CONFIG["log_file"])
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def full_path(kind, filename_key):
    """Build a full file path from the CONFIG dictionary."""
    return os.path.join(CONFIG[kind], CONFIG[filename_key])

def generate_sample_data():
    """Create a sample sales_data.csv file inside data_dir if one is missing."""
    path = full_path("data_dir", "input_file")
    if os.path.exists(path):
        print(f"Sample data already exists at: {path}")
        return

    sample_rows = [
        ["P001", "Wireless Mouse", "Electronics", "South", 25, 599.00, "2026-01-05"],
        ["P002", "Office Chair", "Furniture", "North", 10, 3499.00, "2026-01-06"],
        ["P003", "Bluetooth Speaker", "Electronics", "East", 40, 1299.00, "2026-01-07"],
        ["P004", "Notebook Pack", "Stationery", "West", 100, 89.00, "2026-01-08"],
        ["P005", "LED Desk Lamp", "Furniture", "South", 15, 799.00, "2026-01-09"],
        ["P006", "USB-C Cable", "Electronics", "North", 60, 199.00, "2026-01-10"],
        ["P007", "Whiteboard Marker Set", "Stationery", "East", 75, 149.00, "2026-01-11"],
        ["P008", "Study Table", "Furniture", "West", 5, 4999.00, "2026-01-12"],
        ["P009", "Mechanical Keyboard", "Electronics", "South", 20, 2199.00, "2026-01-13"],
        ["P010", "Sticky Notes", "Stationery", "North", 150, 45.00, "2026-01-14"],
    ]

    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDNAMES)
            writer.writerows(sample_rows)
        logging.info(f"Sample data generated at {path}")
        print(f"Sample data created at: {path}")
    except PermissionError:
        logging.error(f"Permission denied while creating sample file at {path}")
        print("Error: Permission denied while creating the sample data file.")

def load_data(path=None):
    """
    Read a CSV file into a list of dictionaries.
    Handles FileNotFoundError, PermissionError and malformed rows gracefully.
    Numeric fields are converted to float/int automatically.
    """
    if path is None:
        path = full_path("data_dir", "input_file")

    records = []
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    row["Quantity"] = int(row["Quantity"])
                    row["UnitPrice"] = float(row["UnitPrice"])
                    records.append(row)
                except (ValueError, KeyError) as e:
                    logging.warning(f"Skipped malformed row {row_num} in {path}: {e}")
                    print(f"Warning: skipped malformed row {row_num} ({e})")
        logging.info(f"Loaded {len(records)} records from {path}")
        print(f"Loaded {len(records)} records from '{os.path.basename(path)}'.")
    except FileNotFoundError:
        logging.error(f"File not found: {path}")
        print(f"Error: File not found -> {path}")
    except PermissionError:
        logging.error(f"Permission denied reading: {path}")
        print(f"Error: Permission denied while reading -> {path}")
    except csv.Error as e:
        logging.error(f"CSV parsing error in {path}: {e}")
        print(f"Error: Could not parse CSV file -> {e}")

    return records


def save_data(records, path):
    """Write a list of dictionaries to a CSV file, creating folders as needed."""
    if not records:
        print("No data to save.")
        return False

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(records)
        logging.info(f"Saved {len(records)} records to {path}")
        print(f"Saved {len(records)} records to: {path}")
        return True
    except PermissionError:
        logging.error(f"Permission denied writing to: {path}")
        print(f"Error: Permission denied while writing -> {path}")
        return False

def filter_data(records, column, value):
    """Return records where `column` matches `value` (case-insensitive for text)."""
    if not records:
        print("No records loaded yet.")
        return []
    if column not in FIELDNAMES:
        print(f"Invalid column: {column}")
        return []

    if column in NUMERIC_FIELDS:
        try:
            value = float(value)
        except ValueError:
            print("Please enter a numeric value for this column.")
            return []
        filtered = [r for r in records if r[column] == value]
    else:
        filtered = [r for r in records if str(r[column]).lower() == str(value).lower()]

    print(f"Found {len(filtered)} matching record(s).")
    return filtered


def sort_data(records, column, descending=False):
    """Return records sorted by the given column."""
    if not records:
        print("No records loaded yet.")
        return []
    if column not in FIELDNAMES:
        print(f"Invalid column: {column}")
        return records

    try:
        sorted_records = sorted(records, key=lambda r: r[column], reverse=descending)
        return sorted_records
    except TypeError as e:
        logging.error(f"Sort error on column {column}: {e}")
        print(f"Error while sorting: {e}")
        return records


def summarize_data(records):
    """
    Compute overall and per-category summary statistics:
    total revenue, quantity sold, average unit price, top-selling product.
    Returns a dictionary (used both for on-screen display and TXT export).
    """
    if not records:
        print("No records loaded yet.")
        return {}

    for r in records:
        r["Revenue"] = r["Quantity"] * r["UnitPrice"]

    total_revenue = sum(r["Revenue"] for r in records)
    total_quantity = sum(r["Quantity"] for r in records)
    avg_price = mean(r["UnitPrice"] for r in records)
    top_product = max(records, key=lambda r: r["Revenue"])

    categories = {}
    for r in records:
        cat = r["Category"]
        categories.setdefault(cat, {"quantity": 0, "revenue": 0.0})
        categories[cat]["quantity"] += r["Quantity"]
        categories[cat]["revenue"] += r["Revenue"]

    summary = {
        "record_count": len(records),
        "total_revenue": total_revenue,
        "total_quantity": total_quantity,
        "average_unit_price": avg_price,
        "top_product": top_product["ProductName"],
        "top_product_revenue": top_product["Revenue"],
        "by_category": categories,
    }
    return summary


def print_summary(summary):
    """Nicely print a summary dictionary produced by summarize_data()."""
    if not summary:
        return
    print("\n----- SALES SUMMARY -----")
    print(f"Total Records     : {summary['record_count']}")
    print(f"Total Quantity Sold: {summary['total_quantity']}")
    print(f"Total Revenue     : Rs. {summary['total_revenue']:.2f}")
    print(f"Average Unit Price: Rs. {summary['average_unit_price']:.2f}")
    print(f"Top Product       : {summary['top_product']} "
          f"(Rs. {summary['top_product_revenue']:.2f})")
    print("\nBy Category:")
    for cat, stats in summary["by_category"].items():
        print(f"  {cat:<12} Qty: {stats['quantity']:<6} "
              f"Revenue: Rs. {stats['revenue']:.2f}")
    print("--------------------------\n")


def search_records(records, keyword):
    """Search ProductName column for a keyword (case-insensitive, partial match)."""
    if not records:
        print("No records loaded yet.")
        return []
    results = [r for r in records if keyword.lower() in r["ProductName"].lower()]
    print(f"Found {len(results)} record(s) matching '{keyword}'.")
    return results

def export_csv(records, filename=None):
    """Export any list of records (filtered/sorted) to a new CSV in output_dir."""
    if filename is None:
        filename = CONFIG["export_csv"]
    path = os.path.join(CONFIG["output_dir"], filename)
    fieldnames = FIELDNAMES + (["Revenue"] if records and "Revenue" in records[0] else [])
    try:
        os.makedirs(CONFIG["output_dir"], exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        logging.info(f"Exported {len(records)} records to {path}")
        print(f"Exported {len(records)} record(s) to: {path}")
    except PermissionError:
        logging.error(f"Permission denied writing to {path}")
        print(f"Error: Permission denied while writing -> {path}")


def export_summary_txt(summary, filename=None):
    """Export the summary dictionary to a readable TXT report."""
    if filename is None:
        filename = CONFIG["summary_txt"]
    path = os.path.join(CONFIG["output_dir"], filename)

    if not summary:
        print("Nothing to export - generate a summary first.")
        return

    try:
        os.makedirs(CONFIG["output_dir"], exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("SALES SUMMARY REPORT\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 40 + "\n")
            f.write(f"Total Records      : {summary['record_count']}\n")
            f.write(f"Total Quantity Sold: {summary['total_quantity']}\n")
            f.write(f"Total Revenue      : Rs. {summary['total_revenue']:.2f}\n")
            f.write(f"Average Unit Price : Rs. {summary['average_unit_price']:.2f}\n")
            f.write(f"Top Product        : {summary['top_product']} "
                    f"(Rs. {summary['top_product_revenue']:.2f})\n")
            f.write("\nBy Category:\n")
            for cat, stats in summary["by_category"].items():
                f.write(f"  {cat:<12} Qty: {stats['quantity']:<6} "
                        f"Revenue: Rs. {stats['revenue']:.2f}\n")
        logging.info(f"Summary report exported to {path}")
        print(f"Summary report saved to: {path}")
    except PermissionError:
        logging.error(f"Permission denied writing to {path}")
        print(f"Error: Permission denied while writing -> {path}")


def display_records(records, limit=None):
    """Print records in a simple tabular layout."""
    if not records:
        print("No records to display.")
        return
    shown = records[:limit] if limit else records
    header = f"{'ID':<6}{'Product':<22}{'Category':<12}{'Region':<8}{'Qty':<6}{'Price':<10}{'Date':<12}"
    print(header)
    print("-" * len(header))
    for r in shown:
        print(f"{r['ProductID']:<6}{r['ProductName']:<22}{r['Category']:<12}"
              f"{r['Region']:<8}{r['Quantity']:<6}{r['UnitPrice']:<10.2f}{r['Date']:<12}")
    print(f"\n({len(shown)} of {len(records)} record(s) shown)\n")

def main_menu():
    ensure_directories()
    setup_logging()
    logging.info("Program started.")

    records = []          # currently loaded working set
    last_summary = {}      # most recently generated summary

    menu = """
=========================================================
   FILE HANDLING & DATA PROCESSING SYSTEM - SALES DATA
=========================================================
 1. Generate sample data file
 2. Load data from CSV
 3. View all records
 4. Filter records
 5. Sort records
 6. Summarize data
 7. Search records by product name
 8. Export current records to CSV
 9. Export summary report to TXT
 0. Exit
=========================================================
"""
    while True:
        print(menu)
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            generate_sample_data()

        elif choice == "2":
            path_input = input(
                f"Press Enter to use default path ({CONFIG['input_file']}) "
                "or type a full path: "
            ).strip()
            records = load_data(path_input if path_input else None)

        elif choice == "3":
            display_records(records)

        elif choice == "4":
            print(f"Available columns: {', '.join(FIELDNAMES)}")
            col = input("Filter by column: ").strip()
            val = input("Value to match: ").strip()
            filtered = filter_data(records, col, val)
            display_records(filtered)
            if filtered and input("Set this as current working set? (y/n): ").lower() == "y":
                records = filtered

        elif choice == "5":
            print(f"Available columns: {', '.join(FIELDNAMES)}")
            col = input("Sort by column: ").strip()
            order = input("Descending? (y/n): ").strip().lower() == "y"
            records = sort_data(records, col, descending=order)
            display_records(records)

        elif choice == "6":
            last_summary = summarize_data(records)
            print_summary(last_summary)

        elif choice == "7":
            keyword = input("Enter product name keyword: ").strip()
            results = search_records(records, keyword)
            display_records(results)

        elif choice == "8":
            fname = input(
                f"Press Enter for default filename ({CONFIG['export_csv']}) "
                "or type a new one: "
            ).strip()
            export_csv(records, fname if fname else None)

        elif choice == "9":
            if not last_summary:
                last_summary = summarize_data(records)
                print_summary(last_summary)
            export_summary_txt(last_summary)

        elif choice == "0":
            logging.info("Program exited by user.")
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()
