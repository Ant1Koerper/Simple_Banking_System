import sqlite3
from random import randrange


# function which manages the working flow
def banking():
    conn = create_database()
    finished = False

    while not finished:
        input_from_user = user_input({
            "1": "Create an account",
            "2": "Log into account",
            "0": "Exit"
        })
        if input_from_user == "1":
            create_new_card(conn)
        elif input_from_user == "2":
            finished = card_login(conn)
        elif input_from_user == "0":
            finished = True
        else:
            print("Something unexpected happened. Aborting")
            finished = True
    conn.close()
    return None


# create a new SQLite database or use just return the connection string to
# the already existing one
def create_database():
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()

    # create table card if it doesn't exist
    if cur.execute("SELECT name FROM sqlite_master WHERE name='card'").fetchone() is None:
        cur.execute("CREATE TABLE card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)")

    return conn


def check_login(conn, card_number, pin):
    cur = conn.cursor()
    result = cur.execute(f"SELECT * FROM card "
                         f"WHERE number = '{card_number}' "
                         f"AND pin = '{pin}'")
    return False if result.fetchone() is None else True


def check_card_number_existence(conn, card_number):
    cur = conn.cursor()
    result = cur.execute(f"SELECT * FROM card WHERE number = {card_number}")
    return False if result.fetchone() is None else True


def print_balance(conn, card_number):
    cur = conn.cursor()
    result = cur.execute(f"SELECT balance FROM card WHERE number = {card_number}")
    print(f"Balance: {result.fetchone()}")
    return None


def close_account(conn, card_number):
    cur = conn.cursor()
    result = cur.execute(f"DELETE FROM card WHERE number = {card_number}")
    conn.commit()
    print("The account has been closed!")
    return None


def add_income(conn, card_number):
    income_to_add = input("Enter income:")
    transfer_money(conn, card_number, income_to_add)
    print("Income was added!")
    return None


def transfer_money(conn, card_number, amount):
    cur = conn.cursor()
    result = cur.execute(
        f"UPDATE card "
        f"SET balance = balance + {amount} "
        f"WHERE number = {card_number}"
    )
    conn.commit()
    return None


def add_new_card(conn, card_number, pin):
    cur = conn.cursor()
    result = cur.execute(
        f"INSERT INTO card VALUES "
        f"({card_number}, {card_number}, {pin}, {0})"
    )
    conn.commit()
    return None


def do_transfer(conn, card_number):
    cur = conn.cursor()
    print("Transfer")
    transfer_to = input("Enter card number:")

    if str(card_number) == str(transfer_to):
        print("You can't transfer money to the same account!")
        return None
    if not check_luhn_algorithm(transfer_to):
        print("Probably you made a mistake in the card number. Please try again!")
        return None
    if not check_card_number_existence(conn, transfer_to):
        print("Such a card does not exist.")
        return None

    amount_to_transfer = input("Enter how much money you want to transfer:")
    if cur.execute(f"SELECT * From card WHERE number = {card_number} "
                   f"AND balance <= {int(amount_to_transfer)}").fetchone() is not None:
        print("Not enough money!")
        return None

    transfer_money(conn, card_number, -int(amount_to_transfer))
    transfer_money(conn, transfer_to, amount_to_transfer)
    print("Success!")

    return None


def card_login(conn):
    card_number = input("Enter your card number:")
    pin = input("Enter your PIN:")

    login_successful = check_login(conn, card_number, pin)

    if not login_successful:
        print("Wrong card number or PIN!")
    elif login_successful:
        print("You have successfully logged in!")
        while True:
            input_from_user = user_input({
                "1": "Balance",
                "2": "Add income",
                "3": "Do transfer",
                "4": "Close account",
                "5": "Log out",
                "0": "Exit"
            })
            if input_from_user == "1":
                print_balance(conn, card_number)
            elif input_from_user == "2":
                add_income(conn, card_number)
            elif input_from_user == "3":
                do_transfer(conn, card_number)
            elif input_from_user == "4":
                close_account(conn, card_number)
            elif input_from_user == "5":
                return False
            elif input_from_user == "0":
                return True
            else:
                print("Something unexpected happened. Aborting")
                return True

    return False


# create a new card and add it to the dictionary of cards
def create_new_card(conn):
    card_number = create_card_number()
    while check_card_number_existence(conn, card_number):
        card_number = create_card_number()
    pin = (f"{randrange(0, 10)}"
           f"{randrange(0, 10)}"
           f"{randrange(0, 10)}"
           f"{randrange(0, 10)}")

    print("Your card has been created")
    print("Your card number:")
    print(card_number)
    print("Your card PIN:")
    print(pin)

    # add new card
    add_new_card(conn, card_number, pin)
    return None


def create_card_number():
    card_number = "400000"
    check_sum = 8
    doubling_counter = 6
    for _ in range(9):
        next_number = randrange(0, 10)
        card_number += str(next_number)
        next_number_modified = next_number
        # Luhn algorithm
        doubling_counter += 1
        if doubling_counter % 2 == 1:
            next_number_modified *= 2
        if next_number_modified > 9:
            next_number_modified -= 9
        check_sum += next_number_modified

    # ensure that the last digit fulfills the checksum
    last_digit = (10 - check_sum % 10) % 10
    card_number += str(last_digit)

    return card_number


def check_luhn_algorithm(card_number):
    check_sum = 0
    doubling_counter = 0
    for n in str(card_number):
        current_number = int(n)
        doubling_counter += 1
        if doubling_counter % 2 == 1:
            current_number *= 2
        if current_number > 9:
            current_number -= 9
        check_sum += current_number

    return check_sum % 10 == 0


# check user input
def user_input(options):
    for k, v in options.items():
        print(f"{k}. {v}")
    input_from_user = input()

    while input_from_user not in options.keys():
        input_from_user = input("No valid option. Please Try again.")

    return input_from_user


# run banking
banking()
