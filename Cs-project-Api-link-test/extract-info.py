
import json
import subprocess
import sys
import re
from pathlib import Path

# File containing emails retrieved from Microsoft Outlook
FILE_PATH = Path(__file__).parent / "outlook_emails.json"


# --------------------------------------------------
# OUTLOOK SIGN-IN AND EMAIL EXTRACTION !
# --------------------------------------------------

def sign_in_to_outlook():
    """Authenticate with Outlook before showing the menu."""

    extraction_script = Path(__file__).parent / "outlook-extraction.py"

    if not extraction_script.exists():
        print(f"\nError: {extraction_script.name} was not found.")
        print("Make sure both Python files are in the same folder.")
        return False

    print("\n" + "=" * 45)
    print("MICROSOFT OUTLOOK SIGN-IN")
    print("=" * 45)
    print("Starting Outlook authentication...")
    print("Follow the Microsoft sign-in instructions below.\n")

    try:
        result = subprocess.run(
            [sys.executable, str(extraction_script)],
            check=False
        )

    except Exception as error:
        print(f"\nCould not start Outlook authentication: {error}")
        return False

    if result.returncode != 0:
        print("\nOutlook authentication or extraction failed.")
        print("The email manager will not start.")
        return False

    if not FILE_PATH.exists():
        print("\nError: outlook_emails.json was not created.")
        print("Check your Outlook extraction script.")
        return False

    # Verify that the JSON file contains valid email data.
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data.get("value"), list):
            print("\nError: The JSON file has an unexpected format.")
            return False

    except (json.JSONDecodeError, OSError) as error:
        print(f"\nCould not read Outlook email data: {error}")
        return False

    print("\nOutlook extraction completed successfully!")
    return True


# --------------------------------------------------
# LOAD AND SAVE EMAILS
# --------------------------------------------------

def load_emails():
    """Load emails from the Microsoft Graph JSON response."""

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data.get("value", [])

    except FileNotFoundError:
        print("Error: outlook_emails.json was not found.")
        print("Run Outlook-extraction.py first.")
        return []

    except (json.JSONDecodeError, KeyError) as error:
        print(f"Error loading email data: {error}")
        return []


def save_emails(emails):
    """Save email data back to the JSON file."""

    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {"value": emails},
            file,
            indent=2,
            ensure_ascii=False
        )


# --------------------------------------------------
# MICROSOFT GRAPH FIELD HELPERS
# --------------------------------------------------

def get_sender(email):
    sender = email.get("from") or {}
    address = sender.get("emailAddress") or {}

    return address.get("name") or email.get("sender", "Unknown")


def get_sender_email(email):
    sender = email.get("from") or {}
    address = sender.get("emailAddress") or {}

    return (
        address.get("address")
        or email.get("sender_email", "")
    ).lower()


def get_recipients(email):
    recipients = email.get("toRecipients")

    if recipients is not None:
        result = []

        for recipient in recipients:
            address = recipient.get("emailAddress") or {}
            result.append(address.get("address", ""))

        return result

    return email.get("recipients", [])


def get_body(email):
    body = email.get("body", "")

    if isinstance(body, dict):
        return body.get("content", "")

    return body


def get_subject(email):
    return email.get("subject") or "(No subject)"


def get_received_date(email):
    return email.get("receivedDateTime") or email.get(
        "received", "Unknown"
    )


def is_email_read(email):
    return email.get("isRead", email.get("is_read", False))


def get_folder(email):
    # Standard Graph message responses do not include a folder field.
    return email.get("folder", "inbox")


def get_attachments(email):
    attachments = email.get("attachments", [])

    if attachments:
        return [
            item.get(
                "name",
                item.get("fileName", "Unnamed attachment")
            )
            for item in attachments
        ]

    return []


# --------------------------------------------------
# INBOX
# --------------------------------------------------

def show_inbox(emails):
    inbox = [
        email for email in emails
        if get_folder(email) == "inbox"
    ]

    if not inbox:
        print("\nNo inbox emails found.")
        return

    for email in inbox:
        status = "Unread" if not is_email_read(email) else "Read"

        print("-" * 45)
        print("ID:", email.get("id", "Unknown"))
        print("Subject:", get_subject(email))
        print("From:", get_sender(email))
        print("Sender email:", get_sender_email(email))
        print("Date:", get_received_date(email))
        print("Status:", status)
        print("Importance:", email.get("importance", "normal"))


# --------------------------------------------------
# READ AN EMAIL
# --------------------------------------------------

def view_email(emails):
    email_id = input("Enter email ID: ").strip()

    for email in emails:
        if email.get("id") == email_id:
            print("\nSubject:", get_subject(email))
            print("From:", get_sender(email))
            print("Sender email:", get_sender_email(email))
            print("To:", ", ".join(get_recipients(email)))
            print("Date:", get_received_date(email))
            print("\nMessage:")
            print(get_body(email))
            print("\nAttachments:", get_attachments(email))

            # Update the local copy only.
            if "isRead" in email:
                email["isRead"] = True
            else:
                email["is_read"] = True

            save_emails(emails)

            print("\nEmail marked as read in the local JSON file.")
            print("This does not mark it as read on Outlook itself.")
            return

    print("Email not found.")


# --------------------------------------------------
# SEARCH EMAILS
# --------------------------------------------------

def search_emails(emails):
    query = input("Enter search term: ").strip().lower()

    if not query:
        print("Please enter a search term.")
        return

    results = []

    for email in emails:
        searchable_text = " ".join([
            get_subject(email),
            get_sender(email),
            get_sender_email(email),
            get_body(email)
        ]).lower()

        if query in searchable_text:
            results.append(email)

    print("\nResults:", len(results))

    for email in results:
        print(
            email.get("id", ""),
            "|",
            get_subject(email),
            "|",
            get_sender(email)
        )


# --------------------------------------------------
# UNREAD EMAILS
# --------------------------------------------------

def show_unread(emails):
    unread = [
        email for email in emails
        if get_folder(email) == "inbox"
        and not is_email_read(email)
    ]

    print("\nUnread emails:", len(unread))

    for email in unread:
        print(
            email.get("id", ""),
            "|",
            get_subject(email),
            "|",
            get_sender(email)
        )


# --------------------------------------------------
# EMAIL RANKING
# --------------------------------------------------

def rank_emails(emails):
    """
    Rank emails based on sender, subject, and body.

    High: 3 or more points
    Medium: 1-2 points
    Low: 0 points

    Each matching keyword contributes points.
    """

    high_priority_keywords = [
        "urgent",
        "action required",
        "immediate action",
        "as soon as possible",
        "deadline",
        "time sensitive",
        "critical",
        "overdue",
        "due today",
        "emergency"
    ]

    medium_priority_keywords = [
        "important",
        "please review",
        "response needed",
        "follow up",
        "follow-up",
        "meeting",
        "assignment",
        "application",
        "reminder",
        "due soon"
    ]

    for email in emails:
        points = 0

        sender_email = get_sender_email(email)
        subject = get_subject(email)
        body = get_body(email)

        # Strip HTML tags for keyword matching.
        text = re.sub(
            r"<[^>]+>",
            " ",
            subject + " " + body
        )
        text = re.sub(r"\s+", " ", text).lower()

        # Emails from the specified university domain.
        if sender_email.endswith("@monmouth.edu"):
            points += 1

        # High-priority keyword matches.
        for keyword in high_priority_keywords:
            if keyword in text:
                points += 2

        # Medium-priority keyword matches.
        for keyword in medium_priority_keywords:
            if keyword in text:
                points += 1

        # Respect Microsoft's existing importance flag.
        importance = (
            email.get("importance", "normal") or "normal"
        ).lower()

        if importance == "high":
            points += 1

        email["rank_points"] = points

        if points >= 3:
            email["rank"] = "High"
        elif points >= 1:
            email["rank"] = "Medium"
        else:
            email["rank"] = "Low"

    # Highest-ranked emails appear first.
    return sorted(
        emails,
        key=lambda email: email["rank_points"],
        reverse=True
    )


def show_ranked_emails(emails):
    ranked_emails = rank_emails(emails)

    if not ranked_emails:
        print("\nNo emails found.")
        return

    print("\n=== RANKED EMAILS ===")

    for email in ranked_emails:
        print("-" * 45)
        print("Rank:", email["rank"])
        print("Points:", email["rank_points"])
        print("Subject:", get_subject(email))
        print("From:", get_sender(email))
        print("Sender email:", get_sender_email(email))
        print("Date:", get_received_date(email))
        print("Importance:", email.get("importance", "normal"))


def clear_cached_sign_in():
    """Remove the saved Outlook sign-in token cache."""

    cache_path = Path(__file__).resolve().parent / "msal_token_cache.json"

    if cache_path.exists():
        try:
            cache_path.unlink()
            print(f"Cleared cached Outlook sign-in at: {cache_path}")
            return
        except OSError as error:
            print(f"Warning: Could not clear token cache: {error}")
            return

    print(f"No cached Outlook sign-in found at: {cache_path}")


# --------------------------------------------------
# MAIN MENU
# --------------------------------------------------

def main():
    # Sign in and retrieve emails before displaying options.
    if not sign_in_to_outlook():
        return

    while True:
        emails = load_emails()

        print("\n=== OUTLOOK EMAIL MANAGER ===")
        print("1. View inbox")
        print("2. Read an email")
        print("3. Search emails")
        print("4. Show unread emails")
        print("5. Rank emails")
        print("6. Clear cached Outlook sign-in")
        print("7. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            show_inbox(emails)

        elif choice == "2":
            view_email(emails)

        elif choice == "3":
            search_emails(emails)

        elif choice == "4":
            show_unread(emails)

        elif choice == "5":
            show_ranked_emails(emails)

        elif choice == "6":
            clear_cached_sign_in()

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Enter 1-7.")


if __name__ == "__main__":
    main()
