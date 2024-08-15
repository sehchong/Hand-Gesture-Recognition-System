import tkinter as tk
from tkinter import ttk

class MessageHistoryFrame:
    def __init__(self, root):
        self.root = root
        self.root.title("Message History")

        self.message_history_frame = ttk.Frame(self.root)
        self.message_history_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.message_history_label = ttk.Label(self.message_history_frame, text="Message History", font=("Helvetica", 14))
        self.message_history_label.grid(row=0, column=0, padx=10, pady=(10, 0))

        self.message_treeview = ttk.Treeview(
            self.message_history_frame,
            columns=("Date", "Time", "Message"),
            show="headings",
            selectmode="browse",
            height=10
        )
        self.message_treeview.heading("Date", text="Date", anchor="w")  # Anchor the text to the left
        self.message_treeview.heading("Time", text="Time", anchor="w")  # Anchor the text to the left
        self.message_treeview.heading("Message", text="Message", anchor="w")  # Anchor the text to the left
        self.message_treeview.column("Date", width=150)  # Increase the width
        self.message_treeview.column("Time", width=100)
        self.message_treeview.column("Message", width=450)  # Increase the width
        self.message_treeview.grid(row=1, column=0, padx=10, pady=10)
        self.message_treeview.bind("<Double-1>", self.show_full_message)  # Double-click to show the full message

        self.message_treeview_scrollbar = ttk.Scrollbar(self.message_history_frame, orient="vertical", command=self.message_treeview.yview)
        self.message_treeview_scrollbar.grid(row=1, column=1, sticky="ns")
        self.message_treeview.configure(yscrollcommand=self.message_treeview_scrollbar.set)

        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=("Helvetica", 14))
        self.style.configure("Treeview", font=("Helvetica", 12))

        self.message_label = tk.Label(self.message_history_frame, text="Full Message:", font=("Helvetica", 12))
        self.message_label.grid(row=2, column=0, padx=10, pady=(0, 10), columnspan=2, sticky="w")

        self.full_message_label = tk.Label(self.message_history_frame, text="", font=("Helvetica", 12), wraplength=600, bg="black", fg="white")
        self.full_message_label.grid(row=3, column=0, padx=10, pady=(0, 10), columnspan=2, sticky="w")

        # Create a frame for the buttons
        button_frame = ttk.Frame(self.message_history_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        # Add the "Clear" button to clear the full message label
        self.clear_full_message_button = ttk.Button(button_frame, text="Clear", command=self.clear_full_message)
        self.clear_full_message_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Add the "Clear History" button
        self.clear_history_button = ttk.Button(button_frame, text="Clear History", command=self.clear_history)
        self.clear_history_button.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Center the buttons horizontally
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

    def update_message_history(self):
        # Load your message history data and add it to the Treeview
        try:
            with open("history_messages.txt", "r") as history_file:
                messages = history_file.readlines()
                self.message_treeview.delete(*self.message_treeview.get_children())
                current_date = None  # Track current date
                current_time = None  # Track current time
                for message in messages:
                    message_parts = message.strip().split(": ")
                    if len(message_parts) == 2:
                        message_time, message_content = message_parts
                        date, time = message_time.split(" ")
                        if date != current_date or time != current_time:
                            # Insert Date and Time values only once for each message
                            self.message_treeview.insert("", "end", values=(date, time, message_content))
                            current_date = date
                            current_time = time
                        else:
                            # Insert an empty string for Date and Time to keep the table consistent
                            self.message_treeview.insert("", "end", values=("", "", message_content))
        except FileNotFoundError:
            pass

        self.root.after(1000, self.update_message_history)

    def clear_history(self):
        with open("history_messages.txt", "w") as history_file:
            history_file.truncate(0)
        self.message_treeview.delete(*self.message_treeview.get_children())

    def show_full_message(self, event):
        selected_item = self.message_treeview.selection()[0]
        full_message = self.message_treeview.item(selected_item, "values")[2]
        self.full_message_label.config(text=full_message)

    def clear_full_message(self):
        self.full_message_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    message_history_frame = MessageHistoryFrame(root)
    message_history_frame.update_message_history()
    root.mainloop()
