"""
Password Generator & Strength Checker
--------------------------------------
Project 2: A command-line tool that generates cryptographically secure
passwords and evaluates the strength of any password against common
security criteria (length, character variety, weak patterns).

Author: Ardra
"""

import string
import secrets
import re
import json
import os
from datetime import datetime

# File used to persist a log of past password generations.
# Only metadata (timestamp, length, score, rating) is stored here —
# actual passwords are never written to disk for security reasons.
HISTORY_FILE = "password_history.json"


def build_character_pool(use_upper=True, use_lower=True,
                          use_digits=True, use_special=True):
    """
    Builds a dictionary of character pools based on which categories
    are enabled. Keeping each category separate (rather than one big
    string) lets generate_password() guarantee at least one character
    from every selected category.
    """
    pools = {}
    if use_upper:
        pools['upper'] = string.ascii_uppercase
    if use_lower:
        pools['lower'] = string.ascii_lowercase
    if use_digits:
        pools['digits'] = string.digits
    if use_special:
        pools['special'] = "!@#$%^&*()-_=+[]{};:,.<>?/"

    return pools


def generate_password(length=12, use_upper=True, use_lower=True,
                       use_digits=True, use_special=True):
    """
    Generates a single cryptographically secure password.

    Uses the `secrets` module (not `random`) because `random` is not
    safe for security-sensitive values — it's predictable and meant
    for simulations/games, not passwords or tokens.

    Guarantees at least one character from each selected category by
    picking one from each pool first, then filling the rest of the
    length from the combined pool, then shuffling so the guaranteed
    characters aren't always in the same position.
    """
    pools = build_character_pool(use_upper, use_lower, use_digits, use_special)

    if not pools:
        raise ValueError("At least one character type must be selected.")

    if length < len(pools):
        raise ValueError(
            f"Password length must be at least {len(pools)} "
            f"to include one of each selected character type."
        )

    # Step 1: guarantee one character from each selected category.
    password_chars = [secrets.choice(chars) for chars in pools.values()]

    # Step 2: fill the remaining length from the combined pool.
    combined_pool = "".join(pools.values())
    remaining_length = length - len(password_chars)
    password_chars += [secrets.choice(combined_pool) for _ in range(remaining_length)]

    # Step 3: shuffle so guaranteed characters aren't predictably placed.
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


def generate_multiple_passwords(count, length=12, use_upper=True,
                                 use_lower=True, use_digits=True,
                                 use_special=True):
    """
    Generates a batch of unique passwords. A set is used to collect
    results so accidental duplicates (rare, but possible with short
    lengths/small pools) are automatically discarded and regenerated.
    """
    passwords = set()
    while len(passwords) < count:
        passwords.add(generate_password(length, use_upper, use_lower,
                                         use_digits, use_special))
    return list(passwords)


def check_password_strength(password):
    """
    Scores a password out of 8 points based on length and character
    variety, then subtracts points for common weaknesses (dictionary
    words, repeated characters, sequential digits). Returns a dict
    with the numeric score, a human-readable rating, and a list of
    actionable feedback tips.
    """
    score = 0
    max_score = 8
    feedback = []

    # --- Length scoring ---
    length = len(password)

    if length >= 16:
        score += 3
    elif length >= 12:
        score += 2
    elif length >= 8:
        score += 1
    else:
        feedback.append("Password is too short (use at least 8 characters).")

    # --- Character variety checks ---
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*()\-_=+\[\]{};:,.<>?/]", password))

    if has_upper:
        score += 1
    else:
        feedback.append("Add uppercase letters.")

    if has_lower:
        score += 1
    else:
        feedback.append("Add lowercase letters.")

    if has_digit:
        score += 1
    else:
        feedback.append("Add numbers.")

    if has_special:
        score += 1
    else:
        feedback.append("Add special characters (e.g. !@#$%).")

    # --- Weak pattern penalties ---
    common_weak_patterns = [
        "password", "123456", "qwerty", "letmein",
        "admin", "welcome", "abc123", "iloveyou"
    ]
    lowered = password.lower()
    for pattern in common_weak_patterns:
        if pattern in lowered:
            score -= 2
            feedback.append(f"Avoid common patterns like '{pattern}'.")
            break

    # Penalize 3+ repeated identical characters in a row (e.g. "aaa").
    if re.search(r"(.)\1{2,}", password):  
        score -= 1
        feedback.append("Avoid repeating the same character multiple times.")

    # Penalize ascending/descending numeric sequences (e.g. "1234").
    if re.search(r"(0123|1234|2345|3456|4567|5678|6789|9876|8765)", password):
        score -= 1
        feedback.append("Avoid sequential numbers.")

    # Clamp score to the valid 0-8 range (penalties could push it negative).
    score = max(0, min(score, max_score))

    # --- Convert numeric score into a human-readable rating ---
    if score <= 2:
        rating = "Weak"
    elif score <= 4:
        rating = "Medium"
    elif score <= 6:
        rating = "Strong"
    else:
        rating = "Very Strong"

    if not feedback:
        feedback.append("Great password! No major weaknesses detected.")

    return {
        "score": score,
        "max_score": max_score,
        "rating": rating,
        "feedback": feedback
    }



def load_history():
    """Loads password generation history from a JSON file (metadata only, no plaintext saved by default)."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history_entry(length, rating, score):
    """
    Appends a record of a generation event to history.
    NOTE: For security, the actual password is NOT stored — only metadata.
    """
    history = load_history()
    history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "length": length,
        "strength_rating": rating,
        "score": score
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def view_history():
    """Displays past generation history (metadata only)."""
    history = load_history()
    if not history:
        print("\nNo history found yet.\n")
        return

    print("\n" + "=" * 60)
    print(f"{'Timestamp':<20}{'Length':<10}{'Rating':<15}{'Score'}")
    print("=" * 60)
    for entry in history:
        print(f"{entry['timestamp']:<20}{entry['length']:<10}"
              f"{entry['strength_rating']:<15}{entry['score']}/8")
    print("=" * 60 + "\n")



def print_strength_report(password, result):
    """Prints a formatted strength report with a visual score bar."""
    bar_length = 20
    # Scale the score (out of max_score) to a 20-character progress bar.
    filled = int((result["score"] / result["max_score"]) * bar_length)
    bar = "#" * filled + "-" * (bar_length - filled)

    print("\n" + "-" * 50)
    print(f"Password       : {password}")
    print(f"Strength       : {result['rating']}")
    print(f"Score          : {result['score']} / {result['max_score']}")
    print(f"[{bar}]")
    print("Feedback:")
    for tip in result["feedback"]:
        print(f"  - {tip}")
    print("-" * 50 + "\n")


def get_yes_no(prompt):
    """Helper to get a validated yes/no answer from the user."""
    while True:
        choice = input(prompt + " (y/n): ").strip().lower()
        if choice in ("y", "yes"):
            return True
        if choice in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


def get_valid_length(prompt="Enter password length: ", minimum=4, maximum=64):
    """Helper to get a validated integer length from the user."""
    while True:
        try:
            length = int(input(prompt))
            if minimum <= length <= maximum:
                return length
            print(f"Please enter a number between {minimum} and {maximum}.")
        except ValueError:
            print("Please enter a valid whole number.")


def menu_generate_password():
    """Handles the 'Generate Password' menu flow."""
    print("\n--- Generate a New Password ---")
    length = get_valid_length()
    use_upper = get_yes_no("Include uppercase letters?")
    use_lower = get_yes_no("Include lowercase letters?")
    use_digits = get_yes_no("Include numbers?")
    use_special = get_yes_no("Include special characters?")

    try:
        password = generate_password(length, use_upper, use_lower,
                                      use_digits, use_special)
    except ValueError as e:
        print(f"\nError: {e}\n")
        return

    result = check_password_strength(password)
    print_strength_report(password, result)
    save_history_entry(length, result["rating"], result["score"])


def menu_generate_multiple():
    """Handles generating a batch of passwords at once."""
    print("\n--- Generate Multiple Passwords ---")
    count = get_valid_length("How many passwords do you want? ", 1, 20)
    length = get_valid_length()
    use_upper = get_yes_no("Include uppercase letters?")
    use_lower = get_yes_no("Include lowercase letters?")
    use_digits = get_yes_no("Include numbers?")
    use_special = get_yes_no("Include special characters?")

    try:
        passwords = generate_multiple_passwords(count, length, use_upper,
                                                 use_lower, use_digits,
                                                 use_special)
    except ValueError as e:
        print(f"\nError: {e}\n")
        return

    print()
    for i, pwd in enumerate(passwords, 1):
        result = check_password_strength(pwd)
        print(f"{i}. {pwd}   [{result['rating']}, {result['score']}/8]")
        save_history_entry(length, result["rating"], result["score"])
    print()


def menu_check_strength():
    """Handles the 'Check Strength of My Own Password' menu flow."""
    print("\n--- Check Password Strength ---")
    password = input("Enter a password to check: ")
    if not password:
        print("Password cannot be empty.\n")
        return
    result = check_password_strength(password)
    print_strength_report(password, result)
    save_history_entry(len(password), result["rating"], result["score"])


def main_menu():
    """Displays the main menu and routes user choices."""
    while True:
        print("=" * 50)
        print("   PASSWORD GENERATOR & STRENGTH CHECKER")
        print("=" * 50)
        print("1. Generate a Secure Password")
        print("2. Generate Multiple Passwords")
        print("3. Check Strength of My Own Password")
        print("4. View Generation History")
        print("5. Exit")
        print("-" * 50)

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            menu_generate_password()
        elif choice == "2":
            menu_generate_multiple()
        elif choice == "3":
            menu_check_strength()
        elif choice == "4":
            view_history()
        elif choice == "5":
            print("\nThank you for using the Password Generator. Stay secure!\n")
            break
        else:
            print("\nInvalid choice. Please select a number from 1 to 5.\n")


if __name__ == "__main__":
    main_menu()
