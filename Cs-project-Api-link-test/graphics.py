# Welcome to our super awesome graphics file

import tkinter as tk
import extract_info 

def load_into_list():
    if extract_info.sign_in_to_outlook():
        emails = extract_info.load_emails()
        
        listbox.delete(0, tk.END)
        
        for email in emails:
            subject = extract_info.get_subject(email)
            sender = extract_info.get_sender(email)
            listbox.insert(tk.END, f"  {subject}   |   From: {sender}")

root = tk.Tk()
root.title("Outlook Organizer")
root.geometry("650x500")
root.config(bg="#f3f3f3") 

header_label = tk.Label(root, text="Outlook Email Organizer", font=("Segoe UI", 16, "bold"), bg="#f3f3f3", fg="#201f1e")
header_label.pack(pady=(15, 5))

sync_button = tk.Button(
    root, 
    text="Sync & Load Emails", 
    command=load_into_list, 
    bg="#0078d4", 
    fg="white", 
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    padx=15,
    pady=6,
    cursor="hand2"
)
sync_button.pack(pady=10)

frame = tk.Frame(root, bg="#f3f3f3")
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

listbox = tk.Listbox(
    frame, 
    width=80, 
    height=18, 
    font=("Segoe UI", 10),
    bg="white",
    fg="#333333",
    selectbackground="#cce8ff",
    selectforeground="#000000",
    relief="solid",
    borderwidth=1
)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.mainloop()