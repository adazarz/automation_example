This is just an example of automation and it neither includes any company-specific data nor is a property of any company. It's here just for presentational purposes. The part of the code that interacts with SAP is not published here.

There is version with graphical user interface as well as terminal-olnly version. The aim of the program is to read and process data from an excel file and use them to change descriptions and reason codes of the items in SAP FBL5N transaction.

How the program reads data from excel

At the beginning it asks about the saving date, it proposes the current one:

<img width="1048" height="309" alt="image" src="https://github.com/user-attachments/assets/0b402d83-8037-4bac-8b39-01316567fdc8" />
>

It uses the columns highlighted below:
<img width="1129" height="184" alt="image" src="https://github.com/user-attachments/assets/fe992366-2964-4121-9dd1-3b8ff1fe91e9" />

The program skips the lines with ci-joint and avance, speaking precisely all the lines where the detail is among (lower or upper case):
<img width="740" height="39" alt="image" src="https://github.com/user-attachments/assets/0aee3d8c-58c3-4c99-a20a-0a878b8b8ca2" />

<img width="1004" height="141" alt="image" src="https://github.com/user-attachments/assets/23494434-fd3c-4a35-bfdc-d0b3a48d34ba" />

<img width="1090" height="371" alt="image" src="https://github.com/user-attachments/assets/f2ba8fc6-e3f3-421b-a41f-696e61c22442" />

If a detail is among:
 <img width="638" height="34" alt="image" src="https://github.com/user-attachments/assets/4454a49a-d1ea-4edc-9e70-5312b33b9745" />

the program will code the detail as 0 and later try to describe all the items on the account:

If there are inconsistencies in the numbers of customers, it will warn you about this at the beginning:
<img width="671" height="146" alt="image" src="https://github.com/user-attachments/assets/b2ad5180-c60c-4cf1-89b3-be0394c74d49" />

<img width="1090" height="267" alt="image" src="https://github.com/user-attachments/assets/299bf297-557c-41a3-81ea-2ddffa9a38ed" />

The program treats everything that isn’t a number in detail column just as a separation of items’ numbers:
<img width="501" height="196" alt="image" src="https://github.com/user-attachments/assets/33ae3ec5-1130-4649-a0c1-b03e27711d3a" />

For BOEs with the same detail, bank abbreviation and fairly consecutive numbers, it concatenates the references like so:
<img width="1148" height="92" alt="image" src="https://github.com/user-attachments/assets/e9a7cd01-6eab-44b7-b697-cc7310b9604d" />

<img width="940" height="185" alt="image" src="https://github.com/user-attachments/assets/8a1e6eff-5dc5-48d6-8e69-be887eaf4ed8" />

If the bank abbreviations are different, it joins them like so:
<img width="1090" height="113" alt="image" src="https://github.com/user-attachments/assets/b70df5c4-f84e-46e9-b693-a1fedb57e97c" />

<img width="1065" height="142" alt="image" src="https://github.com/user-attachments/assets/f3c91a8c-9eca-4512-b737-0a828e9f782a" />

If the number of BOEs with the same detail is large enough (more than four) and their reference numbers are precisely consecutive, it joins them with a dash:
<img width="1090" height="122" alt="image" src="https://github.com/user-attachments/assets/8df779a2-fea9-4bf5-a517-1217f0254a5a" />

If there is more than one boe assigned to a detail, the program doesn’t use a due date in the description, as these due dates are always different.
The program also understands the details written in such a way:
<img width="1090" height="298" alt="image" src="https://github.com/user-attachments/assets/f3a1d25c-ff6b-464b-b28e-276737dc53af" />

<img width="1090" height="154" alt="image" src="https://github.com/user-attachments/assets/e4d572ca-d9cb-41c9-8700-eb60f955a309" />

If there are big differences in invoice numbers lengths, it will elaborate the shorter endings in order to avoid filtering out unnecessary invoices:
<img width="1090" height="139" alt="image" src="https://github.com/user-attachments/assets/3031e609-ef4a-44ee-8347-ce535a01171b" />

<img width="779" height="128" alt="image" src="https://github.com/user-attachments/assets/8fba4a9a-7520-4b08-9e35-c240ab53ceb9" />

The program uses clipboard to paste the invoice numbers into filtering window in SAP fbl5n, so be ware of using copy/paste during the program work.
<img width="1090" height="322" alt="image" src="https://github.com/user-attachments/assets/f2f50fec-daec-4af3-8b21-5f387a0aeb73" />
