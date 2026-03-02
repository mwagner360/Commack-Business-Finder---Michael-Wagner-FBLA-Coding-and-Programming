import tkinter as tk
from database import setupDatabase
from gui import BusinessFinderApp
# when running this file, it references the other python files
def main():
    setupDatabase()
    window = tk.Tk()
    app = BusinessFinderApp(window)
    window.mainloop()

if __name__ == "__main__":
    main()