# File Handling & Data Processing System

## Overview

The **File Handling & Data Processing System** is a Python console application that demonstrates essential file handling and data processing techniques using CSV files. It allows users to manage sales records by loading, viewing, searching, filtering, sorting, summarizing, and exporting data through a simple menu-driven interface.

The application automatically generates sample data when needed and stores all processed information locally. It also maintains detailed logs of user activities, making it useful for learning practical data management concepts in Python.

This project showcases the use of file handling, CSV processing, data analysis, logging, exception handling, and modular programming using only Python's standard library.

---

## Features

### Sales Data Management

* Generate a sample sales dataset automatically.
* Load and process sales records from a CSV file.
* Display records in a clear and organized table.
* Skip invalid or malformed records without interrupting program execution.

### Data Search and Filtering

* Search products by name using partial and case-insensitive matching.
* Filter records based on any available column.
* Support both text-based and numeric filtering.

### Data Sorting

* Sort records by any column.
* Choose ascending or descending order.
* Organize data for easier analysis.

### Data Analysis

Generate useful sales insights, including:

* Total revenue
* Total quantity sold
* Average unit price
* Best-selling product
* Category-wise sales summary

### Export Options

* Export processed records to a new CSV file.
* Generate a formatted text report containing sales summaries.
* Save exported files for future reference.

### Logging

* Record application activities with timestamps.
* Display important logs in the console.
* Store detailed logs in a dedicated log file.

### Error Handling

The application handles common issues safely, including:

* Missing files
* Permission errors
* Invalid or incomplete data
* File reading and writing errors

This ensures the application continues running without unexpected crashes.

---

## Technologies Used

* **Python 3**

### Standard Python Libraries

* `csv` – Reading and writing CSV files
* `os` – File and directory management
* `logging` – Activity logging
* `datetime` – Date and time management
* `statistics` – Data analysis and average calculations

No external libraries or third-party packages are required.

---

## Requirements

* Python 3.7 or later
* Windows, macOS, or Linux
* No additional dependencies
* No internet connection required

---

## Installation

1. Install Python 3 if it is not already installed.

```bash
python --version
```

2. Download or clone the project.

3. Open the project folder in your terminal or command prompt.

No additional installation is required.

---

## Running the Application

Run the following command from the project directory:

```bash
python file_handling_system.py
```

When running the application for the first time:

1. Generate the sample sales dataset.
2. Load the generated CSV file.
3. Use the menu to analyze and manage the data.

The application automatically creates the required folders and files when needed.

---

## Menu Options

```text
1. Generate Sample Data
2. Load Data from CSV
3. View All Records
4. Filter Records
5. Sort Records
6. View Sales Summary
7. Search Products
8. Export Records to CSV
9. Export Summary Report
0. Exit
```

---

## Sample Output

```text
=========================================================
     FILE HANDLING & DATA PROCESSING SYSTEM
=========================================================

1. Generate Sample Data
2. Load Data
3. View Records
...

Enter your choice: 6

--------------- SALES SUMMARY ----------------

Total Records      : 10
Total Quantity     : 500
Total Revenue      : Rs. 123456.00
Average Unit Price : Rs. 1367.80
Top Product        : Study Table

Category Summary

Electronics : Quantity 145 | Revenue Rs. 87654.00
Furniture   : Quantity 30  | Revenue Rs. 33990.00
Stationery  : Quantity 325 | Revenue Rs. 18525.00
```

---

## Project Structure

```text
File_Handling_System/
│
├── file_handling_system.py
├── data/
│   └── sales_data.csv
├── output/
├── logs/
│   └── application.log
└── README.md
```

---

## Future Enhancements

Possible improvements for future versions include:

* Add support for editing and deleting records
* Enable multi-column sorting and filtering
* Generate graphical reports and charts
* Support Excel and JSON file formats
* Create configurable report templates
* Add automated unit testing
* Develop a graphical user interface using Tkinter
* Build a web-based version using Flask

---

## Learning Outcomes

This project provided practical experience in:

* Python file handling
* CSV data processing
* Data filtering and sorting
* Report generation
* Logging
* Exception handling
* Modular programming
* Console application development
* Basic data analysis techniques

---

## Author

**Ardra Rajesh**
Developed as part of the **CODEVEDX Python Programming Internship**.
