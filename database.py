import sqlite3
import shutil
from datetime import datetime
from seed_data import BUSINESSES, DEALS, getStarterReviews

DB = "businesses.db"


def setupDatabase():
    db = sqlite3.connect(DB)
    c = db.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, category TEXT NOT NULL,
        address TEXT, phone TEXT, email TEXT, website TEXT,
        description TEXT, verified INTEGER DEFAULT 0)""")

    c.execute("""CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER, username TEXT NOT NULL,
        rating REAL NOT NULL, comment TEXT, date TEXT NOT NULL,
        FOREIGN KEY (business_id) REFERENCES businesses(id))""")

    # UNIQUE prevents someone from favoriting the same place twice
    c.execute("""CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER, username TEXT NOT NULL, date_added TEXT,
        FOREIGN KEY (business_id) REFERENCES businesses(id),
        UNIQUE(business_id, username))""")

    c.execute("""CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER, title TEXT NOT NULL,
        description TEXT, discount INTEGER, expiry TEXT,
        active INTEGER DEFAULT 1,
        FOREIGN KEY (business_id) REFERENCES businesses(id))""")

    c.execute("SELECT COUNT(*) FROM businesses")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO businesses (name,category,address,phone,email,website,description,verified) VALUES (?,?,?,?,?,?,?,?)", BUSINESSES)
        c.executemany("INSERT INTO deals (business_id,title,description,discount,expiry,active) VALUES (?,?,?,?,?,?)", DEALS)
        c.executemany("INSERT INTO reviews (business_id,username,rating,comment,date) VALUES (?,?,?,?,?)", getStarterReviews())

    db.commit()
    db.close()


def loadBusinessList(category=None, searchText=None, sortBy="name"):
    # builds the query based on active filters
    db = sqlite3.connect(DB)
    c = db.cursor()

    query = """SELECT b.id, b.name, b.category, b.phone,
                  COALESCE(AVG(r.rating), 0), COUNT(r.id)
           FROM businesses b LEFT JOIN reviews r ON b.id = r.business_id
           WHERE 1=1"""
    params = []

    if category and category != "All":
        query += " AND b.category = ?"
        params.append(category)
    if searchText:
        query += " AND (b.name LIKE ? OR b.description LIKE ?)"
        params.append("%" + searchText + "%")
        params.append("%" + searchText + "%")

    query += " GROUP BY b.id"

    if sortBy == "name":
        query += " ORDER BY b.name"
    elif sortBy == "rating_desc":
        query += " ORDER BY COALESCE(AVG(r.rating),0) DESC"
    elif sortBy == "rating_asc":
        query += " ORDER BY COALESCE(AVG(r.rating),0) ASC"
    elif sortBy == "reviews_desc":
        query += " ORDER BY COUNT(r.id) DESC"

    c.execute(query, params)
    rows = c.fetchall()
    db.close()
    return rows


def lookupBusiness(bid):
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute("SELECT name,category,address,phone,email,website,description,verified FROM businesses WHERE id=?", (bid,))
    row = c.fetchone()
    db.close()
    return row


def saveBusiness(name, cat, addr, phone, email, website, desc):
    db = sqlite3.connect(DB)
    c = db.cursor()
    try:
        c.execute("INSERT INTO businesses (name,category,address,phone,email,website,description,verified) VALUES (?,?,?,?,?,?,?,0)",
                  (name, cat, addr, phone, email, website, desc))
        newId = c.lastrowid
        db.commit()
    except sqlite3.Error as e:
        print("could not save business:", e)
        newId = None
    db.close()
    return newId


def saveReview(bid, user, rating, comment):
    db = sqlite3.connect(DB)
    c = db.cursor()
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT INTO reviews (business_id,username,rating,comment,date) VALUES (?,?,?,?,?)",
                  (bid, user, rating, comment, ts))
        db.commit()
        ok = True
    except sqlite3.Error as e:
        print("review failed:", e)
        ok = False
    db.close()
    return ok


def loadReviews(bid):
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute("SELECT username,rating,comment,date FROM reviews WHERE business_id=? ORDER BY date DESC", (bid,))
    rows = c.fetchall()
    db.close()
    return rows


def saveFavorite(bid, user):
    db = sqlite3.connect(DB)
    c = db.cursor()
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("INSERT INTO favorites (business_id,username,date_added) VALUES (?,?,?)", (bid, user, today))
        db.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False  # already favorited
    except sqlite3.Error as e:
        print("fav error:", e)
        result = False
    db.close()
    return result


def loadFavorites(user):
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute("""SELECT b.name, b.category, f.date_added, f.id
                 FROM favorites f JOIN businesses b ON f.business_id=b.id
                 WHERE f.username=? ORDER BY f.date_added DESC""", (user,))
    rows = c.fetchall()
    db.close()
    return rows

def removeFavorite(fid):
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute("DELETE FROM favorites WHERE id=?", (fid,))
    db.commit()
    db.close()


def loadDeals(bid=None):
    db = sqlite3.connect(DB)
    c = db.cursor()
    if bid is not None:
        c.execute("SELECT title,description,discount,expiry FROM deals WHERE business_id=? AND active=1", (bid,))
    else:
        c.execute("""SELECT b.name, d.title, d.description, d.discount, d.expiry
                     FROM deals d JOIN businesses b ON d.business_id=b.id
                     WHERE d.active=1 ORDER BY d.expiry""")
    rows = c.fetchall()
    db.close()
    return rows


def categoryBreakdown():
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute("""SELECT b.category, COUNT(DISTINCT b.id), COALESCE(AVG(r.rating),0), COUNT(r.id)
                 FROM businesses b LEFT JOIN reviews r ON b.id=r.business_id
                 GROUP BY b.category ORDER BY COUNT(DISTINCT b.id) DESC""")
    rows = c.fetchall()
    db.close()
    return rows


def topRatedList(n=10, cat=None):
    db = sqlite3.connect(DB)
    c = db.cursor()
    query = """SELECT b.name, b.category, AVG(r.rating), COUNT(r.id)
           FROM businesses b JOIN reviews r ON b.id=r.business_id"""
    params = []
    if cat and cat != "All":
        query += " WHERE b.category=?"
        params.append(cat)
    query += " GROUP BY b.id HAVING COUNT(r.id)>=1 ORDER BY AVG(r.rating) DESC LIMIT ?"
    params.append(n)
    c.execute(query, params)
    rows = c.fetchall()
    db.close()
    return rows


def dumpAllReviews():
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute("""SELECT b.name, r.username, r.rating, r.comment, r.date
                 FROM reviews r JOIN businesses b ON r.business_id=b.id ORDER BY r.date DESC""")
    rows = c.fetchall()
    db.close()
    return rows


# recommendation engine
# looks at what categories the user has favorited or rated highly,
# then suggests businesses in those categories they haven't saved yet

def findRecommendations(user, limit=6):
    db = sqlite3.connect(DB)
    c = db.cursor()

    # get preferred categories from favorites and highly rated reviews
    c.execute("""SELECT DISTINCT b.category FROM favorites f
                 JOIN businesses b ON f.business_id=b.id WHERE f.username=?
                 UNION
                 SELECT DISTINCT b.category FROM reviews r
                 JOIN businesses b ON r.business_id=b.id
                 WHERE r.username=? AND r.rating>=4.0""", (user, user))
    cats = [row[0] for row in c.fetchall()]

    if len(cats) > 0:
        c.execute("SELECT business_id FROM favorites WHERE username=?", (user,))
        saved = [row[0] for row in c.fetchall()]

        catPlaceholders = ",".join(["?" for x in cats])
        query = ("SELECT b.id, b.name, b.category, b.description,"
                 " COALESCE(AVG(r.rating),0), COUNT(r.id)"
                 " FROM businesses b LEFT JOIN reviews r ON b.id=r.business_id"
                 " WHERE b.category IN (" + catPlaceholders + ")")
        params = list(cats)

        if len(saved) > 0:
            savedPlaceholders = ",".join(["?" for x in saved])
            query += " AND b.id NOT IN (" + savedPlaceholders + ")"
            params = params + saved

        query += " GROUP BY b.id ORDER BY COALESCE(AVG(r.rating),0) DESC LIMIT ?"
        params.append(limit)
        c.execute(query, params)
        results = c.fetchall()
        db.close()
        if len(results) > 0:
            return results

    # no history yet, fall back to top rated overall
    db2 = sqlite3.connect(DB)
    c2 = db2.cursor()
    c2.execute("""SELECT b.id, b.name, b.category, b.description,
                         COALESCE(AVG(r.rating),0), COUNT(r.id)
                  FROM businesses b LEFT JOIN reviews r ON b.id=r.business_id
                  GROUP BY b.id HAVING COUNT(r.id)>0
                  ORDER BY COALESCE(AVG(r.rating),0) DESC LIMIT ?""", (limit,))
    results = c2.fetchall()
    db2.close()
    return results

# backup of the database so I dont lose any businesses' information
def makeBackup(path):
    try:
        shutil.copy2(DB, path)
        return True
    except OSError as e:
        print("backup failed:", e)
        return False
