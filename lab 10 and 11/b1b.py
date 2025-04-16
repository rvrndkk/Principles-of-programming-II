import psycopg2
import csv

def connect():
    return psycopg2.connect(
        dbname="suppliers",
        user="postgres",
        password="3799979",
        host="localhost",
        port="5432"
    )

def new_tbl():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL
                )
            """)
        conn.commit()

def insert_scv(filename):
    with connect() as conn:
        with conn.cursor() as cur, open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (row[0], row[1]))
        conn.commit()
        # conn.rollback() esli nado
        print("Data inserted from CSV.")

def insert_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
        conn.commit()
        print("Data inserted.")

def update_user():
    field = input("What to update? (name or phone): ").strip().lower()
    if field == "name":
        old = input("Enter phone of user whose name to update: ")
        new = input("Enter new name: ")
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE phonebook SET name = %s WHERE phone = %s", (new, old))
            conn.commit()
    elif field == "phone":
        old = input("Enter name of user whose phone to update: ")
        new = input("Enter new phone: ")
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE phonebook SET phone = %s WHERE name = %s", (new, old))
            conn.commit()
    print("Update complete.")

def query_data():
    print("1. Show all\n2. Filter by name\n3. Filter by phone prefix")
    choice = input("Choose option: ")
    with connect() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                cur.execute("SELECT * FROM phonebook")
            elif choice == "2":
                name = input("Enter part of name: ")
                cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s", (f'%{name}%',))
            elif choice == "3":
                prefix = input("Enter phone prefix: ")
                cur.execute("SELECT * FROM phonebook WHERE phone LIKE %s", (f'{prefix}%',))
            for row in cur.fetchall():
                print(row)

def delete_entry():
    field = input("Delete by (name/phone): ").strip().lower()
    value = input(f"Enter {field}: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM phonebook WHERE {field} = %s", (value,))
        conn.commit()
        print("Entry deleted.")

def main():
    new_tbl()
    while True:
        print("\nPhoneBook Menu")
        print("1. upload data from csv file")
        print("2. Insert from console")
        print("3. Update user")
        print("4. Query data")
        print("5. Delete entry")
        print("6. Exit")
        choice = input("Choose: ")
        if choice == "1":
            print("file name: ")
            ff = input()
            insert_scv(ff)
        elif choice == "2":
            insert_console()
        elif choice == "3":
            update_user()
        elif choice == "4":
            query_data()
        elif choice == "5":
            delete_entry()
        elif choice == "6":
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
