# Password Generator & Strength Checker

## Overview

The **Password Generator & Strength Checker** is a Python console application that helps users create secure passwords and evaluate the strength of existing ones. It generates passwords using Python's `secrets` module, ensuring cryptographically secure randomness suitable for real-world use.

The application also analyzes password strength based on commonly accepted security practices and maintains a local history of password generation and analysis activities. For privacy and security, only metadata such as the date, password length, and strength rating is stored-actual passwords are never saved.

This project demonstrates practical Python programming concepts, including secure random number generation, file handling, regular expressions, input validation, exception handling, and modular programming.

## Features

### Secure Password Generation

* Generate cryptographically secure passwords using Python's `secrets` module.
* Create passwords suitable for personal and professional use.
* Ensure every generated password is unique and highly unpredictable.

### Customizable Password Options

* Choose the desired password length.
* Include or exclude:

  * Uppercase letters
  * Lowercase letters
  * Numbers
  * Special characters
* Guarantee that every selected character category appears at least once in the generated password.

### Multiple Password Generation

* Generate up to 20 unique passwords in a single operation.
* Useful when creating passwords for multiple accounts.

### Password Strength Analysis

Evaluate any password based on several security factors, including:

* Password length
* Character diversity
* Presence of uppercase and lowercase letters
* Numbers and special characters
* Common weak passwords
* Repeated characters
* Sequential number patterns

The application provides:

* A strength score
* A visual progress bar
* Ratings such as:

  * Weak
  * Medium
  * Strong
  * Very Strong
* Suggestions for improving weak passwords.

### Password History

* Maintain a local history of password generation and strength checks.
* Store only metadata, including:

  * Date and time
  * Password length
  * Strength score
  * Overall rating
* Never save the actual password, ensuring user privacy.

### User-Friendly Interface

* Simple menu-driven console application
* Clear prompts and formatted output
* Comprehensive input validation
* Graceful error handling to prevent unexpected crashes

---

## Technologies Used

* **Python 3**

### Standard Python Libraries

* `secrets` – Secure password generation
* `string` – Character sets
* `re` – Pattern matching for password analysis
* `json` – Local history storage
* `os` – File management
* `datetime` – Timestamp generation

No external libraries or third-party packages are required.

---

## Requirements

* Python 3.7 or later
* Windows, macOS, or Linux
* No internet connection required
* No API keys or additional software needed

---

## Installation

1. Install Python 3 if it is not already available.

```bash id="g0pnm4"
python --version
```

2. Download or clone the project.

3. Open the project folder in your terminal or command prompt.

4. No additional dependencies need to be installed.

---

## Running the Application

Run the following command from the project directory:

```bash id="5s0q4e"
python password_generator.py
```

After launching the application, use the interactive menu to:

* Generate secure passwords
* Generate multiple passwords
* Check the strength of an existing password
* View password history

The application automatically creates a JSON file to store password history if it does not already exist.

---

## Sample Output

```text id="rh4wrq"
==================================================
      PASSWORD GENERATOR & STRENGTH CHECKER
==================================================

1. Generate a Secure Password
2. Generate Multiple Passwords
3. Check Password Strength
4. View Password History
5. Exit

Enter your choice: 1

Password : xT9!qLp2@Rw6zK

Strength : Very Strong
Score    : 8 / 8

Feedback:
• Excellent password.
• No significant weaknesses detected.
```

---

## Project Structure

```text id="mhw5s0"
Password_Generator/
│
├── password_generator.py
├── password_history.json
└── README.md
```

---

## Future Enhancements

Potential improvements for future versions include:

* Option to exclude visually similar characters such as **0**, **O**, **1**, and **l**
* Export generated passwords to an encrypted file
* Add an option to clear password history
* Support passphrase-based password generation
* Generate QR codes for secure password sharing
* Add automated unit tests for improved reliability
* Develop a graphical user interface using Tkinter

---

## Learning Outcomes

This project provided practical experience in:

* Secure password generation
* Python file handling
* Regular expressions
* Input validation
* Exception handling
* JSON data storage
* Modular programming
* Console application development
* Basic cybersecurity concepts related to password security

---

## Author

**Ardra Rajesh**

Developed as part of the **CODEVEDX Python Programming Internship**.
