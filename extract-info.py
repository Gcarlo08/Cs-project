# Email ranking works in three modes low, medium or high, it is able to read email contents and gather the information from each and use keywords
import json
from pathlib import Path

FILE_PATH = Path(__file__).parent / "mock_emails.json"


def load_emails():
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data["value"]
    except FileNotFoundError:
        print("Error: mock_emails.json was not found.")
        return []
    except (json.JSONDecodeError, KeyError):
        print("Error: The JSON file is invalid or missing 'value'.")
        return []


def save_emails(emails):
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump({"value": emails}, file, indent=2)


def show_inbox(emails):
    inbox = [
        email for email in emails
        if email.get("folder") == "inbox"
    ]

    if not inbox:
        print("\nNo emails found.")
        return

    for email in inbox:
        status = "Unread" if not email.get("is_read", False) else "Read"

        print("-" * 40)
        print("ID:", email.get("id", "Unknown"))
        print("Subject:", email.get("subject", "(No subject)"))
        print("From:", email.get("sender", "Unknown"))
        print("Date:", email.get("received", "Unknown"))
        print("Status:", status)
        print("Importance:", email.get("importance", "normal"))


def view_email(emails):
    email_id = input("Enter email ID: ").strip()

    for email in emails:
        if email.get("id") == email_id:
            print("\nSubject:", email.get("subject", ""))
            print("From:", email.get("sender", ""))
            print("Sender email:", email.get("sender_email", ""))
            print("To:", ", ".join(email.get("recipients", [])))
            print("Date:", email.get("received", ""))
            print("\nMessage:")
            print(email.get("body", ""))
            print("\nAttachments:", email.get("attachments", []))

            email["is_read"] = True
            save_emails(emails)
            print("\nEmail marked as read.")
            return

    print("Email not found.")


def search_emails(emails):
    query = input("Enter search term: ").strip().lower()

    if not query:
        print("Please enter a search term.")
        return

    results = []

    for email in emails:
        searchable_text = " ".join([
            email.get("subject", ""),
            email.get("sender", ""),
            email.get("sender_email", ""),
            email.get("body", "")
        ]).lower()

        if query in searchable_text:
            results.append(email)

    print("\nResults:", len(results))

    for email in results:
        print(
            email.get("id", ""),
            "|",
            email.get("subject", ""),
            "|",
            email.get("sender", "")
        )


def show_unread(emails):
    unread = [
        email for email in emails
        if email.get("folder") == "inbox"
        and not email.get("is_read", False)
    ]

    print("\nUnread emails:", len(unread))

    for email in unread:
        print(email.get("id"), "|", email.get("subject"))


def rank_emails(emails):
    for email in emails:
        points = 0
        sender_email = email.get("sender_email", "").lower()
        email_text = (
            email.get("subject", "") + " " + email.get("body", "")
        ).lower()

        if "@monmouth.edu" in sender_email:
            points += 1

        if "urgent" in email_text:
            points += 1

        email["rank_points"] = points

        if points == 2:
            email["rank"] = "High"
        elif points == 1:
            email["rank"] = "Medium"
        else:
            email["rank"] = "Low"

    save_emails(emails)
    return sorted(emails, key=lambda email: email["rank_points"], reverse=True)


def show_ranked_emails(emails):
    ranked_emails = rank_emails(emails)

    if not ranked_emails:
        print("\nNo emails found.")
        return

    for email in ranked_emails:
        print("-" * 40)
        print("Rank:", email["rank"])
        print("Points:", email["rank_points"])
        print("Subject:", email.get("subject", "(No subject)"))
        print("From:", email.get("sender", "Unknown"))


def main():
    while True:
        emails = load_emails()

        print("\n=== MOCK OUTLOOK ===")
        print("1. View inbox")
        print("2. Read an email")
        print("3. Search emails")
        print("4. Show unread emails")
        print("5. Rank emails")
        print("6. Exit")

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
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Enter 1-6.")


if __name__ == "__main__":
    main()
        