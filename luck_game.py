import tkinter as tk
from tkinter import messagebox
import random

def check_luck():
    # Generate random number between 0 and 1
    result = random.random()
    
    # 75% chance of losing (if result <= 0.75)
    if result <= 0.75:
        messagebox.showinfo("Result", "You lost!")
    else:
        messagebox.showinfo("Result", "You won!")

# Create main window
window = tk.Tk()
window.title("Luck Game")
window.geometry("200x100")

# Create and place button
button = tk.Button(window, text="Good Luck!", command=check_luck)
button.pack(expand=True)

# Start the application
window.mainloop()