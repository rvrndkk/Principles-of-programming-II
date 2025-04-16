import psycopg2
import csv
import json
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




def ins_or_upd(name, phone):
    name = input('Name')
    phone = input('Phone')
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE OR REPLACE PROCEDURE insert1(user_name TEXT, user_phone TEXT)
        LANGUAGE plpgsql AS $$
        BEGIN
            IF EXISTS (SELECT 1 FROM phonebook WHERE name = user_name) THEN
                UPDATE phonebook SET phone = user_phone WHERE name = user_name;
            ELSE
                INSERT INTO phonebook(name, phone) VALUES (user_name, user_phone);
            END IF;
        END;
        $$;
    """)
    cur.execute("CALL insert1(%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()

def manyy(user_list):
    n = int(input("How many to insert? "))
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE OR REPLACE PROCEDURE insert_m1(json_data JSON)
        LANGUAGE plpgsql AS $$
        DECLARE
            user_obj JSON;
            user_name TEXT;
            user_phone TEXT;
            bad_entries TEXT[] := ARRAY[]::TEXT[];
        BEGIN
            FOR user_obj IN SELECT * FROM json_array_elements(json_data)
            LOOP
                user_name := user_obj->>'name';
                user_phone := user_obj->>'phone';
                IF user_phone ~ '^\\+7[0-9]{10}$' THEN
                    PERFORM insert_or_update_user(user_name, user_phone);
                ELSE
                    bad_entries := array_append(bad_entries, user_name  user_phone);
                END IF;
            END LOOP;
            RAISE NOTICE 'Invalid entries: %', bad_entries;
        END;
        $$;
    """)
    json_data = json.dumps(user_list)
    cur.execute("CALL insert_m1(%s::json)", (json_data,))
    conn.commit()
    cur.close()
    conn.close()

def by_pat(pattern):
    pattern = input("Enter pattern (part of name or phone): ")
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE OR REPLACE FUNCTION search_u1(pat TEXT)
        RETURNS TABLE(name TEXT, phone TEXT)
        LANGUAGE sql AS $$
        SELECT name, phone FROM phonebook
        WHERE name ILIKE '%'  '%' OR phone ILIKE '%'  '%';
        $$;
    """)
    cur.execute("SELECT * FROM search_u1(%s)", (pattern,))
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()

def get_pag(limit, offset):
    limit = int(input("Limit: "))
    offset = int(input("Offset: "))
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE OR REPLACE FUNCTION get_u1(lim INT, off INT)
        RETURNS TABLE(name TEXT, phone TEXT)
        LANGUAGE sql AS $$
        SELECT name, phone FROM phonebook LIMIT lim OFFSET off;
        $$;
    """)
    cur.execute("SELECT * FROM get_u1(%s, %s)", (limit, offset))
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()

def delete_u():
    identifier = input("Enter name or phone to delete: ")
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE OR REPLACE PROCEDURE delete_u1(identifier TEXT)
        LANGUAGE plpgsql AS $$
        BEGIN
            DELETE FROM phonebook WHERE name = identifier OR phone = identifier;
        END;
        $$;
    """)
    cur.execute("CALL delete_u1(%s)", (identifier,))
    conn.commit()
    cur.close()
    conn.close()
    print("User deleted if existed.")






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
        print("7. Search by Pattern (Function)")
        print("8. Insert/Update User (Procedure)")
        print("9. Insert Many Users (Procedure)")
        print("10. Query with Pagination (Function)")
        print("11. Delete by name or phone (Procedure)")

        choice = input("Choose an option: ")
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
        elif choice == "7":
            by_pat()
        elif choice == "8":
            ins_or_upd()
        elif choice == "9":
            manyy()
        elif choice == "10":
            get_pag()
        elif choice == "11":
            delete_u()

        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
