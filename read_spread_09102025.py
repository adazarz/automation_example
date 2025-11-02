 import pandas as pd
import win32com.client
from datetime import date
from pprint import pprint

class bcolors:
    FAIL = '\033[91m'
    ENDC = '\033[0m'

#Cleaning the details of letters, separating the numbers
def clean(detail):
    #Auxiliary variables
    cleaned_details = []
    a = str()
    #Directly adding stand-alone numbers
    if isinstance(detail,int):
        cleaned_details.append(detail)
    else:
        l = len(detail) - 1
        for i,sign in enumerate(detail):
            if sign.isdigit():
                a += sign
                if i == l:
                    cleaned_details.append(a)
                    a = str()
            elif a:
                cleaned_details.append(a)
                a = str()
    #Elaborating shortened details, ex. 122345/46/47/48 into 122345, 122346, 122347, 122348
    #Elaboration happens if subsequent invoice numbers are shorter by at least 5 digits or are shorter by at least three digits and the next 
    #number is greater by one than the first, as in the example above.
    count = 0
    while count < len(cleaned_details) - 1:
        first_number = cleaned_details[count]
        next_number = cleaned_details[count+1]
        dif = len(str(first_number)) - len(str(next_number))
        if dif > 4:
            cleaned_details[count + 1] = first_number[:dif] + next_number
        elif dif > 2:
            c = first_number[dif:]
            if int(next_number) - int(c) == 1:
                cleaned_details[count + 1] = first_number[:dif] + next_number
        count += 1
    return cleaned_details

def text_only(detail):
    if isinstance(detail, int):
        return False
    for sign in detail:
        if sign.isdigit():
            return False
    return True

#Checking if the BOE references can be processed in a specifically integer-like way, that is, if they include letters, ex. AXN12345
def is_int(number):
    count_letters = 0
    for i in str(number):
        if not i.isdigit():
            count_letters += 1
    if count_letters == 0:
        return True
    else:
        return False
    
def differs_by_up_to_fifty(s1, s2):
    return is_int(s1) and is_int(s2) and abs(int(s1) - int(s2)) < 100

#Checking if we can merge bills of exchange's references
#The program compares "cleaned" details, it means sheer numbers, so as to recognise the same details written in a slightly different way
#ex. "AVANCE 253" and "SOLDE 253" will be recognised as identical
def can_merge(i, j):
    return (
        clients[i] == clients[j] and
        clean(details[i]) == clean(details[j]) and
        banq_domi[i].upper() == banq_domi[j].upper()
    ) 

def remove_line(h):
    clients.pop(h)
    nlcn.pop(h)
    banq_domi.pop(h)
    echeance.pop(h)
    details.pop(h)
    montants.pop(h)
    
#Checking the format of date d'echeance, formatting accordingly
def date_format(echeance):
    if isinstance(echeance,date):
        return echeance.strftime("%d/%m/%Y")
    else:
        return echeance

def connecting(numbers):
    #Checking if we can connect shortened nlcn with a dash
    if not all(is_int(z) for z in numbers):
        return
    y = 1
    while y < len(numbers):
        if len(numbers) > 3 and all(len(x) == 2 for x in numbers[y:]) and numbers[y-1].isdigit():
            numbers_parallel = [int(x) for x in numbers if x.isdigit()]
            numbers_parallel[y-1] = int(str(numbers[y-1])[-2:])
            from_the_beginning = y - 1
            while from_the_beginning < len(numbers) + 1 - y:
                from_the_end = 1
                while from_the_end <= len(numbers) + 1 - y:
                    if numbers_parallel[-from_the_end] != "-" and numbers_parallel[from_the_beginning] != "-" and numbers_parallel[-from_the_end] - numbers_parallel[from_the_beginning] == len(numbers) - from_the_beginning - from_the_end > 2:
                        difference = numbers_parallel[-from_the_end] - numbers_parallel[from_the_beginning]
                        co = 0
                        while co < difference -1:
                            numbers.pop(from_the_beginning + 1)
                            co += 1
                        numbers.insert(from_the_beginning + 1, "-")
                        #numbers[y:] = [str(x) for x in numbers_parallel[y:]]
                    from_the_end += 1
                from_the_beginning += 1
        y += 1

#Reading the data from excel macro
excel = pd.read_excel(PATH_TO_EXCEL_FILE)
clients = excel["Unnamed: 1"][3:].to_list()
nlcn = excel["Unnamed: 3"][3:].to_list()
names = excel["Unnamed: 2"][3:].to_list()
banq_domi = excel["Unnamed: 5"][3:].to_list()
echeance = excel["Unnamed: 7"][3:].to_list()
details = excel["Unnamed: 8"][3:].to_list()
montants = excel["Unnamed: 4"][3:].to_list()

#Ensuring customer numbers are of type int
clients = [int(i) for i in clients]

#Detecting incosistencies in customers' names and numbers
df2 = pd.DataFrame({"clients":clients, "names":names})

name_counts = df2.groupby('names')['clients'].nunique()
inconsistent_rows = df2[df2['names'].isin(name_counts[name_counts > 1].index)]

if len(inconsistent_rows) > 0:
    print(f"{bcolors.FAIL}There are inconsistencies in customers' numbers and names, please check.{bcolors.ENDC}\n")
    print(inconsistent_rows)
    print()

#Getting rid of the leading zeros from nlcn
y = -1
while y < len(nlcn) - 1:
    y += 1
    try:
        nlcn[y] = int(nlcn[y])
    except:
        continue

#Program can use automatically the current date or ask the user, it can be adjusted, just (un)comment this:
saving_date = input("Enter saving date or y to use the current one.\n")
if saving_date == "y":
    saving_date = date.today().strftime("%d/%m/%Y")

#And (un)comment this:
# saving_date = date.today().strftime("%d/%m/%Y")

date_length = len(saving_date) + 2

#Removing lines with ci-joint and avance and merging references from lines with no nlcn and checking for "SOLDE" in the details
text_only_line_removed = False
to_remove = []
for h, de in enumerate(details):
    try:
        if str(de).upper().strip() in ["SOLDE DU COMPTE","SOLDE","LE SOLDE","SOLDE COMPTE"]:
            details[h] = 0
        elif pd.isna(nlcn[h]):
            if clients[h] and de:
                details[h+1] = str(details[h+1]) + "/" + str(details[h])
                to_remove.append(h)
        elif str(de).upper() in ["AVANCE", "CI-JOINT","CI JOINT", "CI ATTACHE", "CI-ATTACHE"] or pd.isna(de):
            to_remove.append(h)
        elif text_only(de):
            text_only_line_removed = True
            to_remove.append(h)
    except AttributeError:
        print("AttributeError")

for h in reversed(to_remove):
    remove_line(h)
if not clients:
    input(f"{bcolors.FAIL}The file has no lines with details. You probably forgot to save it.{bcolors.ENDC}\n")

#Function for shortening consecutive bills of exchange
def shortening():
    gathered_nlcn = []
    for n in box:
        gathered_nlcn.append(nlcn[n])
    sorted_nlcn = sorted(gathered_nlcn)
    for n, m in  zip(box, range(len(box))):
        nlcn[n] = sorted_nlcn[m]
    #nlcn[box[0]:box[-1]+1] = sorted_nlcn
    previous = int(nlcn[box[0]])
    for z in box[1:]:
        current = int(nlcn[z])
        for power in range(2, len(str(nlcn[z]))):
            if current // 10**power == previous // 10**power:
                nlcn[z] = str(nlcn[z])[-power:]
                break
        previous = current

#Detecting consecutive bills of exchange numbers in order to shorten them
unique_details = {(client, detail, bq) : list() for detail, client, bq in zip(details, clients, banq_domi)}

for i, (client, detail, bq) in enumerate(zip(clients, details, banq_domi)):
    unique_details[(client,detail, bq)].append(i)

for detail in unique_details:
    if len(unique_details[detail]) > 1:
        box = [unique_details[detail][0]]
        for y in unique_details[detail][1:]:
            if can_merge(box[-1],y) and differs_by_up_to_fifty(nlcn[box[-1]], nlcn[y]):
                box.append(y)
            else:
                if len(box) > 1:
                    shortening()
                box = [y]

        #Handle the last box
        if len(box) > 1:
            shortening()

#Merging bills of exchange numers and bank abbreviations
boes = [pd.NA] * len(nlcn)
for detail in unique_details:
    if len(unique_details[detail]) == 1:
        boes[unique_details[detail][0]] = str(nlcn[unique_details[detail][0]]) + "/" + banq_domi[unique_details[detail][0]]
    else:
        group = [unique_details[detail][0]]  # Start with the first index

        for i,x in enumerate(unique_details[detail][1:]):
            if can_merge(group[-1], x):
                group.append(x)
            else:
                # Merge current group
                numbers = [str(nlcn[i]) for i in group]
                #Checking if we can connect shortened nlcn with a dash
                connecting(numbers)
                suffix = "/" + banq_domi[group[0]]
                merged = "+".join(numbers) + suffix
                if "+-+" in merged:
                    merged = merged.replace("+-+", "-")
                for i in group:
                    boes[i] = merged
                group = [x]
                
            # Handle the last group
            if group and i == len(unique_details[detail]) - 2:
                numbers = [str(nlcn[i]) for i in group]
                connecting(numbers)
                suffix = "/" + banq_domi[group[0]]
                merged = "+".join(numbers) + suffix
                if "+-+" in merged:
                    merged = merged.replace("+-+", "-")
                for i in group:
                    boes[i] = merged

#Creating final data
final_data = dict()
accounts = list(dict.fromkeys(clients))

details = list(tuple(clean(x)) for x in details)

repeated_accounts = []
repeated_details = []
for i, account in enumerate(accounts):
    if clients.count(account) == 1:
        ind = clients.index(account)
        final_data[account] = {details[ind] : (boes[ind], saving_date + " due " + date_format(echeance[ind]), str(round(montants[ind], 2)) + " MAD")}
    else:
        for j, account_in_clients in enumerate(clients):
            if account == account_in_clients:
                repeated_accounts.append(j)
        final_data[account] = {details[k] : (boes[k], saving_date + \
        " due " + date_format(echeance[k]), str(round(montants[k], 2)) + " MAD") for k in repeated_accounts}
        repeated_accounts = []

#Checking for duplicate details and customer numbers
invoices = list(dict.fromkeys(details))
for detail in invoices:
    if details.count(detail) > 1:
        new_amount = 0
        for a, det in enumerate(details):
            if detail == det and (not repeated_accounts or clients[repeated_accounts[-1]] == clients[a]):
                repeated_details.append(a)
                if not repeated_accounts:
                    repeated_accounts.append(a)
            else:
                continue
        for g in repeated_details:
            new_amount += montants[g]
        for e in repeated_details:
            montants[e] = new_amount
        
        #Removing duplicate merged boe references
        if repeated_details:
          final_data[clients[repeated_details[0]]][detail] = tuple(set(boes[b] for b in repeated_details)) + \
          (saving_date,) + tuple(set(" " + str(round(montants[b], 2)) + " MAD" for b in repeated_details))
        repeated_details = []
        repeated_accounts = []

pprint(final_data,sort_dicts=False)

if text_only_line_removed:
    print(f"\n{bcolors.FAIL}A line with no number in detail has been removed, it should be examined.{bcolors.ENDC}\n")

input("Write anything to continue.\n")
clipboard = list()

# Connecting to ERP - part removed

#Main loop - part removed due to confidentiality

ex = input("Write anything to exit the program\n").lower()

while ex not in list("{:c}".format(x) for x in range(97, 123)) + list(str(x) for x in range(10)):

    ex = input("Write anything to exit the program\n").lower()



