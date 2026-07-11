# Task Automation Tool

## Overview

The **Task Automation Tool** is a Python-based console application designed to automate common repetitive tasks, including file organization, report generation, and email notifications. It helps reduce manual effort by automatically sorting files into categorized folders, creating detailed reports, and optionally sending email summaries of completed tasks.

The application can be used through an interactive menu or by using command-line arguments, making it suitable for both beginners and advanced users. It is built entirely with Python's standard library, so no external packages are required.

This project demonstrates practical implementation of file handling, automation, logging, report generation, command-line programming, and email integration using Python.

---

## Features

### File Organizer

* Automatically organize files into categorized folders based on file type.
* Supported categories include:

  * Images
  * Documents
  * Videos
  * Audio
  * Archives
  * Scripts
  * Others
* Skip hidden files, system files, and directories.
* Automatically rename duplicate files to prevent overwriting.
* Preview file organization using **Dry Run** mode without making any changes.

### Report Generation

* Generate detailed reports after each automation task.
* Export reports in:

  * Text (.txt)
  * CSV (.csv)
* Reports include:

  * Total processed files
  * Moved files
  * Skipped files
  * Failed operations
  * Detailed activity log

### Email Notifications

* Send a summary of completed tasks via email.
* Attach generated reports automatically.
* Securely use Gmail App Passwords through environment variables without storing credentials in the source code.

### Logging

* Record application activity with timestamps.
* Display logs in the console.
* Save logs to a persistent log file for future reference.

### Flexible Execution

The application supports two execution modes:

* Interactive menu for easy navigation.
* Command-line interface for automation and scripting.

### Error Handling

The application safely handles common errors such as:

* Missing folders
* Permission issues
* Missing attachments
* Invalid file paths
* Email delivery failures
* Network-related errors

These errors are reported clearly without causing the application to crash.

---

## Technologies Used

* **Python 3**

### Standard Python Libraries

* `os` – File and directory operations
* `shutil` – File movement and management
* `csv` – CSV report generation
* `logging` – Application logging
* `argparse` – Command-line argument handling
* `smtplib` – Email communication
* `email.message` – Email message creation
* `socket` – Network timeout handling
* `datetime` – Date and time management

No external libraries or third-party packages are required.

---

## Requirements

* Python 3.7 or later
* Windows, macOS, or Linux
* No additional dependencies

**Optional**

To use the email notification feature, configure a Gmail account with an App Password.

---

## Installation

1. Install Python 3 if it is not already installed.

```bash
python --version
```

2. Download or clone the project.

3. Open the project folder in your terminal or command prompt.

4. (Optional) Configure the following environment variables if you want to enable email notifications:

* `EMAIL_SENDER`
* `EMAIL_PASSWORD`
* `EMAIL_RECIPIENT`

No additional installation or package setup is required.

---

## Running the Application

### Interactive Mode

Run the application using:

```bash
python task_automation_tool.py
```

The interactive menu allows you to:

* Organize files
* Preview file organization (Dry Run)
* Generate reports
* Send email summaries

### Command-Line Mode

You can also execute tasks directly from the terminal.

Examples:

```bash
python task_automation_tool.py --organize --dry-run

python task_automation_tool.py --organize --report --report-format csv

python task_automation_tool.py --organize --report --email
```

---

## Available Command-Line Options

| Option            | Description                             |
| ----------------- | --------------------------------------- |
| `--organize`      | Organize files into categorized folders |
| `--source PATH`   | Specify the source folder               |
| `--dry-run`       | Preview actions without moving files    |
| `--report`        | Generate a report after completion      |
| `--report-format` | Choose report format (`txt` or `csv`)   |
| `--email`         | Send a summary email                    |
| `--to ADDRESS`    | Specify the recipient email address     |

---

## Sample Output

```text
=================================================
             TASK AUTOMATION TOOL
=================================================

1. Organize Files
2. Dry Run Preview
3. Generate Report
4. Email Summary
5. Exit

Enter your choice: 2

----------- File Organizer Summary -----------

Processed Files : 6
Moved Files     : 5
Skipped Files   : 1
Failed Files    : 0
```

### Sample Report

```text
AUTOMATION TASK REPORT

Generated: 2026-07-05 14:23:10

Summary
--------------------------------

Processed : 6
Moved     : 5
Skipped   : 1
Failed    : 0

Activity Log

photo.png   → Images      (Moved)
notes.txt   → Documents   (Moved)
.DS_Store   → Skipped
```

---

## Project Structure

```text
Task_Automation_Tool/
│
├── task_automation_tool.py
├── reports/
├── logs/
│   └── automation.log
└── README.md
```

---

## Future Enhancements

Future improvements may include:

* Organize files based on creation or modification date
* Support additional email service providers
* Add continuous folder monitoring (Watch Mode)
* Use a configuration file for user preferences
* Add undo functionality for file organization
* Generate PDF reports
* Develop a graphical user interface using Tkinter
* Create automated unit tests for all modules

---

## Learning Outcomes

This project provided practical experience in:

* Python automation
* File and directory management
* Report generation
* Command-line programming
* Logging and debugging
* Email automation
* Exception handling
* Modular programming
* Building real-world automation tools

---

## Author

**Ardra Rajesh**
Developed as part of the **CODEVEDX Python Programming Internship**.
