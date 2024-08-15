import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

class ASLDisplayFrame:
    def __init__(self, root):
        # Create the main window
        self.root = root
        self.root.title("American Sign Language Display")
        self.root.geometry("700x670")

        # Create a top Frame for the title
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)

        # Create label for the display page
        title = tk.Label(top_frame, text="Types of American Sign Languages",font=('Times', 21))
        title.grid(row=0, column=1, pady=5)

        # Create a separator line
        separator = ttk.Separator(root, orient="horizontal")
        separator.pack(fill="x", padx=10, pady=10)

        # Create a Frame for the display of ASL
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(fill="y", expand=True)

        # Create an object of the ASL Image
        self.img = ImageTk.PhotoImage(Image.open("./Image/asl.jpg","r"))

        # Create a Label Widget to display the text or Image
        label = tk.Label(bottom_frame, image = self.img)
        label.pack()

# Create and run the ASL Display frame
if __name__ == "__main__":
    root = tk.Tk()
    asl_display_frame = ASLDisplayFrame(root)
    root.mainloop()