"""
=========================================================================
 PROJECT 5 : TASK AUTOMATION TOOL
 Automations: File Organizer + Report Generator + Email Notifier
 Author     : Ardra
=========================================================================
 A single-file, console-based Python tool that automates repetitive
 tasks. Sections below are kept clearly separated (config, logging,
 file organizer, report generator, email notifier, CLI/menu) so the
 code stays modular and easy to read even though it lives in one file.

 -------------------------------------------------------------------
 SETUP
 -------------------------------------------------------------------
 1. No external packages needed - everything here is Python standard
    library (os, shutil, smtplib, email, csv, logging, argparse).

 2. (Optional, only needed for the email feature) Set your email
    app-password as an environment variable - never hardcode it:
        macOS/Linux:   export EMAIL_PASSWORD="your_app_password"
        Windows (PS):  $env:EMAIL_PASSWORD = "your_app_password"
    For Gmail, generate an App Password at
    https://myaccount.google.com/apppasswords (requires 2-Step Verification).

 3. Run it:
        python task_automation_tool.py                  (interactive menu)
        python task_automation_tool.py --organize --dry-run
        python task_automation_tool.py --organize --report --report-format csv
        python task_automation_tool.py --organize --report --email --to you@example.com
=========================================================================
"""

import os
import sys
import csv
import shutil
import socket
import smtplib
import logging
import argparse
from email.message import EmailMessage
from datetime import datetime


# =========================================================================
# 1. CONFIGURATION  (edit these to reconfigure the whole tool)
# =========================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    # --- File Organizer settings ---
    "source_dir": os.path.join(BASE_DIR, "sample_data"),
    "dry_run_default": False,

    # Maps file extensions -> destination category folder name.
    "category_map": {
        ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
        ".gif": "Images", ".bmp": "Images", ".svg": "Images", ".webp": "Images",
        ".pdf": "Documents", ".docx": "Documents", ".doc": "Documents",
        ".txt": "Documents", ".md": "Documents", ".xlsx": "Documents",
        ".csv": "Documents", ".pptx": "Documents",
        ".mp4": "Videos", ".mov": "Videos", ".avi": "Videos", ".mkv": "Videos",
        ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio",
        ".zip": "Archives", ".rar": "Archives", ".tar": "Archives", ".gz": "Archives",
        ".py": "Scripts", ".js": "Scripts", ".sh": "Scripts", ".json": "Scripts",
    },
    "default_category": "Others",

    # --- Logging ---
    "log_dir": os.path.join(BASE_DIR, "logs"),
    "log_file": "automation.log",

    # --- Reports ---
    "report_dir": os.path.join(BASE_DIR, "reports"),

    # --- Email notifier settings ---
    # Password is NEVER stored here - read from an environment variable
    # so credentials never end up in source control.
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": os.environ.get("EMAIL_SENDER", "your_email@gmail.com"),
    "email_password_env_var": "EMAIL_PASSWORD",
    "default_recipient": os.environ.get("EMAIL_RECIPIENT", "recipient@example.com"),
    "smtp_timeout_seconds": 10,
}


# =========================================================================
# 2. LOGGING SETUP  (every task reports success/failure through this)
# =========================================================================
def get_logger(name="automation"):
    """Return a configured logger that writes to both console and file."""
    os.makedirs(CONFIG["log_dir"], exist_ok=True)
    log_path = os.path.join(CONFIG["log_dir"], CONFIG["log_file"])

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# =========================================================================
# 3. FILE ORGANIZER  (sorts a messy folder into category subfolders)
# =========================================================================
def get_category(filename):
    """Look up which category folder a file belongs in, based on extension."""
    _, ext = os.path.splitext(filename)
    return CONFIG["category_map"].get(ext.lower(), CONFIG["default_category"])


def resolve_name_conflict(destination_path):
    """
    If destination_path already exists, append _1, _2, ... before the
    extension until a free filename is found. Prevents silently
    overwriting an existing file.
    """
    if not os.path.exists(destination_path):
        return destination_path

    folder, filename = os.path.split(destination_path)
    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        candidate = os.path.join(folder, f"{name}_{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def organize_files(source_dir=None, dry_run=None, logger=None):
    """
    Scan source_dir and move each file into a category subfolder.

    Returns {"actions": [...], "summary": {...}}.

    Edge cases handled gracefully (logged, never crash the whole run):
      - source_dir missing               -> FileNotFoundError
      - no permission to read/move a file-> PermissionError
      - source_dir is empty              -> reported, not an error
      - a "file" that's actually a dir   -> skipped, not moved
      - hidden/system files              -> skipped
      - destination filename collision   -> auto-renamed, not overwritten
    """
    source_dir = source_dir or CONFIG["source_dir"]
    dry_run = CONFIG["dry_run_default"] if dry_run is None else dry_run

    actions = []
    summary = {"processed": 0, "moved": 0, "skipped": 0, "failed": 0}

    def log(level, msg):
        if logger:
            getattr(logger, level)(msg)

    if not os.path.isdir(source_dir):
        log("error", f"Source directory not found: {source_dir}")
        actions.append({"file": None, "category": None, "status": "failed",
                         "message": f"Source directory not found: {source_dir}",
                         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        summary["failed"] += 1
        return {"actions": actions, "summary": summary}

    try:
        entries = os.listdir(source_dir)
    except PermissionError:
        log("error", f"Permission denied reading directory: {source_dir}")
        actions.append({"file": None, "category": None, "status": "failed",
                         "message": f"Permission denied reading directory: {source_dir}",
                         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        summary["failed"] += 1
        return {"actions": actions, "summary": summary}

    if not entries:
        log("info", f"Source directory is empty: {source_dir}")

    for entry in entries:
        entry_path = os.path.join(source_dir, entry)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if os.path.isdir(entry_path):
            summary["skipped"] += 1
            actions.append({"file": entry, "category": None, "status": "skipped",
                             "message": "Is a directory, not a file", "timestamp": timestamp})
            continue

        if entry.startswith(".") or entry in ("Thumbs.db", "desktop.ini"):
            summary["skipped"] += 1
            actions.append({"file": entry, "category": None, "status": "skipped",
                             "message": "Hidden/system file", "timestamp": timestamp})
            continue

        summary["processed"] += 1
        category = get_category(entry)
        category_dir = os.path.join(source_dir, category)
        destination = os.path.join(category_dir, entry)

        try:
            if dry_run:
                log("info", f"[DRY RUN] Would move '{entry}' -> {category}/")
                actions.append({"file": entry, "category": category, "status": "dry_run",
                                 "message": f"Would move to {category}/", "timestamp": timestamp})
                summary["moved"] += 1
                continue

            os.makedirs(category_dir, exist_ok=True)
            destination = resolve_name_conflict(destination)
            shutil.move(entry_path, destination)
            log("info", f"Moved '{entry}' -> {category}/{os.path.basename(destination)}")
            actions.append({"file": entry, "category": category, "status": "moved",
                             "message": f"Moved to {category}/{os.path.basename(destination)}",
                             "timestamp": timestamp})
            summary["moved"] += 1

        except PermissionError:
            log("error", f"Permission denied moving '{entry}'")
            actions.append({"file": entry, "category": category, "status": "failed",
                             "message": "Permission denied", "timestamp": timestamp})
            summary["failed"] += 1
        except OSError as e:
            log("error", f"OS error moving '{entry}': {e}")
            actions.append({"file": entry, "category": category, "status": "failed",
                             "message": f"OS error: {e}", "timestamp": timestamp})
            summary["failed"] += 1

    log("info", f"Organize run complete. Summary: {summary}")
    return {"actions": actions, "summary": summary}


# =========================================================================
# 4. REPORT GENERATOR  (turns task results into .txt or .csv reports)
# =========================================================================
def _timestamped_filename(prefix, extension):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}.{extension}"


def generate_text_report(task_name, result, logger=None):
    """Write a human-readable .txt summary report. Returns the path or None."""
    os.makedirs(CONFIG["report_dir"], exist_ok=True)
    path = os.path.join(CONFIG["report_dir"], _timestamped_filename(f"{task_name}_report", "txt"))

    summary = result.get("summary", {})
    actions = result.get("actions", [])

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"AUTOMATION TASK REPORT: {task_name}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write("SUMMARY\n-------\n")
            for key, value in summary.items():
                f.write(f"  {key.capitalize():<12}: {value}\n")

            f.write("\nDETAILS\n-------\n")
            if not actions:
                f.write("  (no actions recorded)\n")
            for a in actions:
                f.write(f"  [{a['timestamp']}] {a.get('file') or '(n/a)':<25} "
                        f"-> {str(a.get('category')):<12} "
                        f"[{a['status'].upper()}] {a['message']}\n")

        if logger:
            logger.info(f"Text report written to {path}")
        return path
    except PermissionError:
        if logger:
            logger.error(f"Permission denied writing report to {path}")
        return None


def generate_csv_report(task_name, result, logger=None):
    """Write a structured .csv report (one row per action). Returns path or None."""
    os.makedirs(CONFIG["report_dir"], exist_ok=True)
    path = os.path.join(CONFIG["report_dir"], _timestamped_filename(f"{task_name}_report", "csv"))

    actions = result.get("actions", [])
    fieldnames = ["timestamp", "file", "category", "status", "message"]

    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for a in actions:
                writer.writerow({k: a.get(k) for k in fieldnames})

        if logger:
            logger.info(f"CSV report written to {path}")
        return path
    except PermissionError:
        if logger:
            logger.error(f"Permission denied writing report to {path}")
        return None


def build_email_summary(task_name, result):
    """Build a short plain-text summary suitable for an email body."""
    summary = result.get("summary", {})
    lines = [f"Automation task '{task_name}' finished.", "", "Summary:"]
    for key, value in summary.items():
        lines.append(f"  {key.capitalize()}: {value}")
    return "\n".join(lines)


# =========================================================================
# 5. EMAIL NOTIFIER  (sends a status email when a task finishes)
# =========================================================================
def send_email(subject, body, to_addr=None, attachment_path=None, logger=None):
    """
    Send a plain-text email, optionally with one file attachment.
    Returns (success: bool, message: str). Never raises.
    """
    to_addr = to_addr or CONFIG["default_recipient"]
    password = os.environ.get(CONFIG["email_password_env_var"])

    def log(level, msg):
        if logger:
            getattr(logger, level)(msg)

    if not password:
        message = (
            f"Email not sent: {CONFIG['email_password_env_var']} environment "
            "variable is not set. See the setup notes at the top of this file."
        )
        log("warning", message)
        return False, message

    if not to_addr or "@" not in to_addr:
        message = f"Email not sent: '{to_addr}' is not a valid email address."
        log("error", message)
        return False, message

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = CONFIG["sender_email"]
    msg["To"] = to_addr
    msg.set_content(body)

    if attachment_path:
        try:
            with open(attachment_path, "rb") as f:
                data = f.read()
            filename = os.path.basename(attachment_path)
            msg.add_attachment(data, maintype="application", subtype="octet-stream",
                                filename=filename)
        except FileNotFoundError:
            message = f"Email not sent: attachment not found at {attachment_path}"
            log("error", message)
            return False, message
        except PermissionError:
            message = f"Email not sent: permission denied reading attachment {attachment_path}"
            log("error", message)
            return False, message

    try:
        with smtplib.SMTP(CONFIG["smtp_server"], CONFIG["smtp_port"],
                           timeout=CONFIG["smtp_timeout_seconds"]) as server:
            server.starttls()
            server.login(CONFIG["sender_email"], password)
            server.send_message(msg)
        message = f"Email sent successfully to {to_addr}."
        log("info", message)
        return True, message

    except smtplib.SMTPAuthenticationError:
        message = "Email not sent: authentication failed. Check sender email/app password."
        log("error", message)
        return False, message
    except smtplib.SMTPConnectError:
        message = f"Email not sent: could not connect to {CONFIG['smtp_server']}."
        log("error", message)
        return False, message
    except (socket.timeout, TimeoutError):
        message = "Email not sent: connection to the SMTP server timed out."
        log("error", message)
        return False, message
    except smtplib.SMTPException as e:
        message = f"Email not sent: SMTP error - {e}"
        log("error", message)
        return False, message
    except OSError as e:
        message = f"Email not sent: network error - {e}"
        log("error", message)
        return False, message


# =========================================================================
# 6. CLI / MENU LAYER  (orchestrates the sections above; no automation
#    logic of its own)
# =========================================================================
def print_summary(task_name, summary):
    print(f"\n--- {task_name} Summary ---")
    for key, value in summary.items():
        print(f"  {key.capitalize():<10}: {value}")
    print()


def handle_report(task_name, result, fmt, logger):
    path = generate_csv_report(task_name, result, logger) if fmt == "csv" \
        else generate_text_report(task_name, result, logger)
    print(f"Report saved to: {path}" if path else "Report could not be saved (see log for details).")
    return path


def handle_email(task_name, result, to_addr, report_path, logger):
    body = build_email_summary(task_name, result)
    success, message = send_email(
        subject=f"Automation Report: {task_name}",
        body=body, to_addr=to_addr, attachment_path=report_path, logger=logger,
    )
    print(message)
    return success


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Task Automation Tool - automates file organization, "
                    "reporting, and email notifications."
    )
    parser.add_argument("--organize", action="store_true", help="Run the file organizer task.")
    parser.add_argument("--source", type=str, default=CONFIG["source_dir"],
                        help="Folder to organize (default: configured sample_data folder).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what the organizer would do without moving any files.")
    parser.add_argument("--report", action="store_true", help="Generate a report file after running tasks.")
    parser.add_argument("--report-format", choices=["txt", "csv"], default="txt",
                        help="Report format (default: txt).")
    parser.add_argument("--email", action="store_true", help="Email a summary of the task results.")
    parser.add_argument("--to", type=str, default=None,
                        help="Recipient email address (overrides config default).")
    return parser


def run_from_args(args, logger):
    if not args.organize:
        print("No task selected. Use --organize, or run with no arguments for the menu.")
        return

    logger.info(f"Starting file organizer on: {args.source}")
    result = organize_files(source_dir=args.source, dry_run=args.dry_run, logger=logger)
    print_summary("File Organizer", result["summary"])

    report_path = None
    if args.report:
        report_path = handle_report("file_organizer", result, args.report_format, logger)

    if args.email:
        handle_email("file_organizer", result, args.to, report_path, logger)


def interactive_menu(logger):
    menu = """
=========================================================
             TASK AUTOMATION TOOL
=========================================================
 1. Organize a folder (real run)
 2. Organize a folder (dry run / preview only)
 3. Generate report from last run
 4. Email summary of last run
 0. Exit
=========================================================
"""
    last_result = None
    last_task_name = "file_organizer"
    last_report_path = None

    while True:
        print(menu)
        choice = input("Enter your choice: ").strip()

        if choice in ("1", "2"):
            source = input(f"Folder to organize [Enter for default: {CONFIG['source_dir']}]: ").strip()
            source = source or CONFIG["source_dir"]
            dry_run = (choice == "2")
            last_result = organize_files(source_dir=source, dry_run=dry_run, logger=logger)
            print_summary("File Organizer" + (" (dry run)" if dry_run else ""), last_result["summary"])

        elif choice == "3":
            if not last_result:
                print("Run an organize task first (option 1 or 2).")
                continue
            fmt = input("Report format - txt or csv? [txt]: ").strip().lower() or "txt"
            fmt = fmt if fmt in ("txt", "csv") else "txt"
            last_report_path = handle_report(last_task_name, last_result, fmt, logger)

        elif choice == "4":
            if not last_result:
                print("Run an organize task first (option 1 or 2).")
                continue
            to_addr = input(f"Recipient email [Enter for default: {CONFIG['default_recipient']}]: ").strip() or None
            handle_email(last_task_name, last_result, to_addr, last_report_path, logger)

        elif choice == "0":
            logger.info("Task Automation Tool exited by user.")
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


def main():
    logger = get_logger()
    logger.info("Task Automation Tool started.")

    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        if len(sys.argv) > 1:
            run_from_args(args, logger)
        else:
            interactive_menu(logger)
    except KeyboardInterrupt:
        logger.warning("Interrupted by user (Ctrl+C). Exiting cleanly.")
        print("\nInterrupted. Exiting cleanly - no partial state left behind.")
        sys.exit(0)


if __name__ == "__main__":
    main()
