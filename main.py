import sqlite3
# import random
import json


def load_strings(file_path):
    with open(file_path, 'r') as file:
        strings = json.load(file)
    return strings


def create_or_open_database(sql_strings):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute(sql_strings["create_table"])

    # Check if the table is empty
    cursor.execute(sql_strings["count_entries"])
    count = cursor.fetchone()[0]

    # If the table is empty, insert 100 random book entries from the JSON file
    if count == 0:
        with open('books.json', 'r') as file:
            books = json.load(file)
        # random_books = random.sample(books, 10)
        cursor.executemany(sql_strings["insert_entries"],
                           [(book['title'],
                             book['description']) for book in books])
        conn.commit()

    return conn, cursor


def display_first_five_entries(cursor, strings, sql_strings):
    # Display the first 5 entries
    cursor.execute(sql_strings["select_first_five"])
    results = cursor.fetchall()

    if results:
        print(strings["welcome_message"])
        for row in results:
            print(f"ID: {row[0]}, Title: {row[1]}, Description: {row[2]}")
    else:
        print(strings["no_entries_message"])


def search_entries(cursor, search_text, sql_strings):
    # Perform a search in the database matching whole words
    # using spaces around the search text
    cursor.execute(sql_strings["search_entries"],
                   (f'% {search_text} %', f'% {search_text} %'))
    results = cursor.fetchall()

    # Additionally check for exact matches at the start or end of the field
    cursor.execute(sql_strings["search_entries"],
                   (f'{search_text} %', f'{search_text} %'))
    results += cursor.fetchall()

    cursor.execute(sql_strings["search_entries"],
                   (f'% {search_text}', f'% {search_text}'))
    results += cursor.fetchall()

    # Remove duplicates
    unique_results = {result[0]: result for result in results}

    return list(unique_results.values())


def mark_order_created(conn, cursor, entry_id, strings, sql_strings):
    # Mark an entry as "order created"
    cursor.execute(sql_strings["mark_order_created"], (entry_id,))
    conn.commit()
    if cursor.rowcount > 0:
        print(strings["order_created_message"].format(entry_id=entry_id))
    else:
        print(strings["already_ordered_message"].format(entry_id=entry_id))


def main():
    strings = load_strings('strings.json')
    sql_strings = load_strings('sql_strings.json')
    conn, cursor = create_or_open_database(sql_strings)

    # Display the first 5 entries by default
    display_first_five_entries(cursor, strings, sql_strings)

    while True:
        search_text = input(strings["search_prompt"])
        if search_text.lower() == 'exit':
            break

        # Improved search functionality
        results = search_entries(cursor, search_text, sql_strings)

        if results:
            print(strings["search_results"])
            for row in results:
                print(f"ID: {row[0]}, Title: {row[1]}, Description: {row[2]}")

            buy_choice = input(strings["buy_prompt"])
            if buy_choice.lower() == 'yes':
                entry_id = int(input(strings["enter_id_prompt"]))
                mark_order_created(conn, cursor, entry_id,
                                   strings, sql_strings)
        else:
            print(strings["no_matching_entries"])

    # Close the database connection
    conn.close()


if __name__ == '__main__':
    main()
