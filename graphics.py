#Welcome to our super awesome graphics file
#Test Graphics - Basic layout for testing purposes

import tkinter as tk

root = tk.Tk()
root.title("Example")
root.geometry("1280x720")

def on_click():
    label.config(text="Stop clicking me!")

label = tk.Label(root, text="Hello world!")
label.pack(pady=200)

button = tk.Button(root, text="Click Me", command=on_click)
button.pack(pady=100)

root.mainloop()
