# Student Management System

The **Student Management System** is a Python-based console application designed to simplify the management of student records. It provides an easy-to-use, menu-driven interface for handling student information, attendance, marks, and performance analysis.

The application stores all data locally using JSON files, making it lightweight, portable, and simple to use without requiring any external database or third-party libraries.

This project demonstrates the practical use of Python concepts such as functions, classes, file handling, data validation, exception handling, and modular programming.

## Features

### Student Management

* Add new student records
* View all students in a formatted table
* Update existing student information
* Delete student records
* Search students by ID or name
* Validate important inputs such as age, email, and phone number

### Attendance Management

* Mark students as **Present**, **Absent**, or **Leave**
* Track attendance history
* Calculate attendance percentage automatically
* Display alerts for students with attendance below **75%**

### Marks & Grade Management

* Record marks for five subjects
* Calculate average marks automatically
* Generate grades from **A+** to **F**
* View complete academic performance

### Performance Analytics

* Predict student performance using rule-based analysis
* Generate personalized study recommendations
* Display a leaderboard based on academic performance
* Award achievement badges and ranking medals
* Sort students by name, department, or average marks
* View department-wise and grade-wise statistics

### Additional Features

* Clean and user-friendly console interface
* Proper input validation and exception handling
* Automatic creation of required JSON files
* Persistent data storage without any external database
* Modular and easy-to-understand code structure


## Technologies Used

* **Python 3**
* Standard Python Libraries:

  * **json** – Store and retrieve data
  * **os** – File and directory operations
  * **datetime** – Date and time management
  * **collections.defaultdict** – Statistical analysis and data grouping

---

## Requirements

* Python **3.7** or later
* No additional packages or dependencies
* Compatible with:

  * Windows
  * macOS
  * Linux

---

## Installation

1. Install Python 3 if it is not already installed.

   ```bash
   python --version
   ```

2. Download or clone this repository.

3. Open the project folder in your terminal or command prompt.

4. No additional installation is required because the project uses only Python's standard library.

---

##  Running the Project

Navigate to the project directory and run:

```bash
python student_management.py
```

When the application runs for the first time, it automatically creates the following files to store data:

* `students.json`
* `attendance.json`
* `marks.json`

These files ensure that all records are saved and available the next time the program is launched.

---

## Sample Output

```text
╔══════════════════════════════════════════════════════════╗
║         🎓 STUDENT MANAGEMENT SYSTEM 🎓                  ║
║          Python Console Application v1.0                ║
╚══════════════════════════════════════════════════════════╝

1. Student Management
2. Attendance Management
3. Marks Management
4. Analytics & Performance
0. Exit

Choose an option: 4

────────────────────────────────────────────────────────────

ID      Name              Avg Marks   Attendance   Prediction
--------------------------------------------------------------
S001    Ardra Rajesh         88.4        92.0%      Excellent
S002    Komal Verma          58.2        68.5%      Needs Improvement
```

## Project Structure

```text
Student_Management_System/
│
├── student_management.py
├── students.json
├── attendance.json
├── marks.json
└── README.md
```

## Future Enhancements

Some improvements planned for future versions include:

* Implement machine learning for performance prediction
* Export reports to CSV and Excel
* Add support for multiple classes and semesters
* Develop a graphical user interface (GUI) using Tkinter
* Create a web-based version using Flask or Django
* Add user authentication and login functionality
* Generate printable student reports
* Improve test coverage with unit testing

## Learning Outcomes

This project helped strengthen practical knowledge of:

* Python programming
* Object-Oriented Programming (OOP)
* File handling using JSON
* Functions and modular programming
* Exception handling
* Input validation
* Data processing
* Console application development

## Author

**Ardra Rajesh**
Developed as part of the **CODEVEDX Python Programming Internship**.

