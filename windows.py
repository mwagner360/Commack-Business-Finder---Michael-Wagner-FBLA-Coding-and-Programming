# all the popup/dialog windows

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import csv

from database import (lookupBusiness, saveReview, loadReviews, saveFavorite,
                      loadFavorites, removeFavorite, loadDeals, saveBusiness,
                      categoryBreakdown, topRatedList, dumpAllReviews,
                      findRecommendations, makeBackup)

# can't import FontManager at the top because gui.py imports this file too
# lazy import inside functions avoids any problems

def getFM():
    from gui import FontManager
    return FontManager


# business details popup

def openDetailsWindow(parent, bid, currentUser, refreshCallback):
    info = lookupBusiness(bid)
    if not info:
        return

    name, category, address, phone, email, website, desc, verified = info
    fm = getFM()

    win = tk.Toplevel(parent)
    win.title(name)
    win.geometry("620x520")
    win.minsize(460, 360)

    # scrollable frame setup
    canvas = tk.Canvas(win, highlightthickness=0)
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw", width=600)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    titleText = name
    if verified:
        titleText += "  (Verified)"
    tk.Label(inner, text=titleText, font=fm.font(5, bold=True),
             wraplength=560, anchor="w").pack(pady=(12, 2), padx=16, anchor="w")
    tk.Label(inner, text=category, font=fm.font(1, italic=True),
             fg="gray").pack(padx=16, anchor="w")

    # contact info section
    infoFrame = tk.LabelFrame(inner, text="Details", font=fm.font(bold=True))
    infoFrame.pack(fill="x", padx=16, pady=(8, 4))

    for label, value in [("Address", address), ("Phone", phone),
                         ("Email", email), ("Website", website)]:
        if value:
            row = tk.Frame(infoFrame)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=label + ":", font=fm.font(bold=True),
                     width=8, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=fm.font()).pack(side="left")

    if desc:
        tk.Label(infoFrame, text=desc, font=fm.font(),
                 wraplength=540).pack(padx=10, pady=(2, 6), anchor="w")

    # show deals if this business has any
    deals = loadDeals(bid)
    if deals:
        dealFrame = tk.LabelFrame(inner, text="Active Deals",
                                  font=fm.font(bold=True), fg="dark green")
        dealFrame.pack(fill="x", padx=16, pady=4)
        for deal in deals:
            txt = "  " + deal[0] + " - " + deal[1] + " (" + str(deal[2]) + "% off)  |  Expires: " + deal[3]
            tk.Label(dealFrame, text=txt, font=fm.font(),
                     wraplength=540).pack(padx=10, pady=2, anchor="w")

    # reviews section
    revFrame = tk.LabelFrame(inner, text="Reviews", font=fm.font(bold=True))
    revFrame.pack(fill="both", expand=True, padx=16, pady=(4, 8))

    reviews = loadReviews(bid)
    if reviews:
        for reviewer, rating, comment, date in reviews:
            card = tk.Frame(revFrame, relief="groove", bd=1)
            card.pack(fill="x", padx=8, pady=3)

            topRow = tk.Frame(card)
            topRow.pack(fill="x", padx=8, pady=(4, 1))
            tk.Label(topRow, text=reviewer + " - " + str(rating) + "/5",
                     font=fm.font(bold=True)).pack(side="left")
            tk.Label(topRow, text=date, font=fm.font(-2), fg="gray").pack(side="right")

            tk.Label(card, text=comment, font=fm.font(), wraplength=520,
                     justify="left", anchor="w").pack(padx=8, pady=(0, 5), anchor="w")
    else:
        tk.Label(revFrame, text="No reviews yet", font=fm.font(), fg="gray").pack(pady=8)

    # buttons at the bottom
    btns = tk.Frame(inner)
    btns.pack(pady=10)
    ttk.Button(btns, text="Write Review", style="Action.TButton",
               command=lambda: [win.destroy(), openReviewForm(parent, bid, name, currentUser, refreshCallback)]
               ).pack(side="left", padx=4)
    ttk.Button(btns, text="Favorite", style="Green.TButton",
               command=lambda: quickFav(bid, name, currentUser)).pack(side="left", padx=4)
    ttk.Button(btns, text="Close", command=win.destroy).pack(side="left", padx=4)


def quickFav(bid, name, user):
    if saveFavorite(bid, user):
        messagebox.showinfo("Saved", "'" + name + "' added to favorites!")
    else:
        messagebox.showinfo("Already Saved", "'" + name + "' is already in your favorites.")


# write a review

def openReviewForm(parent, bid, bizName, currentUser, refreshCallback):
    win = tk.Toplevel(parent)
    win.title("Review - " + bizName)
    win.geometry("400x370")
    win.resizable(False, False)
    fm = getFM()

    tk.Label(win, text="Review: " + bizName,
             font=fm.font(2, bold=True), wraplength=360).pack(pady=(12, 8))

    tk.Label(win, text="Rating:", font=fm.font()).pack()
    ratingVar = tk.DoubleVar(value=5.0)
    ratingLabel = tk.Label(win, text="5.0 / 5", font=fm.font(3, bold=True))
    ratingLabel.pack()

    def sliderMoved(val):
        ratingLabel.config(text=str(round(float(val), 1)) + " / 5")

    tk.Scale(win, from_=1, to=5, orient="horizontal", variable=ratingVar,
             resolution=0.5, length=220, command=sliderMoved).pack(pady=(0, 6))

    tk.Label(win, text="Comment:", font=fm.font()).pack(anchor="w", padx=34)
    commentBox = tk.Text(win, height=5, width=36, font=fm.font(), wrap="word")
    commentBox.pack(padx=34, pady=(2, 4))
    commentBox.focus()

    err = tk.Label(win, text="", font=("Arial", 9), fg="red")
    err.pack()

    def submit():
        err.config(text="")
        text = commentBox.get("1.0", "end").strip()

        if not text:
            err.config(text="Write something")
            return
        if len(text) < 5:
            err.config(text="Too short")
            return
        # reject input that's just one repeated character
        if len(set(text.replace(" ", ""))) < 2:
            err.config(text="Write a real review")
            return

        if saveReview(bid, currentUser, ratingVar.get(), text):
            messagebox.showinfo("Done", "Review posted!")
            win.destroy()
            refreshCallback()
        else:
            err.config(text="Something went wrong")

    ttk.Button(win, text="Post Review", command=submit,
               style="Action.TButton").pack(pady=(6, 10))


# favorites window

def openFavoritesWindow(parent, currentUser):
    win = tk.Toplevel(parent)
    win.title("My Favorites")
    win.geometry("540x340")

    tk.Label(win, text=currentUser + "'s Favorites",
             font=("Arial", 13, "bold")).pack(pady=(10, 6))

    tableFrame = tk.Frame(win)
    tableFrame.pack(fill="both", expand=True, padx=12, pady=4)
    scrollbar = ttk.Scrollbar(tableFrame)
    scrollbar.pack(side="right", fill="y")

    favTable = ttk.Treeview(tableFrame, columns=("Business", "Category", "Date Added"),
                            show="headings", yscrollcommand=scrollbar.set)
    scrollbar.config(command=favTable.yview)
    favTable.heading("Business", text="Business")
    favTable.heading("Category", text="Category")
    favTable.heading("Date Added", text="Date Added")
    favTable.column("Business", width=200)
    favTable.column("Category", width=120)
    favTable.column("Date Added", width=100)
    favTable.pack(fill="both", expand=True)

    for fav in loadFavorites(currentUser):
        favTable.insert("", "end", values=fav[:3], tags=(fav[3],))

    def removeSelected():
        sel = favTable.selection()
        if not sel:
            return
        fid = favTable.item(sel[0])["tags"][0]
        if messagebox.askyesno("Confirm", "Remove from favorites?"):
            removeFavorite(fid)
            favTable.delete(sel[0])

    btns = tk.Frame(win)
    btns.pack(pady=8)
    ttk.Button(btns, text="Remove", command=removeSelected,
               style="Red.TButton").pack(side="left", padx=4)
    ttk.Button(btns, text="Close", command=win.destroy).pack(side="left", padx=4)


# recommendations

def openRecsWindow(parent, currentUser):
    win = tk.Toplevel(parent)
    win.title("Recommended For You")
    win.geometry("580x440")

    tk.Label(win, text="Recommended For You",
             font=("Arial", 13, "bold")).pack(pady=(10, 2))
    tk.Label(win, text="Based on your favorites and reviews",
             font=("Arial", 9), fg="gray").pack(pady=(0, 8))

    # scrollable container
    outer = tk.Frame(win)
    outer.pack(fill="both", expand=True, padx=12, pady=4)
    canvas = tk.Canvas(outer, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw", width=535)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    recs = findRecommendations(currentUser, limit=8)

    if not recs:
        tk.Label(inner, text="No recommendations yet - try favoriting some businesses!",
                 font=("Arial", 11), fg="gray").pack(pady=30)
    else:
        for bizId, name, cat, desc, avgRating, numReviews in recs:
            card = tk.Frame(inner, relief="ridge", bd=2, padx=10, pady=6)
            card.pack(fill="x", padx=6, pady=4)

            topRow = tk.Frame(card)
            topRow.pack(fill="x")
            tk.Label(topRow, text=name, font=("Arial", 11, "bold")).pack(side="left")
            tk.Label(topRow, text=cat, font=("Arial", 9, "italic"), fg="gray").pack(side="right")

            if avgRating > 0:
                ratingText = str(round(avgRating, 1)) + " / 5  (" + str(numReviews) + " reviews)"
            else:
                ratingText = "No ratings yet"
            tk.Label(card, text=ratingText, font=("Arial", 10), anchor="w").pack(fill="x")

            if desc:
                tk.Label(card, text=desc, font=("Arial", 9), fg="gray",
                         anchor="w", wraplength=500).pack(fill="x", pady=(2, 0))

            bizDeals = loadDeals(bizId)
            if bizDeals:
                tk.Label(card, text="Deal: " + bizDeals[0][0] + " - " + bizDeals[0][1],
                         font=("Arial", 9, "bold"), fg="dark green",
                         anchor="w").pack(fill="x", pady=(2, 0))

            ttk.Button(card, text="Favorite", style="Green.TButton",
                       command=lambda b=bizId, n=name, u=currentUser: quickFav(b, n, u)
                       ).pack(anchor="w", pady=(4, 0))

    ttk.Button(win, text="Close", command=win.destroy).pack(pady=8)


# deals browser

def openDealsWindow(parent):
    win = tk.Toplevel(parent)
    win.title("Deals & Coupons")
    win.geometry("720x380")

    tk.Label(win, text="Active Deals", font=("Arial", 13, "bold")).pack(pady=(10, 6))

    tableFrame = tk.Frame(win)
    tableFrame.pack(fill="both", expand=True, padx=12, pady=4)
    scrollbar = ttk.Scrollbar(tableFrame)
    scrollbar.pack(side="right", fill="y")

    cols = ("Business", "Deal", "Details", "Discount", "Expires")
    table = ttk.Treeview(tableFrame, columns=cols, show="headings", yscrollcommand=scrollbar.set)
    scrollbar.config(command=table.yview)
    for col in cols:
        table.heading(col, text=col)
    table.column("Business", width=150)
    table.column("Deal", width=110)
    table.column("Details", width=200)
    table.column("Discount", width=70)
    table.column("Expires", width=90)
    table.pack(fill="both", expand=True)

    for deal in loadDeals():
        table.insert("", "end", values=(deal[0], deal[1], deal[2], str(deal[3]) + "% off", deal[4]))

    ttk.Button(win, text="Close", command=win.destroy).pack(pady=8)


# add a business

def openAddBusinessWindow(parent, refreshCallback):
    win = tk.Toplevel(parent)
    win.title("Add Business")
    win.geometry("420x470")
    win.resizable(False, False)

    tk.Label(win, text="Add a New Business",
             font=("Arial", 13, "bold")).pack(pady=(10, 2))
    tk.Label(win, text="* = required", font=("Arial", 9), fg="gray").pack(pady=(0, 6))

    form = tk.Frame(win)
    form.pack(padx=24, pady=4)

    fields = {}
    fieldList = [("Name *", "name"), ("Category *", "category"), ("Address", "address"),
                 ("Phone", "phone"), ("Email", "email"), ("Website", "website"),
                 ("Description", "description")]

    for i, (label, key) in enumerate(fieldList):
        tk.Label(form, text=label, font=("Arial", 10),
                 anchor="w").grid(row=i, column=0, sticky="w", pady=3, padx=(0, 8))

        if key == "description":
            fields[key] = tk.Text(form, height=3, width=24, font=("Arial", 10))
        elif key == "category":
            fields[key] = ttk.Combobox(form, width=22, font=("Arial", 10),
                values=["Restaurant", "Cafe", "Retail", "Healthcare", "Services",
                        "Fitness", "Financial", "Automotive", "Entertainment",
                        "Education", "Other"])
        else:
            fields[key] = tk.Entry(form, width=24, font=("Arial", 10))
        fields[key].grid(row=i, column=1, pady=3)

    err = tk.Label(win, text="", font=("Arial", 9), fg="red")
    err.pack(pady=(4, 0))

    def submit():
        err.config(text="")
        name = fields["name"].get().strip()
        cat = fields["category"].get().strip()

        if not name:
            err.config(text="Name is required")
            return
        if not cat:
            err.config(text="Pick a category")
            return

        # validate phone if it is given
        phone = fields["phone"].get().strip()
        if phone:
            digits = re.sub(r'[\s\-\(\)\.]+', '', phone)
            if not digits.isdigit() or len(digits) < 7 or len(digits) > 11:
                err.config(text="Bad phone number")
                return

        # validate email if it is given
        email = fields["email"].get().strip()
        if email and not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
            err.config(text="Bad email format")
            return

        website = fields["website"].get().strip()
        if website and not website.startswith("http"):
            website = "https://" + website

        addr = fields["address"].get().strip()
        desc = fields["description"].get("1.0", "end").strip()

        result = saveBusiness(name, cat, addr or None, phone or None,
                              email or None, website or None, desc or None)
        if result:
            messagebox.showinfo("Added", "'" + name + "' has been added!")
            win.destroy()
            refreshCallback()
        else:
            err.config(text="Could not save")

    btns = tk.Frame(win)
    btns.pack(pady=8)
    ttk.Button(btns, text="Add", command=submit, style="Action.TButton").pack(side="left", padx=4)
    ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="left", padx=4)


# reports

def openCategoryReport(parent):
    win = tk.Toplevel(parent)
    win.title("Category Report")
    win.geometry("580x420")

    tk.Label(win, text="Businesses by Category",
             font=("Arial", 13, "bold")).pack(pady=(10, 6))

    tableFrame = tk.Frame(win)
    tableFrame.pack(fill="both", expand=True, padx=12, pady=4)
    scrollbar = ttk.Scrollbar(tableFrame)
    scrollbar.pack(side="right", fill="y")

    cols = ("Category", "Count", "Avg Rating", "Reviews")
    table = ttk.Treeview(tableFrame, columns=cols, show="headings", yscrollcommand=scrollbar.set)
    scrollbar.config(command=table.yview)
    for col in cols:
        table.heading(col, text=col)
    table.column("Category", width=150)
    table.column("Count", width=80)
    table.column("Avg Rating", width=80)
    table.column("Reviews", width=80)
    table.pack(fill="both", expand=True)

    stats = categoryBreakdown()
    totalBiz = 0
    totalRev = 0
    exportRows = []

    for catName, count, avgRating, numReviews in stats:
        if avgRating > 0:
            ratingText = str(round(avgRating, 1))
        else:
            ratingText = "N/A"
        table.insert("", "end", values=(catName, count, ratingText, numReviews))
        exportRows.append((catName, count, ratingText, numReviews))
        totalBiz += count
        totalRev += numReviews

    tk.Label(win, text="Total: " + str(totalBiz) + " businesses  |  " + str(totalRev) + " reviews",
             font=("Arial", 10, "bold")).pack(pady=4)

    btns = tk.Frame(win)
    btns.pack(pady=6)
    ttk.Button(btns, text="Export CSV", style="Action.TButton",
               command=lambda: saveCsv("category_report.csv",
                   ["Category", "Count", "Avg Rating", "Reviews"], exportRows)
               ).pack(side="left", padx=4)
    ttk.Button(btns, text="Close", command=win.destroy).pack(side="left", padx=4)


def openTopRatedReport(parent):
    win = tk.Toplevel(parent)
    win.title("Top Rated")
    win.geometry("600x440")

    tk.Label(win, text="Top Rated Businesses",
             font=("Arial", 13, "bold")).pack(pady=(10, 4))

    # filter row at the top
    filterRow = tk.Frame(win)
    filterRow.pack(fill="x", padx=12, pady=(0, 6))

    tk.Label(filterRow, text="Category:", font=("Arial", 10)).pack(side="left", padx=(0, 4))
    filterCat = tk.StringVar(value="All")
    ttk.Combobox(filterRow, textvariable=filterCat, state="readonly", width=14, font=("Arial", 10),
                 values=["All", "Restaurant", "Cafe", "Retail", "Healthcare",
                         "Services", "Fitness", "Financial"]).pack(side="left", padx=(0, 8))

    tk.Label(filterRow, text="Show top:", font=("Arial", 10)).pack(side="left", padx=(6, 4))
    limitVar = tk.StringVar(value="15")
    ttk.Combobox(filterRow, textvariable=limitVar, values=["5", "10", "15", "25"],
                 state="readonly", width=4, font=("Arial", 10)).pack(side="left")

    tableFrame = tk.Frame(win)
    tableFrame.pack(fill="both", expand=True, padx=12, pady=4)
    scrollbar = ttk.Scrollbar(tableFrame)
    scrollbar.pack(side="right", fill="y")

    cols = ("#", "Business", "Category", "Rating", "Reviews")
    table = ttk.Treeview(tableFrame, columns=cols, show="headings", yscrollcommand=scrollbar.set)
    scrollbar.config(command=table.yview)
    for col in cols:
        table.heading(col, text=col)
    table.column("#", width=35)
    table.column("Business", width=190)
    table.column("Category", width=100)
    table.column("Rating", width=60)
    table.column("Reviews", width=60)
    table.pack(fill="both", expand=True)

    def reload(*args):
        for item in table.get_children():
            table.delete(item)
        cat = filterCat.get()
        limit = int(limitVar.get())
        for rank, (name, cat2, rating, numReviews) in enumerate(topRatedList(limit, cat if cat != "All" else None), 1):
            table.insert("", "end", values=(rank, name, cat2, str(round(rating, 1)), numReviews))

    filterCat.trace_add("write", reload)
    limitVar.trace_add("write", reload)
    reload()

    ttk.Button(win, text="Close", command=win.destroy).pack(pady=8)


# csv export

def saveCsv(defaultName, headers, data):
    path = filedialog.asksaveasfilename(defaultextension=".csv",
        filetypes=[("CSV", "*.csv")], initialfile=defaultName)
    if not path:
        return
    try:
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in data:
                writer.writerow(row)
        messagebox.showinfo("Exported", "Saved to " + path)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def exportReviews(parent):
    saveCsv("reviews.csv", ["Business", "User", "Rating", "Comment", "Date"],
            dumpAllReviews())


# backup

def doBackup(parent):
    path = filedialog.asksaveasfilename(defaultextension=".db",
        filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
        initialfile="businesses_backup.db")
    if not path:
        return
    if makeBackup(path):
        messagebox.showinfo("Backup Done", "Saved to:\n" + path)
    else:
        messagebox.showerror("Error", "Backup failed")


# help

def openHelpWindow(parent):
    win = tk.Toplevel(parent)
    win.title("Help")
    win.geometry("500x420")
    fm = getFM()

    tk.Label(win, text="How to Use", font=fm.font(3, bold=True)).pack(pady=(12, 8))

    outer = tk.Frame(win)
    outer.pack(fill="both", expand=True, padx=16, pady=4)
    canvas = tk.Canvas(outer, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw", width=455)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    helpItems = [
        ("Browsing", "Use the Category dropdown or type in the Search box. The table updates as you type."),
        ("Sorting", "Use the Sort By options on the left: Name, Highest/Lowest Rated, or Most Reviews."),
        ("Details", "Double-click any business or select it and click View Details."),
        ("Reviews", "Pick a business and click Write Review. Set a rating with the slider and write a comment."),
        ("Favorites", "Click Add to Favorites on any business. See them all under My Favorites."),
        ("Deals", "Click View Deals in the sidebar. Deals also show up on the details page for each business."),
        ("Recommended", "Suggests places based on categories you've favorited or rated 4+ stars."),
        ("Reports", "Category Report shows a breakdown by type and exports to CSV. Top Rated lets you filter by category."),
        ("Add a Business", "Click Add Business. Name and category are required, everything else is optional."),
        ("Backup", "File; Backup Database; saves a copy of the database wherever you want."),
    ]

    for title, info in helpItems:
        tk.Label(inner, text=title, font=fm.font(bold=True),
                 anchor="w").pack(fill="x", pady=(8, 1))
        tk.Label(inner, text=info, font=fm.font(), wraplength=440,
                 justify="left", anchor="w").pack(fill="x", padx=(8, 0), pady=(0, 4))

    ttk.Button(win, text="Close", command=win.destroy).pack(pady=10)