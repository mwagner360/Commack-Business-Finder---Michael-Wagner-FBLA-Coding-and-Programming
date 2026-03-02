# Commack Business Finder

FBLA Coding & Programming 2025-2026

A desktop application for finding and supporting local businesses in Commack, New York. Users can browse businesses by their category, leave reviews, save favorites, view deals, and get personalized recommendations.

Built by Michael Wagner - Commack High School

---

## How to Run

You need Python 3.8 or newer. This is because tkinter and sqlite3 come with Python so there's nothing extra to install with it. Works on Windows, Mac, and Linux.

1. Put all the project files in one folder
2. Open a terminal in that folder
3. Run `python main.py`
4. Enter a username and solve the math captcha to log in

The database is created automatically on first run with businesses, reviews, and deals.

---

## Files

| File | What it does |
|------|-------------|
| `main.py` | Entry point, starts the app |
| `seed_data.py` | Business data, deals, and starter reviews |
| `database.py` | All the SQL queries |
| `gui.py` | Main window with the table, sidebar, and login |
| `windows.py` | All popup windows (details, review form, favorites, etc.) |
| `businesses.db` | SQLite database file which is created on first run |

---

## Features

**Business Directory.** Real Commack businesses across 15 categories. Search updates as you type and you can sort by name, highest or lowest rating, or most reviews.

**Reviews & Ratings.** Rate businesses from 1 to 5 with a slider (half stars included) and leave a comment. Input is validated so blank or spam reviews like repeated characters are not submitted.

**Favorites.** Save businesses to a personal list. There's a UNIQUE constraint in the database on the business ID and username so duplicates are not able to be made.

**Deals and Coupons.** Some businesses have deals with discount percentages and expiration dates. You can view all deals from the sidebar or see them on individual business detail pages.

**Intelligent Recommendations.** The app looks at what categories you've favorited or rated 4+ stars, then suggests businesses in those categories you haven't saved yet. New users with no history get the top rated businesses as a starting point.

**Reports.** Category Report breaks down the number of businesses, average rating, and review count per category, and can be exported to CSV. Top Rated Report lets you filter by category and choose how many results to display.

**Accessibility.** Text size can be adjusted with Ctrl +/-, the A+ and A- buttons in the top bar, or the Accessibility menu. Changes will apply across all open windows.

**Database Backup.** File > Backup Database; saves a copy of the .db file to any location.

**Bot Prevention.** The login screen has a randomized math captcha. Usernames are restricted to letters, numbers, and underscores. There are also character limits.

**Add Business.** Users can add new businesses and there is validation on phone numbers, emails, and websites. Websites without https:// get it added automatically. Submitted businesses by the user are marked as unverified.

---

## Why Python

I chose Python because tkinter and sqlite3 are both part of the standard library, so the app runs on any computer with Python without extra installs. It also made it great to organize the project into separate files without needing a seperate framework.

## How It's Built

The project is split into five files by their role. `main.py` launches the app. `seed_data.py` holds all the business data separately to avoid it from being cluttered mixed in with the database code. `database.py` contains every SQL query the app uses. `gui.py` handles the main window, table, and sidebar. `windows.py` has all the popup windows. 

The GUI never runs SQL directly. Everything goes through functions in `database.py`, so the interface and data layer are kept separate. If I need to change how data is stored I only have to update one file.

The database uses four tables: `businesses`, `reviews`, `favorites`, and `deals`. The favorites table has a UNIQUE constraint on the business_id and username so there wont be duplicate favorites at the database level.

## Libraries

All from Python's standard library and no third party packages were used.

- `tkinter` / `ttk` for the GUI
- `sqlite3` for the database
- `csv` for report exports
- `datetime` for timestamps
- `random` for captcha generation
- `re` for input validation
- `shutil` for database backups

There is no copyrighted material included in this submission.

---

Thanks for checking out my project! I hope you enjoy using it!
