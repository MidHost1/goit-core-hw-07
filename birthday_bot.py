from collections import UserDict
from datetime import datetime, date, timedelta


def input_error(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                if "Invalid date format" in str(e):
                    return str(e)
                return "Give me name and phone please."
            except IndexError:
                return "Give me name and phone please."
        return inner


@input_error
def add_contact(args, book):
    name, phone, *_ = args 
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone, *_ = args  
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone changed."
    return f"Contact {name} not found."

@input_error
def show_phone(args, book):
    name, *_ = args  
    record = book.find(name)
    if record:
        phones = '; '.join(p.value for p in record.phones)
        return f"{name}: {phones}"
    return f"Contact {name} not found."

def show_all(book):
    if not book.data:
        return "No contacts."
    return str(book)

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        return "Give me name and birthday (DD.MM.YYYY) please."
    name, birthday_str = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday_str)
        return f"Birthday added for {name}."
    return f"Contact {name} not found."

@input_error
def show_birthday(args, book):
    if len(args) != 1:
        return "Give me name please."
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday}"
    return f"No birthday for {name}"

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in next 7 days."
    
    result = []
    for item in upcoming:
        result.append(f"{item['name']}: {item['congratulation_date']}")
    return "\n".join(result)



def main():
    book = AddressBook()

    def parse_input(user_input):
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, *args
    
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")



def string_to_date(date_string):
    return datetime.strptime(date_string, "%Y.%m.%d").date()


def date_to_string(date):
    return date.strftime("%Y.%m.%d")


def prepare_user_list(user_data):
    prepared_list = []
    for user in user_data:
        prepared_list.append({"name": user["name"], "birthday": string_to_date(user["birthday"])})
    return prepared_list


def find_next_weekday(start_date, weekday):
    days_ahead = weekday - start_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)


def adjust_for_weekend(birthday):
    if birthday.weekday() >= 5:
        return find_next_weekday(birthday, 0)
    return birthday



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")    
        

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must contain 10 digits.")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    
    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)
        
    
    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                self.phones.remove(phone)
                return
        raise ValueError("Phone not found")

    def edit_phone(self, old, new):
        for phone in self.phones:
            if phone.value == old:
                phone.value = new
                return
        raise ValueError("Old phone not found")

    def find_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                return phone
        return None

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        if self.birthday:
            return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {self.birthday}"
        return f"Contact name: {self.name.value}, phones: {phones_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()


        for name, record in self.data.items():
            if record.birthday:
                birthday_date = record.birthday.value
                birthday_this_year = birthday_date.replace(year=today.year)
                
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    congratulation_date = adjust_for_weekend(birthday_this_year)

                    congratulation_date_str = congratulation_date.strftime("%Y.%m.%d")

                    upcoming_birthdays.append({
                        "name": name,
                        "congratulation_date": congratulation_date_str
                    })

        return upcoming_birthdays

    def find(self, name):
        return self.data.get(name)
        
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())



if __name__ == "__main__":
    main()
