# Welcome to our super awesome graphics file

import html
import re
import threading
import webbrowser

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

import extract_info


# Emails currently loaded from outlook_emails.json.
emails = []
displayed_emails = []


def set_status(message):
    status_label.config(text=message)
    root.update_idletasks()


# Authentication dialog state.
auth_dialog = None
auth_instructions = None
auth_copy_button = None
auth_sign_in_code = ""


def show_authentication_message(message):
    """Update the authentication window from the authentication worker thread."""
    root.after(0, lambda: update_authentication_dialog(message))


def update_authentication_dialog(message):
    global auth_sign_in_code

    if auth_dialog is None or not auth_dialog.winfo_exists():
        return

    code_match = re.search(
        r"enter the code\s+([A-Z0-9-]+)",
        message,
        flags=re.IGNORECASE,
    )
    auth_sign_in_code = code_match.group(1) if code_match else ""

    auth_instructions.config(state=tk.NORMAL)
    auth_instructions.delete("1.0", tk.END)
    auth_instructions.insert(tk.END, message)
    auth_instructions.tag_delete("link")
    auth_instructions.tag_configure(
        "link",
        foreground="#0563c1",
        underline=True,
    )

    for match in re.finditer(r"https?://[^\s]+", message):
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        url = match.group(0).rstrip(".,)")
        auth_instructions.tag_add("link", start, end)
        auth_instructions.tag_bind(
            "link",
            "<Button-1>",
            lambda _event, link=url: webbrowser.open(link),
        )

    auth_instructions.config(state=tk.DISABLED)
    auth_copy_button.config(
        state=tk.NORMAL if auth_sign_in_code else tk.DISABLED
    )

    if "successful" in message.lower():
        auth_dialog.after(500, close_authentication_dialog)


def copy_sign_in_code():
    if not auth_sign_in_code or auth_dialog is None:
        return

    auth_dialog.clipboard_clear()
    auth_dialog.clipboard_append(auth_sign_in_code)
    auth_dialog.update()
    set_status("Microsoft sign-in code copied to the clipboard.")


def close_authentication_dialog():
    global auth_dialog, auth_instructions, auth_copy_button

    if auth_dialog is not None and auth_dialog.winfo_exists():
        auth_dialog.grab_release()
        auth_dialog.destroy()

    auth_dialog = None
    auth_instructions = None
    auth_copy_button = None


def open_authentication_dialog():
    global auth_dialog, auth_instructions, auth_copy_button

    auth_dialog = tk.Toplevel(root)
    auth_dialog.title("Microsoft Outlook sign-in")
    auth_dialog.geometry("700x300")
    auth_dialog.minsize(500, 220)
    auth_dialog.transient(root)
    auth_dialog.grab_set()
    auth_dialog.protocol("WM_DELETE_WINDOW", lambda: None)
    tk.Label(
        auth_dialog,
        text="Microsoft sign-in instructions",
        font=("Segoe UI", 12, "bold"),
    ).pack(anchor="w", padx=15, pady=(15, 5))

    auth_instructions = scrolledtext.ScrolledText(
        auth_dialog,
        wrap=tk.WORD,
        font=("Segoe UI", 10),
        height=9,
        cursor="arrow",
    )
    auth_instructions.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    auth_instructions.insert(
        tk.END,
        "Waiting for Microsoft sign-in instructions...",
    )
    auth_instructions.config(state=tk.DISABLED)
    auth_instructions.tag_configure(
        "link",
        foreground="#0563c1",
        underline=True,
    )

    tk.Label(
        auth_dialog,
        text="The window will close automatically after successful sign-in.",
        fg="#555555",
    ).pack(anchor="w", padx=15, pady=(0, 5))

    auth_copy_button = tk.Button(
        auth_dialog,
        text="Copy Sign-in Code",
        command=copy_sign_in_code,
        state=tk.DISABLED,
    )
    auth_copy_button.pack(anchor="e", padx=15, pady=(0, 15))


def authenticate_in_background(max_emails):
    try:
        success = extract_info.sign_in_to_outlook(
            message_callback=show_authentication_message,
            max_emails=max_emails,
        )
        root.after(0, authentication_finished, success, "")
    except Exception as error:
        root.after(0, authentication_finished, False, str(error))


def authentication_finished(success, error_message):
    close_authentication_dialog()

    if not success:
        sync_button.config(state=tk.NORMAL)
        set_status("Outlook sign-in was not completed.")
        retry = messagebox.askretrycancel(
            "Sign-in incomplete",
            "Microsoft sign-in was not completed. Would you like to try again?"
            + (f"\n\n{error_message}" if error_message else ""),
        )
        if retry:
            sync_emails()
        return

    finish_email_sync()


def finish_email_sync():
    global emails

    try:
        emails = extract_info.load_emails()
        ranked_emails = extract_info.rank_emails(emails)
        extract_info.save_emails(ranked_emails)
        emails = ranked_emails
        display_emails(emails, "All emails")
        set_status(f"Loaded {len(emails)} email(s).")
    except Exception as error:
        set_status("Could not load emails.")
        messagebox.showerror("Sync failed", str(error))
    finally:
        sync_button.config(state=tk.NORMAL)


def sync_emails():
    selected_limit = sync_limit_var.get()
    max_emails = None if selected_limit == "All" else int(selected_limit)

    sync_button.config(state=tk.DISABLED)
    set_status(f"Waiting for Microsoft sign-in ({selected_limit} emails)...")
    open_authentication_dialog()
    threading.Thread(
        target=authenticate_in_background,
        args=(max_emails,),
        daemon=True,
    ).start()


def format_email_line(email, include_rank=False):
    prefix = ""
    if include_rank:
        prefix = f"[{email.get('rank', 'Low')} - {email.get('rank_points', 0)} pts]  "

    read_status = "Read" if extract_info.is_email_read(email) else "Unread"
    return (
        f"{prefix}{extract_info.get_subject(email)}  |  "
        f"From: {extract_info.get_sender(email)}  |  {read_status}"
    )


def display_emails(email_list, title):
    global displayed_emails

    displayed_emails = list(email_list)
    email_listbox.delete(0, tk.END)

    for email in displayed_emails:
        email_listbox.insert(
            tk.END,
            format_email_line(email, include_rank=title.startswith("Ranked emails"))
        )

    view_title.config(text=f"{title} ({len(displayed_emails)})")
    set_status(f"Showing {len(displayed_emails)} email(s).")


def ensure_emails_loaded():
    if not emails:
        messagebox.showinfo("No emails", "Click Sync & Load Emails first.")
        return False
    return True


def show_inbox_view():
    if ensure_emails_loaded():
        inbox = [
            email for email in emails
            if extract_info.get_folder(email) == "inbox"
        ]
        display_emails(inbox, "Inbox")


def show_unread_view():
    if ensure_emails_loaded():
        unread = [
            email for email in emails
            if extract_info.get_folder(email) == "inbox"
            and not extract_info.is_email_read(email)
        ]
        display_emails(unread, "Unread emails")


def show_ranked_view():
    if ensure_emails_loaded():
        ranked = extract_info.rank_emails(emails)
        extract_info.save_emails(ranked)
        display_emails(ranked, "Ranked emails")


def search_view():
    if not ensure_emails_loaded():
        return

    query = search_entry.get().strip().lower()
    if not query:
        messagebox.showwarning("Search", "Please enter a search term.")
        return

    results = []
    for email in emails:
        searchable_text = " ".join([
            extract_info.get_subject(email),
            extract_info.get_sender(email),
            extract_info.get_sender_email(email),
            extract_info.get_body(email),
        ]).lower()

        if query in searchable_text:
            results.append(email)

    display_emails(results, f"Search results for '{query}'")


def clean_email_body(body):
    """Convert an HTML email body into readable text for the GUI."""
    if not isinstance(body, str):
        return str(body)

    # Preserve common visual breaks before removing the remaining tags.
    body = re.sub(r"<\s*(br|/p|/div|/li)\s*/?\s*>", "\n", body, flags=re.IGNORECASE)
    body = re.sub(r"<[^>]+>", "", body)
    body = html.unescape(body)
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n\s*\n+", "\n\n", body)
    return body.strip()


def view_selected_email():
    selection = email_listbox.curselection()
    if not selection:
        messagebox.showinfo("Read an email", "Select an email first.")
        return

    email = displayed_emails[selection[0]]
    recipients = ", ".join(extract_info.get_recipients(email))
    attachments = ", ".join(extract_info.get_attachments(email)) or "None"

    details = (
        f"ID: {email.get('id', 'Unknown')}\n"
        f"Subject: {extract_info.get_subject(email)}\n"
        f"From: {extract_info.get_sender(email)}\n"
        f"Sender email: {extract_info.get_sender_email(email)}\n"
        f"To: {recipients or 'None'}\n"
        f"Date: {extract_info.get_received_date(email)}\n"
        f"Importance: {email.get('importance', 'normal')}\n"
        f"Attachments: {attachments}\n\n"
        "Message:\n"
        f"{clean_email_body(extract_info.get_body(email))}"
    )

    details_text.config(state=tk.NORMAL)
    details_text.delete("1.0", tk.END)
    details_text.insert(tk.END, details)
    details_text.config(state=tk.DISABLED)

    # Match extract_info.py: only update the local JSON copy.
    if "isRead" in email:
        email["isRead"] = True
    else:
        email["is_read"] = True
    extract_info.save_emails(emails)

    email_listbox.delete(selection[0])
    email_listbox.insert(
        selection[0],
        format_email_line(email, include_rank=view_title.cget("text").startswith("Ranked"))
    )
    set_status("Email marked as read locally; Outlook was not changed.")


def clear_cached_sign_in():
    extract_info.clear_cached_sign_in()
    set_status("Cached Outlook sign-in cleared.")


def close_application():
    root.destroy()


root = tk.Tk()
root.title("Outlook Email Organizer")
root.geometry("1050x700")
root.minsize(800, 550)
root.configure(bg="#f3f3f3")

header_label = tk.Label(
    root,
    text="Outlook Email Organizer",
    font=("Segoe UI", 16, "bold"),
    bg="#f3f3f3",
    fg="#201f1e",
)
header_label.pack(pady=(15, 5))

controls = tk.Frame(root, bg="#f3f3f3")
controls.pack(fill=tk.X, padx=20, pady=8)

tk.Label(controls, text="Emails to sync:", bg="#f3f3f3").pack(
    side=tk.LEFT,
    padx=(0, 4),
)
sync_limit_var = tk.StringVar(value="25")
sync_limit_menu = ttk.Combobox(
    controls,
    textvariable=sync_limit_var,
    values=("25", "100", "500", "All"),
    state="readonly",
    width=7,
)
sync_limit_menu.pack(side=tk.LEFT, padx=(0, 8))

sync_button = tk.Button(
    controls,
    text="Sync & Load Emails",
    command=sync_emails,
    bg="#0078d4",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    padx=12,
    pady=6,
)
sync_button.pack(side=tk.LEFT, padx=(0, 6))

tk.Button(controls, text="Inbox", command=show_inbox_view).pack(side=tk.LEFT, padx=3)
tk.Button(controls, text="Unread", command=show_unread_view).pack(side=tk.LEFT, padx=3)
tk.Button(controls, text="Rank Emails", command=show_ranked_view).pack(side=tk.LEFT, padx=3)
tk.Button(controls, text="Read Selected", command=view_selected_email).pack(side=tk.LEFT, padx=3)
tk.Button(controls, text="Clear Sign-in", command=clear_cached_sign_in).pack(side=tk.LEFT, padx=3)
tk.Button(controls, text="Exit", command=close_application).pack(side=tk.RIGHT)

search_frame = tk.Frame(root, bg="#f3f3f3")
search_frame.pack(fill=tk.X, padx=20, pady=(0, 8))

tk.Label(search_frame, text="Search:", bg="#f3f3f3").pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame, width=45)
search_entry.pack(side=tk.LEFT, padx=6)
search_entry.bind("<Return>", lambda _event: search_view())
tk.Button(search_frame, text="Search Emails", command=search_view).pack(side=tk.LEFT)

status_label = tk.Label(
    root,
    text="Click Sync & Load Emails to begin.",
    font=("Segoe UI", 9),
    bg="#f3f3f3",
    fg="#555555",
)
status_label.pack(pady=(0, 5))

view_title = tk.Label(
    root,
    text="Emails (0)",
    anchor="w",
    font=("Segoe UI", 11, "bold"),
    bg="#f3f3f3",
)
view_title.pack(fill=tk.X, padx=20)

content = tk.PanedWindow(root, orient=tk.VERTICAL, sashrelief=tk.RAISED, bg="#f3f3f3")
content.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

list_frame = tk.Frame(content, bg="#f3f3f3")
email_listbox = tk.Listbox(
    list_frame,
    font=("Segoe UI", 10),
    bg="white",
    fg="#333333",
    selectbackground="#cce8ff",
    selectforeground="#000000",
    relief="solid",
    borderwidth=1,
)
list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=email_listbox.yview)
email_listbox.configure(yscrollcommand=list_scrollbar.set)
email_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
content.add(list_frame, minsize=180)

details_text = scrolledtext.ScrolledText(
    content,
    wrap=tk.WORD,
    font=("Segoe UI", 10),
    height=10,
    state=tk.DISABLED,
)
content.add(details_text, minsize=120)

root.mainloop()