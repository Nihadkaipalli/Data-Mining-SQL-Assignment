import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Create a SQLite database connection
conn = sqlite3.connect('bookstore_final.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS Authors (
                    author_id INTEGER PRIMARY KEY,
                    author_name TEXT,
                    nationality TEXT,
                    birth_year INTEGER,
                    UNIQUE(author_name, nationality)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Books (
                    book_id INTEGER PRIMARY KEY,
                    title TEXT,
                    genre TEXT,
                    publication_year INTEGER,
                    author_id INTEGER,
                    price REAL,
                    FOREIGN KEY (author_id) REFERENCES Authors(author_id)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Customers (
                    customer_id INTEGER PRIMARY KEY,
                    customer_name TEXT,
                    email TEXT UNIQUE,
                    age INTEGER,
                    gender TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    zipcode TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Orders (
                    order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    order_date DATE,
                    total_amount REAL,
                    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS OrderDetails (
                    order_id INTEGER,
                    book_id INTEGER,
                    quantity INTEGER,
                    unit_price REAL,
                    PRIMARY KEY (order_id, book_id),
                    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
                    FOREIGN KEY (book_id) REFERENCES Books(book_id)
                )''')

# Generate fake data for authors
authors_data = [(fake.name(), fake.country(), fake.random_int(min=1900, max=2000)) for _ in range(1000)]

# Insert authors data into the Authors table
cursor.executemany('''INSERT OR IGNORE INTO Authors (author_name, nationality, birth_year) VALUES (?, ?, ?)''', authors_data)

# Generate fake data for books
books_data = [(fake.sentence(), fake.random_element(['Fiction', 'Mystery', 'Science Fiction', 'Romance', 'Thriller']), fake.random_int(min=1900, max=2023), random.randint(1, 1000), fake.random_number(digits=2)) for _ in range(1000)]

# Insert books data into the Books table
cursor.executemany('''INSERT INTO Books (title, genre, publication_year, author_id, price) VALUES (?, ?, ?, ?, ?)''', books_data)

# Generate fake data for customers
customers_data = []

existing_emails = set()  # To store generated emails

for _ in range(1000):
    customer_name = fake.name()
    email = fake.email()
    
    # Introduce missing values and duplicates
    if random.random() < 0.1:  # 10% chance of missing email
        email = None
    elif email in existing_emails:
        email = None
    else:
        existing_emails.add(email)
    
    customer_age = fake.random_int(min=18, max=70)
    customer_gender = fake.random_element(['Male', 'Female'])
    
    # Introduce missing values
    if random.random() < 0.05:  # 5% chance of missing address and zip code
        customer_address = None
        customer_zipcode = None
    else:
        customer_address = fake.address()
        customer_zipcode = fake.zipcode()
    
    customer_city = fake.city()
    customer_state = fake.state_abbr()
    
    customers_data.append((customer_name, email, customer_age, customer_gender, customer_address, customer_city, customer_state, customer_zipcode))

# Insert customers data into the Customers table
cursor.executemany('''INSERT INTO Customers (customer_name, email, age, gender, address, city, state, zipcode) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', customers_data)

# Generate fake data for orders
orders_data = []

for i in range(1, 1001):  # Ensure at least 1000 rows
    order_date = datetime.now() - timedelta(days=random.randint(1, 365))
    orders_data.append((i, random.randint(1, 1000), order_date.strftime('%Y-%m-%d'), random.uniform(10, 500)))

# Introduce duplicate orders
orders_data.extend((max(orders_data)[0] + i + 1, customer_id, order_date, total_amount) for i, (order_id, customer_id, order_date, total_amount) in enumerate(orders_data[:50]))

# Insert orders data into the Orders table
cursor.executemany('''INSERT INTO Orders (order_id, customer_id, order_date, total_amount) VALUES (?, ?, ?, ?)''', orders_data)

# Generate fake data for order details
order_details_data = []

for i in range(1, 1001):  # Ensure at least 1000 rows
    order_details_data.append((i, random.randint(1, 1000), random.randint(1, 10), random.uniform(10, 50)))

# Introduce missing values in order details
for _ in range(50):  # Introduce 50 missing values
    order_details_data[random.randint(0, 999)] = (None, None, None, None)

# Insert order details data into the OrderDetails table
cursor.executemany('''INSERT INTO OrderDetails (order_id, book_id, quantity, unit_price) VALUES (?, ?, ?, ?)''', order_details_data)

# Commit changes and close connection
conn.commit()
conn.close()
