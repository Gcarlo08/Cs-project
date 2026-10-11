
import json
from pathlib import Path

import msal
import requests


# --------------------------------------------------
# MICROSOFT CONFIGURATION
# --------------------------------------------------

# Keep your existing Microsoft Application (client) ID here.
CLIENT_ID = "6d4f4ac2-aaff-437e-a0a6-8bc615ab5ee2"

AUTHORITY = "https://login.microsoftonline.com/common"

SCOPES = [
    "User.Read",
    "Mail.Read"
]

GRAPH_URL = "https://graph.microsoft.com/v1.0"

BASE_DIR = Path(__file__).parent
OUTPUT_FILE = BASE_DIR / "outlook_emails.json"

# Stores the MSAL authentication cache locally.
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
        except (OSError, ValueError):
            print("Warning: Token cache could not be loaded.")
            print("You may need to sign in again.")

    return cache


def save_token_cache(cache):
    """Save the token cache when it changes."""

    if cache.has_state_changed:
        CACHE_FILE.write_text(
            cache.serialize(),
            encoding="utf-8"
        )


# --------------------------------------------------
# SIGN IN
# --------------------------------------------------

def sign_in():
    cache = load_token_cache()

    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache
    )

    # Try to reuse a previously signed-in account.
    accounts = app.get_accounts()

    for account in accounts:
        result = app.acquire_token_silent(
            SCOPES,
            account=account
        )

        if result and "access_token" in result:
            save_token_cache(cache)
            print("Using your saved Microsoft sign-in.")
            return result["access_token"]

    # No usable cached token: ask the user to sign in.
    print("Microsoft sign-in is required.")

    flow = app.initiate_device_flow(scopes=SCOPES)

    if "user_code" not in flow:
        raise RuntimeError(
            f"Could not start sign-in: {flow}"
        )

    print(flow["message"])

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise RuntimeError(
            result.get("error_description", str(result))
        )

    save_token_cache(cache)

    print("Microsoft sign-in successful!")

    return result["access_token"]


# --------------------------------------------------
# RETRIEVE EMAILS
# --------------------------------------------------

def get_emails(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "$top": 25,
        "$select": (
            "id,subject,body,bodyPreview,from,toRecipients,"
            "ccRecipients,receivedDateTime,sentDateTime,"
            "isRead,hasAttachments,importance,conversationId"
        ),
        "$orderby": "receivedDateTime DESC"
    }

    response = requests.get(
        f"{GRAPH_URL}/me/messages",
        headers=headers,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json().get("value", [])


# --------------------------------------------------
# SAVE EMAILS
# --------------------------------------------------

def save_emails(emails):
    OUTPUT_FILE.write_text(
        json.dumps(
            {"value": emails},
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(f"Saved {len(emails)} emails to {OUTPUT_FILE}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    try:
        print("Connecting to Microsoft Outlook...")

        token = sign_in()

        print("Retrieving emails...")

        emails = get_emails(token)

        save_emails(emails)

        for email in emails:
            sender = (
                email.get("from") or {}
            ).get("emailAddress") or {}

            print(
                f'{email.get("subject", "(No subject)")}'
                f' | {sender.get("address", "Unknown sender")}'
            )

    except requests.HTTPError as error:
        print(f"Microsoft Graph returned an error: {error}")

        if error.response is not None:
            print(error.response.text)

    except requests.RequestException as error:
        print(f"Microsoft Graph request failed: {error}")

    except (RuntimeError, OSError, ValueError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
