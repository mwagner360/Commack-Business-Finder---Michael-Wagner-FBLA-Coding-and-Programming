# all the commack business data is here
from datetime import datetime

# format is (name, category, address, phone, email, website, description, verified)
# verified = 1 for the ones in this, and ones that the user adds get 0

BUSINESSES = [
    # restaurants
    ("Jackson's Restaurant", "Restaurant", "6005 Jericho Tpke", "631-462-0822", None, None, "American restaurant with lunch and dinner", 1),
    ("The Spare Rib", "Restaurant", "2098 Jericho Tpke", "631-543-5050", None, None, "BBQ restaurant, been open 88 years", 1),
    ("Premier Diner", "Restaurant", "690 Commack Rd", "631-462-1432", None, None, "Family diner with European-style cooking", 1),
    ("Chick-fil-A", "Restaurant", "656 Commack Rd", "631-499-1280", None, None, "Fast food chicken", 1),
    ("Patrizia's", "Restaurant", "34 Vanderbilt Motor Pkwy", "631-499-6049", None, None, "Italian restaurant", 1),
    ("Emilio's Pizzeria", "Restaurant", "2201 Jericho Tpke", "631-462-6267", None, None, "Italian pizzeria, family owned since 1980", 1),
    ("Saffire", "Restaurant", "6330 Jericho Tpke", "631-486-2808", None, None, "South Asian fine dining", 1),
    ("Alma Cocina Mexican", "Restaurant", "354 Larkfield Rd", "631-623-6329", None, None, "Authentic Mexican cuisine", 1),
    ("Sangria 71", "Restaurant", "1095 Jericho Tpke", "631-670-7606", None, None, "Spanish restaurant with paella and tapas", 1),
    ("Mihana Japanese Bistro", "Restaurant", "10 Jericho Tpke", "631-343-7066", None, None, "Japanese food, sushi, and ramen", 1),
    ("Candlelight Diner", "Restaurant", "98 Veterans Memorial Hwy", None, None, None, "Classic diner", 1),
    ("Mario's Pizzeria", "Restaurant", "17 Vanderbilt Motor Pkwy", "631-499-7000", None, None, "Pizzeria, open since 2001", 1),
    ("Outback Steakhouse", "Restaurant", "216 Jericho Tpke", "631-864-7400", None, None, "Steakhouse", 1),
    ("Kiran Palace", "Restaurant", "2052 Jericho Tpke", "631-462-1122", None, None, "Indian cuisine", 1),
    ("Taco Bell", "Restaurant", "2186 Jericho Tpke", "631-343-5641", None, None, "Fast food Mexican", 1),

    # cafes
    ("Commack Bagels", "Cafe", "2059 Jericho Tpke", "631-486-8859", None, None, "Bagel shop and deli", 1),
    ("Mimi's Coffee & Bubble Tea", "Cafe", "6364 Jericho Tpke", None, None, None, "Coffee and bubble tea", 1),
    ("Bagel Chalet", "Cafe", "67 Commack Rd", "631-462-4823", None, None, "Bagel shop", 1),
    ("Tropical Smoothie", "Cafe", "Mayfair Shopping Center", None, None, None, "Smoothies and wraps", 1),

    # retail
    ("Target", "Retail", "100 Long Island Expy", "631-462-9245", None, None, "Department store", 1),
    ("Staples", "Retail", "5003 Jericho Tpke", "631-543-7513", None, None, "Office supplies", 1),
    ("BJ's Wholesale", "Retail", "60 Vanderbilt Motor Pkwy", "631-543-0726", None, None, "Warehouse club", 1),
    ("Sephora", "Retail", "Mayfair Shopping Center", None, None, None, "Beauty products", 1),
    ("GameStop", "Retail", "Mayfair Shopping Center", None, None, None, "Video games", 1),
    ("Lidl", "Retail", "Mayfair Shopping Center", None, None, None, "Grocery store", 1),
    ("Kohl's", "Retail", "50 Crooked Hill Rd", "631-462-3700", None, None, "Department store", 1),
    ("J.Crew Factory", "Retail", "170A Jericho Tpke", "631-980-1008", None, None, "Clothing", 1),
    ("Music & Arts", "Retail", "Mayfair Shopping Center", None, None, None, "Instruments and lessons", 1),

    # healthcare
    ("Commack Family Dental", "Healthcare", "164 Commack Rd", "631-910-4065", None, "https://www.commackfamilydental.com/", "Dentistry", 1),
    ("Northwell GoHealth", "Healthcare", "Mayfair Shopping Center", "631-480-6333", None, None, "Urgent care", 1),
    ("Aspen Dental", "Healthcare", "6218 Jericho Tpke", "631-462-5990", None, None, "Dental services", 1),

    # fitness
    ("Planet Fitness", "Fitness", "Mayfair Shopping Center", "631-656-0019", None, None, "Gym", 1),
    ("Champions Martial Arts", "Fitness", "80 Veteran Memorial Hwy", "631-543-1977", None, None, "Martial arts", 1),

    # services
    ("The UPS Store", "Services", "169 Commack Rd", "631-858-2332", None, None, "Shipping and printing", 1),
    ("H&R Block", "Services", "Mayfair Shopping Center", "631-462-4272", None, None, "Tax prep", 1),
    ("Harry Charles Salon", "Services", "Mayfair Shopping Center", None, None, None, "Salon and spa", 1),
    ("Queen Bee Nails", "Services", "2055 Jericho Tpke", "631-462-7799", None, None, "Nail salon", 1),
    ("Beacon Computers", "Services", "91 Commack Rd", "631-543-1476", None, None, "Computer repair", 1),

    # financial
    ("Capital One Bank", "Financial", "Mayfair Shopping Center", "631-462-0225", None, None, "Banking", 1),
    ("Suffolk Federal CU", "Financial", "100 Motor Pkwy", "631-924-8000", None, None, "Credit union", 1),

    # other categories
    ("Jiffy Lube", "Automotive", "6560 Jericho Tpke", "631-462-5823", None, None, "Oil change and auto services", 1),
    ("Commack Public Library", "Public Service", "18 Hauppauge Rd", "631-499-0888", None, None, "Public library", 1),
    ("Suffolk Y JCC", "Non-Profit", "74 Hauppauge Rd", "631-462-9800", None, None, "Recreation programs", 1),
    ("The Tutoring Center", "Education", "Mayfair Shopping Center", "631-486-7575", None, None, "Tutoring for all grades", 1),
    ("Kids Empire", "Entertainment", "5 Vanderbilt Motor Pkwy", "631-858-0600", None, None, "Indoor playground", 1),
    ("Commack Drive-In", "Entertainment", "698 Commack Rd", "631-462-0097", None, None, "Drive-in movie theater", 1),
    ("Hamlet Golf & CC", "Recreation", "1 Clubhouse Dr", "631-499-0200", None, None, "Golf course and country club", 1),
    ("Hampton Inn Commack", "Hospitality", "680 Commack Rd", "631-462-5700", None, None, "Hotel", 1),
]


# deal ids match the business order above
# jacksons=1, spare rib=2, premier=3, chick-fil-a=4, etc
# i had to recount these a bunch of times when i changed the list

DEALS = [
    (1, "Lunch Special", "20% off weekday lunch", 20, "2026-03-31", 1),
    (2, "Family Meal", "Family meal for 4 - save $15", 25, "2026-04-30", 1),
    (3, "Early Bird", "15% off breakfast before 9 AM", 15, "2026-06-30", 1),
    (4, "Student Discount", "10% off with student ID", 10, "2026-12-31", 1),
    (16, "Dozen Free", "Buy 2 dozen, get 1 free", 33, "2026-04-30", 1),
    (29, "New Patient", "Free consultation for new patients", 100, "2026-12-31", 1),
    (32, "Join for $1", "First month for $1", 95, "2026-05-31", 1),
    (23, "20% Off First Visit", "New customers get 20% off", 20, "2026-06-30", 1),
    (19, "Smoothie BOGO", "Buy one get one free smoothies on Fridays", 50, "2026-05-15", 1),
]


# some starting reviews so the app isnt empty when I first open it
def getStarterReviews():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return [
        (1, "Joe Smith", 4.5, "Great lunch spot, burgers are really good", now),
        (1, "Maria Lopez", 4.0, "Went for dinner, service was solid and food came out quick", now),
        (2, "Dan Romano", 5.0, "Best ribs on Long Island hands down", now),
        (2, "Chris Park", 4.5, "The pulled pork was incredible, sides were good too", now),
        (3, "Nicole Berg", 4.0, "Solid food big portions friendly staff", now),
        (3, "Tom Klein", 4.5, "Their pancakes are so good, we come here every sunday", now),
        (4, "Sarah Walsh", 4.5, "Always consistent and the staff is super nice", now),
        (4, "Mike DeLuca", 4.0, "Good chicken sandwich, drive thru line can be long though", now),
        (5, "Jenny Chen", 5.0, "Amazing pasta, great date night spot", now),
        (5, "Lisa Martin", 4.5, "Love the vibe here, the bread is always warm", now),
        (6, "Anthony Rizzo", 4.0, "Really good slice, one of the better pizza places around here", now),
        (6, "Steve Burns", 4.5, "Been going here since i was a kid, never disappoints", now),
        (7, "Priya Shah", 4.5, "Went for our anniversary, everything was perfect", now),
        (7, "Raj Kumar", 5.0, "The lunch buffet is a steal, so much good food", now),
        (8, "Carlos Mendez", 4.5, "The birria tacos here are next level", now),
        (8, "Amanda Hart", 4.0, "Authentic mexican, not the typical tex mex stuff", now),
        (9, "Diane Foster", 4.5, "Sangria is amazing obviously, food is great too", now),
        (9, "Brian Torres", 5.0, "The paella was incredible, perfect for a special occasion", now),
        (10, "Kevin Lee", 5.0, "Best sushi in commack no question", now),
        (10, "Emily Jones", 4.0, "The ramen here is solid, sushi is better though", now),
        (10, "Alex Nguyen", 4.5, "Tried the tonkotsu ramen and it was amazing", now),
        (11, "Matt Garcia", 3.5, "Classic diner food, nothing fancy but hits the spot at 2am", now),
        (12, "Rob Costa", 4.0, "Good pizza, garlic knots are fire", now),
        (12, "Frank Vitale", 4.5, "Marios uses really good quality ingredients, you can taste the difference", now),
        (13, "David White", 3.5, "Its outback, you know what youre getting. Blooming onion was good", now),
        (14, "Anita Patel", 4.5, "The chicken tikka masala here is so good", now),
        (14, "Sam Rivera", 4.0, "Good naan and biryani, solid spot for indian food in commack", now),
        (15, "Tyler King", 3.0, "Its taco bell lol, good for late night", now),
        (16, "Linda Stern", 4.5, "Best bagels in Commack, the egg sandwiches are great", now),
        (16, "Greg Harris", 5.0, "I come here literally every morning, never disappoints", now),
        (17, "Hannah West", 4.0, "Really good bubble tea, the taro flavor is my favorite", now),
        (17, "Jason Moore", 3.5, "Decent coffee, the bubble tea is better though", now),
        (18, "Mark Taylor", 4.0, "Good bagels, not as good as commack bagels but still solid", now),
        (19, "Rachel Davis", 4.5, "The smoothies here are actually really good", now),
        (20, "Paula Grant", 4.0, "Its target, always a good time, clean store", now),
        (21, "Scott Baker", 3.5, "Good for printer ink and random office stuff", now),
        (22, "Karen James", 4.0, "Love BJs, good prices on bulk items", now),
        (23, "Ashley Reed", 4.5, "Love this sephora, the staff is really helpful", now),
        (24, "Nick Franco", 4.0, "Good selection of games, trade in prices are meh", now),
        (25, "Tina Cruz", 4.0, "Lidl is underrated honestly, good prices good produce", now),
        (26, "Debra Lane", 3.5, "Good deals at kohls, especially with the coupons", now),
        (28, "Ryan Murphy", 4.5, "Great place for instrument rentals and sheet music", now),
        (29, "Susan Kim", 5.0, "Very thorough, great experience overall", now),
        (29, "James Hall", 4.5, "Dr was really nice and explained everything", now),
        (30, "Laura Bell", 4.0, "Got in and out pretty fast, good for when you need urgent care", now),
        (31, "Peter Stone", 4.0, "Aspen dental got me in same day, pretty good service", now),
        (32, "John Diaz", 3.5, "Basic gym but great price, has everything you need", now),
        (32, "Megan Ross", 4.0, "Planet fitness gets the job done, no complaints", now),
        (33, "Donna Perry", 5.0, "My kid loves it here, great instructors", now),
        (34, "Robert Hull", 4.0, "Always helpful when I need to ship packages", now),
        (36, "Cathy Wong", 4.5, "Got a great haircut here, will def come back", now),
        (38, "Eric Todd", 4.5, "Fixed my laptop in like 2 days, very reasonable price", now),
        (41, "Phil Grant", 3.5, "Quick oil change, in and out in 20 min", now),
        (42, "Nancy Ford", 5.0, "Love the library, always has good events for kids", now),
        (42, "Ben Kelly", 4.5, "Great community space, friendly staff", now),
        (43, "Michelle Ruiz", 4.5, "The JCC has great programs for kids, pool is nice too", now),
        (44, "Janet Miles", 4.0, "My kid actually likes going to tutoring here which says a lot", now),
        (45, "Christine Lam", 4.5, "The kids had a blast, great for birthday parties", now),
        (46, "Tony Vega", 4.5, "Drive in is such a cool experience, love coming here in summer", now),
        (46, "Andrea Scott", 5.0, "One of the last drive ins on long island, totally worth it", now),
        (47, "Gary Miller", 4.0, "Nice course, well maintained, good for a weekend round", now),
        (48, "Jeff Walker", 4.0, "Clean rooms, good breakfast, convenient location off the LIE", now),
    ]