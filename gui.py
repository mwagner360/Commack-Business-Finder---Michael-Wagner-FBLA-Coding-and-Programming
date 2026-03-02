# main window for the business finder
# popup windows are in windows.py

import tkinter as tk
from tkinter import ttk, messagebox
import random
import re

from database import loadBusinessList, saveFavorite
from windows import (openDetailsWindow, openReviewForm, openFavoritesWindow,
                     openDealsWindow, openRecsWindow, openAddBusinessWindow,
                     openCategoryReport, openTopRatedReport, exportReviews,
                     doBackup, openHelpWindow)


# tracks the current font size and notifies open windows when it changes
# other files import this so everything scales together

class FontManager:
    curSize = 10
    listeners = []

    @classmethod
    def getSize(cls):
        return cls.curSize

    @classmethod
    def setSize(cls, newSize):
        cls.curSize = max(8, min(18, newSize))
        # keep it in a reasonable range
        for fn in cls.listeners:
            try:
                fn()
            except:
                pass  # window was probably closed

    @classmethod
    def listen(cls, fn):
        cls.listeners.append(fn)

    @classmethod
    def unlisten(cls, fn):
        if fn in cls.listeners:
            cls.listeners.remove(fn)

    @classmethod
    def font(cls, offset=0, bold=False, italic=False):
        # so I don't have to type ("Arial", size, "bold") everywhere
        style = ("bold " if bold else "") + ("italic" if italic else "")
        if style.strip():
            return ("Arial", cls.curSize + offset, style.strip())
        return ("Arial", cls.curSize + offset)


class BusinessFinderApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Commack Business Finder")
        self.root.geometry("1050x680")
        self.root.minsize(900, 550)
        self.currentUser = None

        # show login first, then build the main window
        self.openLogin()
        if self.currentUser is None:
            self.root.destroy()
            return

        self.setupStyles()
        self.createMenuBar()
        self.buildMainLayout()
        self.refreshTable()

        # ctrl +- to change text size and ctrl 0 to reset
        self.root.bind("<Control-equal>", lambda e: self.biggerFont())
        self.root.bind("<Control-plus>", lambda e: self.biggerFont())
        self.root.bind("<Control-minus>", lambda e: self.smallerFont())
        self.root.bind("<Control-0>", lambda e: self.resetFont())

        FontManager.listen(self.onFontChange)


    def setupStyles(self):
        style = ttk.Style()
        style.theme_use("clam")
        sz = FontManager.getSize()

        style.configure("Action.TButton", font=("Arial", sz, "bold"),
                    padding=(10, 5), background="navy", foreground="white")
        style.map("Action.TButton", background=[("active", "dark blue")])

        style.configure("Side.TButton", font=("Arial", sz),
                    padding=(8, 4), background="steel blue", foreground="white")
        style.map("Side.TButton", background=[("active", "dark slate blue")])

        style.configure("Green.TButton", font=("Arial", sz, "bold"),
                    padding=(8, 4), background="sea green", foreground="white")
        style.map("Green.TButton", background=[("active", "dark green")])

        style.configure("Red.TButton", font=("Arial", sz, "bold"),
                    padding=(10, 5), background="firebrick", foreground="white")
        style.map("Red.TButton", background=[("active", "dark red")])

        style.configure("Biz.Treeview", background="white", foreground="black",
                    fieldbackground="white", font=("Arial", sz), rowheight=sz + 16)
        style.configure("Biz.Treeview.Heading", background="navy", foreground="white",
                    font=("Arial", sz, "bold"), padding=5)
        style.map("Biz.Treeview", background=[("selected", "steel blue")],
              foreground=[("selected", "white")])


    def openLogin(self):
        loginWin = tk.Toplevel(self.root)
        loginWin.title("Login")
        loginWin.geometry("360x300")
        loginWin.transient(self.root)
        loginWin.grab_set()
        loginWin.resizable(False, False)

        # center on screen
        loginWin.update_idletasks()
        x = loginWin.winfo_screenwidth() // 2 - 180
        y = loginWin.winfo_screenheight() // 2 - 150
        loginWin.geometry("360x300+" + str(x) + "+" + str(y))

        tk.Label(loginWin, text="Commack Business Finder",
                 font=("Arial", 14, "bold")).pack(pady=(18, 2))
        tk.Label(loginWin, text="Discover local businesses",
                 font=("Arial", 9), fg="gray").pack(pady=(0, 10))

        form = tk.Frame(loginWin)
        form.pack(padx=40)

        tk.Label(form, text="Username:", font=("Arial", 11)).pack(anchor="w")
        nameEntry = tk.Entry(form, width=24, font=("Arial", 12))
        nameEntry.pack(pady=(2, 8), ipady=3)
        nameEntry.focus()

        # math captcha for bot prevention
        num1 = random.randint(2, 15)
        num2 = random.randint(2, 15)
        answer = num1 + num2

        tk.Label(form, text="Bot check: " + str(num1) + " + " + str(num2) + " = ?",
                 font=("Arial", 11, "bold"), fg="dark orange").pack(anchor="w")
        captchaEntry = tk.Entry(form, width=8, font=("Arial", 12), justify="center")
        captchaEntry.pack(pady=(2, 6), anchor="w", ipady=3)

        err = tk.Label(form, text="", font=("Arial", 9), fg="red")
        err.pack(pady=(0, 4))

        def tryLogin(event=None):
            err.config(text="")
            name = nameEntry.get().strip()

            if not name:
                err.config(text="Enter a username")
                return
            if not re.match(r'^[a-zA-Z0-9_]+$', name):
                err.config(text="Letters, numbers, underscores only")
                return
            if len(name) < 2 or len(name) > 20:
                err.config(text="2-20 characters")
                return

            try:
                guess = int(captchaEntry.get().strip())
            except ValueError:
                err.config(text="Type a number")
                captchaEntry.delete(0, tk.END)
                return

            if guess != answer:
                err.config(text="Wrong, try again")
                captchaEntry.delete(0, tk.END)
                return

            self.currentUser = name
            loginWin.destroy()

        nameEntry.bind("<Return>", tryLogin)
        captchaEntry.bind("<Return>", tryLogin)
        ttk.Button(form, text="Log In", command=tryLogin,
                   style="Action.TButton").pack(fill="x", pady=(4, 0))

        self.root.wait_window(loginWin)


    def createMenuBar(self):
        menuBar = tk.Menu(self.root)
        self.root.config(menu=menuBar)

        fileMenu = tk.Menu(menuBar, tearoff=0)
        fileMenu.add_command(label="Add Business", command=lambda: openAddBusinessWindow(self.root, self.refreshTable))
        fileMenu.add_command(label="Backup Database", command=lambda: doBackup(self.root))
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.root.destroy)
        menuBar.add_cascade(label="File", menu=fileMenu)

        toolsMenu = tk.Menu(menuBar, tearoff=0)
        toolsMenu.add_command(label="My Favorites", command=lambda: openFavoritesWindow(self.root, self.currentUser))
        toolsMenu.add_command(label="View Deals", command=lambda: openDealsWindow(self.root))
        toolsMenu.add_command(label="Recommendations", command=lambda: openRecsWindow(self.root, self.currentUser))
        toolsMenu.add_separator()
        toolsMenu.add_command(label="Category Report", command=lambda: openCategoryReport(self.root))
        toolsMenu.add_command(label="Top Rated Report", command=lambda: openTopRatedReport(self.root))
        toolsMenu.add_command(label="Export Reviews CSV", command=lambda: exportReviews(self.root))
        menuBar.add_cascade(label="Tools", menu=toolsMenu)

        accessMenu = tk.Menu(menuBar, tearoff=0)
        accessMenu.add_command(label="Bigger Text  (Ctrl +)", command=self.biggerFont)
        accessMenu.add_command(label="Smaller Text  (Ctrl -)", command=self.smallerFont)
        accessMenu.add_command(label="Reset Text Size  (Ctrl 0)", command=self.resetFont)
        menuBar.add_cascade(label="Accessibility", menu=accessMenu)

        helpMenu = tk.Menu(menuBar, tearoff=0)
        helpMenu.add_command(label="How to Use", command=lambda: openHelpWindow(self.root))
        helpMenu.add_command(label="Shortcuts", command=self.showShortcuts)
        helpMenu.add_separator()
        helpMenu.add_command(label="About", command=self.showAbout)
        menuBar.add_cascade(label="Help", menu=helpMenu)


    def buildMainLayout(self):
        # top header bar
        topBar = tk.Frame(self.root, bg="navy", height=42)
        topBar.pack(fill="x")
        topBar.pack_propagate(False)
        tk.Label(topBar, text="Commack Business Finder", font=("Arial", 13, "bold"), bg="navy", fg="white").pack(side="left", padx=12, pady=8)
        tk.Label(topBar, text="Logged in as " + self.currentUser, font=("Arial", 10), bg="navy", fg="light gray").pack(side="right", padx=12)

        # text size buttons in the top bar
        ttk.Button(topBar, text="A+", style="Side.TButton", command=self.biggerFont).pack(side="right", pady=6)
        ttk.Button(topBar, text="A-", style="Side.TButton", command=self.smallerFont).pack(side="right", padx=(0, 2), pady=6)
        tk.Label(topBar, text="Text:", font=("Arial", 9), bg="navy", fg="light gray").pack(side="right", padx=(8, 2))

        mainArea = tk.Frame(self.root)
        mainArea.pack(fill="both", expand=True, padx=8, pady=6)

        # sidebar with filters and navigation buttons
        sidebar = tk.LabelFrame(mainArea, text="Filters & Actions",
                                font=("Arial", 11, "bold"), width=210)
        sidebar.pack(side="left", fill="y", padx=(0, 6))
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Category:", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(8, 2))
        self.catChoice = tk.StringVar(value="All")
        categories = ["All", "Restaurant", "Cafe", "Retail", "Healthcare", "Services",
                      "Fitness", "Financial", "Automotive", "Public Service", "Non-Profit",
                      "Education", "Entertainment", "Recreation", "Hospitality"]
        ttk.Combobox(sidebar, textvariable=self.catChoice, values=categories,
                     state="readonly", width=18, font=("Arial", 10)).pack(padx=10, pady=(0, 8))
        self.catChoice.trace_add("write", lambda *a: self.refreshTable())

        tk.Label(sidebar, text="Sort By:", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(4, 2))
        self.sortChoice = tk.StringVar(value="name")
        for label, val in [("Name (A-Z)", "name"), ("Highest Rated", "rating_desc"),
                           ("Lowest Rated", "rating_asc"), ("Most Reviews", "reviews_desc")]:
            ttk.Radiobutton(sidebar, text=label, variable=self.sortChoice, value=val, command=self.refreshTable).pack(anchor="w", padx=16)

        tk.Label(sidebar, text="Search:", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(10, 2))
        self.searchBox = tk.StringVar()
        self.searchBox.trace_add("write", lambda *a: self.refreshTable())
        tk.Entry(sidebar, textvariable=self.searchBox, width=18, font=("Arial", 10)).pack(padx=10)

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10, pady=10)

        for txt, cmd, sty in [
            ("My Favorites", lambda: openFavoritesWindow(self.root, self.currentUser), "Side.TButton"),
            ("View Deals", lambda: openDealsWindow(self.root), "Side.TButton"),
            ("Recommended", lambda: openRecsWindow(self.root, self.currentUser), "Green.TButton"),
            ("Reports", lambda: openCategoryReport(self.root), "Side.TButton"),
            ("Add Business", lambda: openAddBusinessWindow(self.root, self.refreshTable), "Side.TButton"),
            ("Help", lambda: openHelpWindow(self.root), "Side.TButton"),
        ]:
            ttk.Button(sidebar, text=txt, command=cmd, style=sty, width=16).pack(padx=10, pady=2)

        # right side is the business table
        rightSide = tk.Frame(mainArea)
        rightSide.pack(side="left", fill="both", expand=True)

        header = tk.Frame(rightSide, bg="navy")
        header.pack(fill="x")
        tk.Label(header, text="Business Directory", font=("Arial", 12, "bold"),
                 bg="navy", fg="white").pack(side="left", padx=10, pady=5)

        tableFrame = tk.Frame(rightSide)
        tableFrame.pack(fill="both", expand=True, pady=(4, 0))

        scroll = ttk.Scrollbar(tableFrame)
        scroll.pack(side="right", fill="y")

        cols = ("Business", "Category", "Rating", "Reviews", "Phone")
        self.bizTable = ttk.Treeview(tableFrame, columns=cols, show="headings",
                                     yscrollcommand=scroll.set, style="Biz.Treeview")
        scroll.config(command=self.bizTable.yview)

        for col in cols:
            self.bizTable.heading(col, text=col)
        self.bizTable.column("Business", width=220)
        self.bizTable.column("Category", width=110)
        self.bizTable.column("Rating", width=80)
        self.bizTable.column("Reviews", width=65)
        self.bizTable.column("Phone", width=110)
        self.bizTable.pack(fill="both", expand=True)

        self.bizTable.bind("<Double-1>", self.viewDetails)
        self.bizTable.bind("<Return>", self.viewDetails)

        # action buttons below the table
        btnRow = tk.Frame(rightSide)
        btnRow.pack(fill="x", pady=6)
        ttk.Button(btnRow, text="View Details", command=self.viewDetails,
                   style="Action.TButton").pack(side="left", padx=4)
        ttk.Button(btnRow, text="Write Review", command=self.writeReview,
                   style="Action.TButton").pack(side="left", padx=4)
        ttk.Button(btnRow, text="Add to Favorites", command=self.addFav,
                   style="Action.TButton").pack(side="left", padx=4)


    def refreshTable(self):
        for row in self.bizTable.get_children():
            self.bizTable.delete(row)

        cat = self.catChoice.get()
        search = self.searchBox.get().strip()

        results = loadBusinessList(
            category=cat if cat != "All" else None,
            searchText=search if search else None,
            sortBy=self.sortChoice.get()
        )

        for bizId, name, category, phone, avgRating, numReviews in results:
            if avgRating > 0:
                rating = str(round(avgRating, 1))
            else:
                rating = "No ratings"
            phoneStr = phone if phone else ""
            self.bizTable.insert("", "end",
                values=(name, category, rating, numReviews, phoneStr), tags=(bizId,))


    def getSelectedId(self):
        sel = self.bizTable.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Pick a business first.")
            return None
        return self.bizTable.item(sel[0])["tags"][0]

    def viewDetails(self, event=None):
        bid = self.getSelectedId()
        if bid:
            openDetailsWindow(self.root, bid, self.currentUser, self.refreshTable)

    def writeReview(self):
        sel = self.bizTable.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Pick a business first.")
            return
        bid = self.bizTable.item(sel[0])["tags"][0]
        name = self.bizTable.item(sel[0])["values"][0]
        openReviewForm(self.root, bid, name, self.currentUser, self.refreshTable)

    def addFav(self):
        sel = self.bizTable.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Pick a business first.")
            return
        bid = self.bizTable.item(sel[0])["tags"][0]
        name = self.bizTable.item(sel[0])["values"][0]
        if saveFavorite(bid, self.currentUser):
            messagebox.showinfo("Saved", "'" + name + "' added to favorites!")
        else:
            messagebox.showinfo("Already Saved", "'" + name + "' is already in your favorites.")

    def biggerFont(self):
        FontManager.setSize(FontManager.getSize() + 1)

    def smallerFont(self):
        FontManager.setSize(FontManager.getSize() - 1)

    def resetFont(self):
        FontManager.setSize(10)

    def onFontChange(self):

        # rebuild styles and reload the table so row height updates
        
        self.setupStyles()
        self.refreshTable()

    def showShortcuts(self):
        messagebox.showinfo("Shortcuts",
            "Enter - View details\nDouble-click - View details\n\n"
            "Ctrl +  -  Bigger text\n"
            "Ctrl -   -  Smaller text\n"
            "Ctrl 0  -  Reset text size\n\n"
            "File --> Add Business / Backup\n"
            "Tools --> Reports, Favorites, Deals\n"
            "Help --> How to Use")

    def showAbout(self):
        messagebox.showinfo("About","Commack Business Finder\n\n FBLA Coding and Programming 2026\n\n\nBuilt by Michael Wagner - Commack High School")