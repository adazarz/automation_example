import pandas as pd
import win32com.client
from datetime import date
from ttkbootstrap import ttk
import ttkbootstrap as ttk
from pandastable import Table
import threading

class My_string(ttk.StringVar):
    def append(self, text):
        self.set(str(self.get()) + text)

root = ttk.Window(themename="flatly", resizable=(True,True))
root.title("")
var = ttk.BooleanVar()
skip_var = ttk.BooleanVar()
info = My_string()
active_row = 0

df3 = pd.DataFrame()
main_frame = ttk.Frame(root, padding=(5,5))
main_frame.pack(padx=5, pady=5)
frame = ttk.Frame(root, padding=(5,5))
frame.pack(fill="both", expand=True)
info_label = ttk.Label(main_frame, textvariable=info, font=("Courier New", 11), wraplength=600)
info_label.grid(column=2, row=0, columnspan=3, rowspan=3)


def define_width(df):
    # Convert all cells to strings and calculate the length of each cell
    cell_lengths = df.astype(str).map(len)

    # Sum the lengths of all cells in each row
    max_row_length = cell_lengths.sum(axis=1).max()
    if max_row_length < 100:
        return max_row_length*12 + 60
    else:
        return 1200
    
def cell_width(df, table):
    cell_lengths = df.astype(str).map(len)
    for col in cell_lengths:
        table.columnwidths[col] = cell_lengths[col].max() * 9 + 30 if cell_lengths[col].max() < 50 else 500

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
        return echeance.strftime("%d/%m/%y")
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
excel = pd.read_excel(r"C:\Users\azarzyck\Desktop\BOE_Posting_MA20_new_procedure_Beta.xlsm")
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
df2 = pd.DataFrame({"numbers":clients, "names":names})

name_counts = df2.groupby('names')['numbers'].nunique()
inconsistent_rows = df2[df2['names'].isin(name_counts[name_counts > 1].index)]

if len(inconsistent_rows) > 0:
    info.set(f"There are inconsistencies in customers' numbers and names, please check.\n{inconsistent_rows}")
    # print(f"{bcolors.FAIL}There are inconsistencies in customers' numbers and names, please check.{bcolors.ENDC}\n")
    # print(inconsistent_rows)
    # print()

#Getting rid of the leading zeros from nlcn
y = -1
while y < len(nlcn) - 1:
    y += 1
    try:
        nlcn[y] = int(nlcn[y])
    except:
        continue

text_only_line_removed = False

def processing():
    global df3
    global details
    global clients
    global final_data
    global text_only_line_removed
    global date_length
    global pt
    global saving_date
    global delen

    describe_button.config(state=["enabled"])
    date_button.config(state=["disabled"])
    date_entry.config(state=["disabled"])
    saving_date = date_entry.get()
    date_length = len(saving_date) + 2

    #Removing lines with ci-joint and avance and merging references from lines with no nlcn and checking for "SOLDE" in the details
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
                info.set("A line with no number in detail has been removed, it should be examined.")
        except AttributeError:
            pass

    for h in reversed(to_remove):
        remove_line(h)
    if not clients:
        info_label.config(text="The file has no lines with details. You probably forgot to save it.")
        # input(f"{bcolors.FAIL}The file has no lines with details. You probably forgot to save it.{bcolors.ENDC}\n")

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
            final_data[account] = {details[ind] : (boes[ind], saving_date + " due " + date_format(echeance[ind]), format(round(montants[ind], 2), ',') + " MAD")}
        else:
            for j, account_in_clients in enumerate(clients):
                if account == account_in_clients:
                    repeated_accounts.append(j)
            final_data[account] = {details[k] : (boes[k], saving_date + \
            " due " + date_format(echeance[k]), format(round(montants[k], 2), ',') + " MAD") for k in repeated_accounts}
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
                (saving_date,) + tuple(set(" " + format(round(montants[b], 2), ',') + " MAD" for b in repeated_details))
            repeated_details = []
            repeated_accounts = []
    Customer1 = list()
    Detail1 = list()
    Description1 = list()
    Sum1 = list()
    delen = 0
    for c in final_data:
        Customer1 = Customer1 + [str(c)] + [""] * (len(final_data[c]) - 1)
        Detail1 = Detail1 + [d for d in final_data[c]]
        for d in final_data[c]:
            delen += len(d)
            Description1 = Description1 + [list(a for a in final_data[c][d])[:-1]]
            Sum1 = Sum1 + list(a for a in final_data[c][d])[-1:]
    df3 = pd.DataFrame({"Customer" : Customer1,
                        "Detail" : Detail1,
                        "Description" : Description1,
                        "Sum" : Sum1,
                        "Status": ["Planned"] * len(Customer1)})
    df3['Description'] = df3['Description'].apply(lambda x: ' '.join(map(str, x)) if isinstance(x, list) else x)


    root.geometry(f"{define_width(df3)}x{df3.Customer.size*26 + 260}")
    pt = Table(frame, dataframe=df3, cellbackgr="#ffffff", rowselectedcolor="#a6c7ec", grid_color="#ffffff", textcolor="black")
    pt.show()
    #Adjusting the width of the pandastable cells
    cell_width(df3, pt)
    # pt.setRowColors(rows=active_row, clr='lightblue', cols='all')


# if text_only_line_removed:
#     print(f"\n{bcolors.FAIL}A line with no number in detail has been removed, it should be examined.{bcolors.ENDC}\n")

# input("Write anything to continue.\n")

def describe():
    global df3
    global pt
    global text_only_line_removed
    global active_row
    clipboard = list()

    # Connecting to SAP
    sap = win32com.client.GetObject("SAPGUI").GetScriptingEngine
    session = sap.Children(0).Children(0)  # Access first open session

    #Main loop
    for key in final_data:
        skip = False
        skip_var.set(False)
        # Open fbl5n
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nfbl5n"
        session.findById("wnd[0]").sendVKey(0)
        # Filling in the customer number and company code
        session.findById("wnd[0]/usr/ctxtDD_KUNNR-LOW").Text = key
        session.findById("wnd[0]/usr/ctxtDD_BUKRS-LOW").Text = "MA20"
        session.findById("wnd[0]/usr/ctxtPA_VARI").Text = "WEKSLE ADAM"
        # Ensuring that normal items are checked
        session.findById("wnd[0]/usr/chkX_NORM").selected = True
        # Executing
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        #Disabling buttons
        save_button.config(state=["disabled"])
        dont_save_button.config(state=["disabled"])
        # Filling in the references
        for ref in final_data[key].keys():
            #Setting the colour of the active line in pandastable
            pt.setRowColors(rows=range(active_row, active_row+1), clr='lightblue', cols='all')
            info.set("")
            active_row += 1
            if len(final_data[key].keys()) > 1:
                #Refreshing if the customer has more than one detail
                session.findById("wnd[0]").maximize()
                session.findById("wnd[0]/mbar/menu[0]/menu[2]").select()
            # Filtering by references if there was no "le solde" or sth similar
            if ref[0] != 0:
                try:
                    session.findById("wnd[0]/usr/lbl[24,5]").caretPosition = 6
                    session.findById("wnd[0]").sendVKey(2)
                except:
                    # probl = ""
                    save_button.config(state=["enabled"])
                    info.set("Wrong customer number, write the correct one in SAP and click save to continue.")
                    # while probl != "y":
                    #     probl = input("Wrong customer number, write the correct one in SAP and write y to continue/ctrl+c to terminate\n").lower()
                    #Two reapeted lines
                    root.wait_variable(var)
                    save_button.config(state=["disabled"])
                    if var.get() == True:
                      session.findById("wnd[0]/tbar[1]/btn[8]").press()
                      session.findById("wnd[0]/usr/lbl[24,5]").caretPosition = 6
                      session.findById("wnd[0]").sendVKey(2)
                      save_button.config(state=["disabled"])

                session.findById("wnd[0]/tbar[1]/btn[38]").press()
                session.findById(r"wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/btn%_%%DYN001_%_APP_%-VALU_PUSH").press()
                #Resetting the clipboard
                clipboard = []
                for i, bare_ref in enumerate(ref):
                    clipboard.append("*" + str(bare_ref))
                df = pd.DataFrame(clipboard[1:], columns=[clipboard[0]])
                # Copy the DataFrame to the clipboard
                df.to_clipboard(index=False)
                #Copying from clipboard
                session.findById("wnd[2]/tbar[0]/btn[24]").press()
                #Executing filtr
                session.findById("wnd[2]/tbar[0]/btn[8]").press()
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            else:
                items_on_account = int(session.findById("wnd[0]/sbar").text[:-16])
            #Checking the sum and reason code's of the filtered invoices in SAP
            items_sum = 0
            empty_rc = False
            with_rc = 0
            #Necessary for handling solde
            if ref[0] != 0:
                len_ref = len(ref)
            else:
                len_ref = items_on_account
            try:
                if len_ref < 35:
                    items_sum = float(session.findById(f"wnd[0]/usr/lbl[106,{len_ref+8}]").text.strip().replace("," ,""))
                    line_number = 7
                    while line_number < len_ref+7 and not with_rc:
                        #session.findById(f"wnd[0]/usr/lbl[123,{line_number}]").setFocus()
                        if session.findById(f"wnd[0]/usr/lbl[123,{line_number}]").text != "":
                            with_rc += 1
                        line_number += 1
                    if not with_rc:
                        empty_rc = True
                    else:
                        info.set("There is an item with reason code.")

                    #Getting the document number below the last item. If empty, indicates that there are not too many items
                    if ref[0] != 0:
                        blank = session.findById(f"wnd[0]/usr/lbl[95,{len(ref)+8}]").text
                        if blank == "":
                            invoice_amount_match = True
                        else:
                            invoice_amount_match = False
                            info.append("\nThe amount of invoices doesn't match")
                            # print("The amount of invoices doesn't match")
                else:
                    left_lines = len_ref
                    line_number = 7
                    while line_number < left_lines + 7:
                        #session.findById(f"wnd[0]/usr/lbl[123,{line_number}]").setFocus()
                        try:
                            if session.findById(f"wnd[0]/usr/lbl[123,{line_number}]").text != "":
                                with_rc += 1
                            line_number += 1
                        except:
                            left_lines = left_lines - line_number + 7
                            if left_lines > 0:
                                session.findById("wnd[0]").maximize()
                                session.findById("wnd[0]").sendVKey(82)
                                line_number = 7
                            else:
                                break
                    if not with_rc:
                        empty_rc = True
                    else:
                        info.append("\nThere is an item with reason code.")
                        # print("There is an item with reason code.")
                    #session.findById(f"wnd[0]/usr/lbl[106,{line_number+2}]").setFocus()
                    try:
                        items_sum = float(session.findById(f"wnd[0]/usr/lbl[106,{line_number+1}]").text.strip().replace("," ,""))
                        blank = session.findById(f"wnd[0]/usr/lbl[95,{line_number+1}]").text
                    except:
                        #Handling cases where only the sum of the invoices is on the next page
                        session.findById("wnd[0]").maximize()
                        session.findById("wnd[0]").sendVKey(82)
                        items_sum = float(session.findById(f"wnd[0]/usr/lbl[106,8]").text.strip().replace("," ,""))
                        blank = session.findById(f"wnd[0]/usr/lbl[95,8]").text
                        
                    #Ensuring the number of items in SAP match the number items from excel
                    if blank == "":
                        invoice_amount_match = True
                    else:
                        invoice_amount_match = False
                        info.append("\nThe amount of invoices doesn't match")
                        # print("The amount of invoices doesn't match")
            except:
                try:
                    if session.findById(f"wnd[0]/usr/lbl[106,{len_ref+9}]").text.strip().replace("," ,""):
                        info.append("\nThere is one item too much.")
                except:
                    info.append("\nNot all of the invoices have been found.")
                # print("Not all of the invoices have been found.")
            # print(items_sum)
            with_rc = 0
            #Selecting all
            #session.findById("wnd[0]/usr/lbl[1,5]").setFocus()
            session.findById("wnd[0]/usr/lbl[1,5]").caretPosition = 0
            session.findById("wnd[0]").sendVKey(5)
            #Opening mass change
            session.findById("wnd[0]/tbar[1]/btn[45]").press()
            #Filling in the text and reason code
            session.findById("wnd[0]").maximize()
            session.findById("wnd[0]/tbar[1]/btn[45]").press()
            #Creating description
            description = str()
            for piece in final_data[key][ref][:-1]:
                description += piece
                description += " "
            #Shortening too long descriptions by removing a date
            description_too_long = False
            if len(description) > 50:
                description = description[:-date_length]
                if len(description) > 50:
                    description_too_long = True
                    info.append(text="The description was far too long, you will have to fill it in manually.")
                    # print("The description was far too long, you will have to fill it in manually.")
                else:
                    info.append("\nThe description was too long, the date has been removed")
                    # print("The description was too long, the date has been removed")
            #If there are no such invoices in a customer account, this one goes wrong
            try:
                if description_too_long:
                    session.findById("wnd[1]/usr/ctxt*BSEG-RSTGR").text = "ABD"
                    save_button.config(state=["enabled"])
                    dont_save_button.config(state=["enabled"])
                else:
                    session.findById("wnd[1]/usr/txt*BSEG-SGTXT").text = description
                    session.findById("wnd[1]/usr/ctxt*BSEG-RSTGR").text = "ABD"
            except:
                # print(ref, final_data[key][ref])
                save_button.config(state=["enabled"])
                dont_save_button.config(state=["enabled"])
                skip_button.config(state=["enabled"])
                info.set("There are no such invoices in this account."
                                    " You can open correct customer account and press save to continue, press don't save to skip the current detail skip this customer altogether. If the customer is correct but there was a typo in the detail, save manually and press don't save.")
                root.wait_variable(var)
                save_button.config(state=["disabled"])
                dont_save_button.config(state=["disabled"])
                skip_button.config(state=["disabled"])
                # problem = input("There are no such invoices in this account."
                #                     " You can open correct customer account and write y to continue, write n to skip the current detail or s to skip this customer altogether. If the customer is correct but there was a typo in the detail, save manually and write n.\n")
                # while problem not in ["y","n","s"]:
                #     problem = input()
                if var.get() == True:
                    #Repeated lines from above till the next try
                    session.findById("wnd[0]/usr/lbl[24,5]").caretPosition = 6
                    session.findById("wnd[0]").sendVKey(2)
                    session.findById("wnd[0]/tbar[1]/btn[38]").press()
                    session.findById(r"wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/btn%_%%DYN001_%_APP_%-VALU_PUSH").press()
                    for i, bare_ref in enumerate(ref):
                        session.findById(f"wnd[2]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,{i}]")\
                        .text = "*" + str(bare_ref)
                        session.findById("wnd[2]/tbar[0]/btn[8]").press()
                        session.findById("wnd[1]/tbar[0]/btn[0]").press()
                        session.findById("wnd[0]/usr/lbl[1,5]").setFocus()
                        session.findById("wnd[0]/usr/lbl[1,5]").caretPosition = 0
                        #Opening mass change
                        session.findById("wnd[0]").sendVKey(5)
                        session.findById("wnd[0]/tbar[1]/btn[45]").press()
                        #Filling in the text and reason code
                        session.findById("wnd[0]").maximize()
                        session.findById("wnd[0]/tbar[1]/btn[45]").press()
                        #Creating description
                        description = str()
                        for piece in final_data[key][ref][:-1]:
                            description += piece
                            description += " "
                        session.findById("wnd[1]/usr/txt*BSEG-SGTXT").text = description
                        session.findById("wnd[1]/usr/ctxt*BSEG-RSTGR").text = "ABD"
                elif var.get() == False and skip_var.get() == False:
                    #Some colour indicating the line has been skipped
                    # print(pd.DataFrame(final_data[key][ref]))
                    continue
                elif skip_var.get() == True:
                    skip = True
                    break
            try:
                correct_amount = items_sum == float(final_data[key][ref][-1].replace("MAD", "").replace(',', '').strip())
                if not correct_amount:
                    diff = round(items_sum - float(final_data[key][ref][-1].replace("MAD", "").replace(',', '').strip()), 2)
                    info.append(f"\nIncorrect amount, SAP {items_sum} diff {diff}")
                    diff_text.config(state=["enabled"])
                    diff_value.set(value=diff)
                    
                if description_too_long:
                    save_button.config(state=["enabled"])
                    dont_save_button.config(state=["enabled"])
                    root.wait_variable(var)
                    info.append(f"\n{ref} {final_data[key][ref]} Fill in the description manually and click save/don't save.\n")
                elif correct_amount and empty_rc and invoice_amount_match:
                    #Saving automatically
                    # print(f"Saved. {ref} {final_data[key][ref]}\n")
                    var.set(True)
                else:
                    save_button.config(state=["enabled"])
                    dont_save_button.config(state=["enabled"])
                    root.wait_variable(var)
                    df3.loc[active_row-1, "Status"] = "Unknown"
                    # pt.redraw()
                    # answer = input(f"Execute mass change? y/n {ref} {final_data[key][ref]}\n").lower()

            except Exception as e:
                input("Exception",e)
            # while answer not in ["y","n"]:
            #     answer = input("Write y or n.\n")
            bar.config(value=(active_row / df3["Customer"].size) * 100)
            percent.config(text=f"{int((active_row / df3["Customer"].size) * 100)} %")
            if var.get() == True:
                #Executing mass change
                try:
                    session.findById("wnd[1]/usr/ctxt*BSEG-RSTGR").setFocus()
                    session.findById("wnd[1]/usr/ctxt*BSEG-RSTGR").caretPosition = 3
                    session.findById("wnd[1]/tbar[0]/btn[0]").press()
                    #Changing the status and line colors in gui
                    pt.setRowColors(rows=range(active_row-1, active_row), clr='lightgreen', cols='all')
                    df3.loc[active_row - 1, "Status"] = "Saved"
                except:
                    info.set("I haven't described")
                    info.append("\n",final_data[key][ref])
            elif var.get() == False:
                try:
                    # print(pd.DataFrame(final_data[key][ref]))
                    info.set("")
                    session.findById("wnd[1]").close()
                    pt.setRowColors(rows=range(active_row-1, active_row), clr='#ffff99', cols='all')
                except:
                    pass
        diff_value.set(value=0)
        diff_text.config(state=["disabled"])
        pt.redraw()
        if skip:
            df3.loc[active_row-1 : active_row+len(final_data[key])-2, "Status"] = "Skipped"
            pt.setRowColors(rows=range(active_row-1, active_row+len(final_data[key])-1), clr='#ffff99', cols='all')
            active_row += len(final_data[key]) - 1
            info.set("")
            continue
    #Updating a log
    with open("descibe_log.txt", "a") as l:
        l.write("\n-------------------------------------------------------------------------------\n")
        l.write("Real date " + date.today().strftime("%d/%m/%y") + "\nSaving date " + saving_date + "\n")
        l.write("Planned items " + str(delen) + "\n")
        l.write(df3.to_string())

    info.set("The program has terminated the work.")
    # ex = input("Write anything to exit the program\n").lower()

    # while ex not in list("{:c}".format(x) for x in range(97, 123)) + list(str(x) for x in range(10)):
    #     ex = input("Write anything to exit the program\n").lower()

#Gui
bar = ttk.Progressbar(main_frame, value=0, length=700, mode="determinate", style="success.Striped.Horizontal.TProgressbar")
bar.grid(column=0, row=4, columnspan=4, sticky = ttk.W + ttk.E, pady=15)
percent = ttk.Label(main_frame, text="0 %", font=("Courier New", 11))
percent.grid(column=4, row=4, sticky=ttk.W, padx=10)
label1 = ttk.Label(main_frame,text="Write the saving date:", font=("Courier New", 11))
label1.grid(column=0, row=0)
default_date = ttk.StringVar(value=f"{date.today().strftime("%d/%m/%y")}")
date_entry = ttk.Entry(main_frame, width=18, font=("Courier New", 11), textvariable=default_date)
date_entry.grid(column=0, row=1)
date_entry.focus_set()
diff_value = ttk.IntVar(value=0)
diff_label = ttk.Label(main_frame, text="Diff", font=("Courier New", 11))
diff_label.grid(column=0, row=2, padx=1, pady=1)
diff_text = ttk.Entry(main_frame, state="disabled", font=("Courier New", 10), textvariable=diff_value)
diff_text.grid(column=0, row=2, padx=1, pady=1)
date_button = ttk.Button(main_frame, text="Use this date", command=processing)
describe_button = ttk.Button(main_frame, text="Describe invoices", command=lambda: threading.Thread(target=describe).start(), state="disabled")
save_button = ttk.Button(main_frame, text="Save", state="disabled", command=lambda: var.set(True))
save_button.grid(column=2, row=3, padx=2)
dont_save_button = ttk.Button(main_frame, text="Don't save", state="disabled", command=lambda: var.set(False))
dont_save_button.grid(column=3,row=3, padx=2, sticky=ttk.W)
describe_button.grid(column=1, row=2, padx=2, pady=2)
date_button.grid(column=1, row=1, padx=2, pady=2)
skip_button = ttk.Button(main_frame, text="Skip customer", state="disabled", command=lambda: (skip_var.set(True), var.set(False)))
skip_button.grid(column=4, row=3)

step = 1
def enter():
    global step
    match step:
        case 1:
            step += 1
            processing()
        case 2:
            threading.Thread(target=describe).start()

root.bind("<Return>",lambda event: enter())

root.mainloop()