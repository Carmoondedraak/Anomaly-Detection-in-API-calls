import random 
import random
import string
import csv

def get_random_string(length):
    '''creates random string of length'''
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    # print random string
    return result_str

def get_userdetails(file):
    '''
        Generates lists of possible user data from csv-file
    '''
    first_names= []
    last_names = [] 
    addresses = []
    cities = []
    countries = []
    with open(file,encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:

            print(row)
            first_names.append(row[1])
            first_names.append(row[2])
            last_names.append(row[3])
            addresses.append(row[4])
            cities.append(row[5])
            countries.append(row[6])

        first_names = list(filter(None, first_names))
        last_names = list(filter(None, last_names))
        addresses = list(filter(None, addresses))
        cities = list(filter(None, cities))
        countries = list(filter(None, countries))

    return first_names, last_names, addresses, cities, countries

def generate_users(first,last,add,cities,countries,n):
    '''Generates a list with generated user data
       **********************************************************
        Input :
        * first  - list of possible first names for users
        * last - list of possible last names for users
        * add - list of possible addresses for users
        * cities - list of cities of residence for users
        * countries - llist of countries the users can be from
        * n - number of users to generate
        **********************************************************
        Output:
        * user_list - list of tuples with information of each user
    '''
    user_list = []
    for i in range(n):
        first_name = random.choice(first)
        last_name = random.choice(last)
        address = random.choice(add)
        email = random.choice(['@gmail.com', '@live.com','@yahoo.com','@hotmail.com'])
        user_name = first_name + last_name
        email_address  = first_name[0] + last_name + email
        password = get_random_string(8)
        post = random.randint(1000, 9999)
        randomindex = random.randint(0,len(cities)-1)
        city = cities[randomindex]
        country = countries[randomindex]
        bank = random.randint(10000000000,99999999999)
        data = str(random.randint(1,12)) + '/' + str(random.randint(2023, 2030)) 
        ccv = random.randint(100,999)
        user_list.append((user_name,password,email_address,first_name,last_name,address,post,city,country,bank,data,ccv))

    return user_list

def main():
    file = "usernames1.csv"
    first,last,add, cities, countries = get_userdetails(file)
    user_list = generate_users(first,last,add,cities,countries, 100)
    print(user_list)
    return user_list

main()