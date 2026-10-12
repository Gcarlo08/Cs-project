
import json
from pathlib import Path
import msal
import requests


# --------------------------------------------------
# MICROSOFT CONFIGURATION
# --------------------------------------------------
#
# Keep your existing Microsoft Application (client) ID here.
import json
import os
from pathlib import Path

import msal
import requests


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

CLIENT_ID = "6d4f4ac2-aaff-437e-a0a6-8bc615ab5ee2"

AUTHORITY = "https://login.microsoftonline.com/common"

SCOPES = [
    "User.Read",
    "Mail.Read",
]

GRAPH_URL = "https://graph.microsoft.com/v1.0"

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_FILE = BASE_DIR / "outlook_emails.json"
CACHE_FILE = BASE_DIR / "msal_token_cache.json"


# --------------------------------------------------
# TOKEN CACHE
# --------------------------------------------------

def load_token_cache():
    """Load previously cached Microsoft authentication tokens."""

    cache = msal.SerializableTokenCache()

    if CACHE_FILE.exists():
        try:
            cache.deserialize(
                CACHE_FILE.read_text(encoding="utf-8")
            )
        except (OSError, ValueError) as error:
            print(f"Warning: Could not load token cache: {error}")
            print("You may need to sign in again.")

    return cache


def save_token_cache(cache):
    """Save the token cache if it has changed."""

    if cache.has_state_changed:
        try:
            CACHE_FILE.write_text(
                cache.serialize(),
                encoding="utf-8",
            )

            # Restrict file permissions on supported operating systems.
            if os.name == "posix":
                CACHE_FILE.chmod(0o600)

        except OSError as error:
            print(f"Warning: Could not save token cache: {error}")


# --------------------------------------------------
# SIGN IN
# --------------------------------------------------

def sign_in():
    """Authenticate the user and return an access token."""

    if not CLIENT_ID or CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        raise RuntimeError(
            "Set CLIENT_ID to your Microsoft Entra "
            "application's client ID before running."
        )

    cache = load_token_cache()

    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache,
    )

    # Try to reuse an existing signed-in account.
    accounts = app.get_accounts()

    for account in accounts:
        result = app.acquire_token_silent(
            SCOPES,
            account=account,
        )

        if result and result.get("access_token"):
            save_token_cache(cache)
            print("Using your saved Microsoft sign-in.")
            return result["access_token"]

    # No usable cached token: request device-code authentication.
    print("Microsoft sign-in is required.")

    flow = app.initiate_device_flow(scopes=SCOPES)

    if not flow or "user_code" not in flow:
        details = (
            flow.get("error_description", str(flow))
            if flow
            else "No response received from Microsoft."
        )
        raise RuntimeError(
            f"Could not start Microsoft sign-in: {details}"
        )

    print(flow["message"])

    result = app.acquire_token_by_device_flow(flow)

    if not result or "access_token" not in result:
        details = (
            result.get("error_description", str(result))
            if result
            else "No authentication result received."
        )
        raise RuntimeError(f"Microsoft sign-in failed: {details}")

    save_token_cache(cache)

    print("Microsoft sign-in successful!")

    return result["access_token"]


# --------------------------------------------------
# RETRIEVE EMAILS
# --------------------------------------------------

def get_emails(access_token, max_emails=25):
    """
    Retrieve up to max_emails messages from the mailbox.

    Follows Microsoft Graph pagination when additional
    messages are available.
    """

    if max_emails <= 0:
        return []

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    params = {
        "$top": min(max_emails, 100),
        "$select": (
            "id,subject,body,bodyPreview,from,toRecipients,"
            "ccRecipients,receivedDateTime,sentDateTime,"
            "isRead,hasAttachments,importance,conversationId"
        ),
        "$orderby": "receivedDateTime DESC",
    }

    url = f"{GRAPH_URL}/me/messages"
    emails = []

    with requests.Session() as session:
        while url and len(emails) < max_emails:
            response = session.get(
                url,
                headers=headers,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()

            emails.extend(data.get("value", []))

            # The nextLink already contains its query parameters.
            url = data.get("@odata.nextLink")
            params = None

    return emails[:max_emails]


# --------------------------------------------------
# SAVE EMAILS
# --------------------------------------------------

def save_emails(emails):
    """Save retrieved messages to a JSON file."""

    OUTPUT_FILE.write_text(
        json.dumps(
            {"value": emails},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Saved {len(emails)} emails to:")
    print(OUTPUT_FILE)


# --------------------------------------------------
# DISPLAY EMAIL SUMMARIES
# --------------------------------------------------

def display_emails(emails):
    """Print each email's subject and sender."""

    for index, email in enumerate(emails, start=1):
        sender = (
            (email.get("from") or {}).get("emailAddress") or {}
        )

        subject = email.get("subject") or "(No subject)"
        address = sender.get("address") or "Unknown sender"

        print(f"{index}. {subject} | {address}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    try:
        print("Connecting to Microsoft Outlook...")

        token = sign_in()

        print("Retrieving emails...")

        emails = get_emails(
            access_token=token,
            max_emails=25,
        )

        save_emails(emails)

        print("\nRetrieved emails:")
        display_emails(emails)

        print("\nDone.")

    except requests.HTTPError as error:
        response = error.response

        if response is not None:
            print(
                f"Microsoft Graph returned HTTP "
                f"{response.status_code}."
            )

            try:
                details = response.json()
                print(
                    json.dumps(
                        details,
                        indent=2,
                        ensure_ascii=False,
                    )
                )
            except ValueError:
                print(response.text)

        else:
            print(f"HTTP error: {error}")

    except requests.RequestException as error:
        print(f"Microsoft Graph request failed: {error}")

    except (RuntimeError, OSError, ValueError) as error:
        print(f"Error: {error}")

    except Exception as error:
        print(
            f"Unexpected error: {type(error).__name__}: {error}"
        )


if __name__ == "__main__":
    main()