This is an example of Python automation. The aim of the program is to automate describing customer items. It takes the data from excel file, processes them and uses to change documents' texts and reason codes in the ERP system. It takes from excel file customer numbers, bill of exchange numbers, their sums and invoice numbers that are planned for payment with these bills of exchange. It also checks if there are no inconsistencies in the customer numbers. There a version with graphical user interface, as well as terminal only version.

The program takes numbers of ex. bills of exchange, joins them with an abbreviation of the bank, saving date, due date and the amount of the payment and assigns it to the detail of payment as a description, and the detail of payment is assigned to the number of customer. So the program creates something like small trees where the customer number is a root, details are branches and to these branches are designated descriptions and amounts. The program stores these information as a dictionary of dictionaries, which is later convenient for looping and introducing the date into an ERP software.

The part of the script that deals with the ERP system has been removed due to its confidentiality.

How the program reads data from excel

At the beginning it asks about the saving date, it proposes the current one:

<img width="1048" height="309" alt="image" src="https://github.com/user-attachments/assets/23267e2f-5a14-4901-a1ee-2e1a82cd0730" />

As the program in independent of excel, it’s necessary to save the file for a program to be able to read it.
<img width="1090" height="258" alt="image" src="https://github.com/user-attachments/assets/acb1334e-a882-4bb1-ad82-48e67c4fd820" />

The program skips the lines with ci-joint and avance, speaking precisely all the lines where the detail is among (lower or upper case):

<img width="740" height="39" alt="image" src="https://github.com/user-attachments/assets/9d687a2a-9f3a-4c95-aafc-0f7d05e3bcaa" />

<img width="1004" height="65" alt="image" src="https://github.com/user-attachments/assets/8afd5d1a-1927-4b4f-ad2d-fc5c093fa5c2" />

<img width="1090" height="371" alt="image" src="https://github.com/user-attachments/assets/50f2b2e2-2248-44c1-8292-21eff334d692" />
>

If a detail is among:
<img width="638" height="34" alt="image" src="https://github.com/user-attachments/assets/5a5ad957-8317-4099-bc71-1b850447a054" />

the program will code the detail as 0 and later try to describe all the items on the account:

<img width="1010" height="60" alt="image" src="https://github.com/user-attachments/assets/3ba0278d-ecc6-4375-957a-3b471a26bfc0" />
<img width="1090" height="162" alt="image" src="https://github.com/user-attachments/assets/c40bcc1f-c1ca-4e2a-b75b-d9856e5b26fb" />

If there are inconsistencies in the numbers of customers, it will warn you about this at the beginning:
<img width="671" height="59" alt="image" src="https://github.com/user-attachments/assets/a5cc9971-2cf3-4fd1-a794-1e8ce21fbaf0" />
<img width="1090" height="267" alt="image" src="https://github.com/user-attachments/assets/f86ceb5b-4e33-438f-945c-1fba284c005b" />

The program treats everything that isn’t a number in detail column just as a separation of items’ numbers:
<img width="501" height="68" alt="image" src="https://github.com/user-attachments/assets/1fbe6fd0-9945-4372-9b86-c21571b814a4" />

<img width="1090" height="141" alt="image" src="https://github.com/user-attachments/assets/6c67a675-537b-488c-88ea-21ce176d2b4c" />

For BOEs with the same detail, bank abbreviation and fairly consecutive numbers, it concatenates the references like so:
<img width="1148" height="42" alt="image" src="https://github.com/user-attachments/assets/e2d14dc1-fdc5-4f0d-a32d-2593c69401db" />
<img width="940" height="185" alt="image" src="https://github.com/user-attachments/assets/b4b000ba-7226-49dd-814d-15829c26030c" />

If the bank abbreviations are different, it joins them like so:
<img width="1090" height="53" alt="image" src="https://github.com/user-attachments/assets/f62bc064-234d-46ac-9073-e4ebb68f0017" />
<img width="1065" height="142" alt="image" src="https://github.com/user-attachments/assets/475b259f-8128-441e-9c1f-a6a0cf348b4a" />

If the number of BOEs with the same detail is large enough (more than four) and their reference numbers are precisely consecutive, it joins them with a dash:
<img width="1090" height="122" alt="image" src="https://github.com/user-attachments/assets/bf61d9d7-aad9-42d8-b00c-5fc7a226f493" />

The program also understands the details written in such a way:
<img width="1090" height="216" alt="image" src="https://github.com/user-attachments/assets/a624375b-597a-4dfc-bf15-4f074aeb9b14" />
<img width="1090" height="154" alt="image" src="https://github.com/user-attachments/assets/dba8f40d-a297-49c4-9f45-d641a491ec27" />

If there are big differences in invoice numbers lengths, it will elaborate the shorter endings in order to avoid filtering out unnecessary invoices:

For detail written in such a way: 22222/23/24/25

<img width="779" height="128" alt="image" src="https://github.com/user-attachments/assets/4a759282-1fa6-47fe-8a29-db73dd3ce570" />

The program uses clipboard to paste the invoice numbers into filtering window in the ERP system, so be ware of using copy/paste during the program work.

<img width="1227" height="362" alt="image" src="https://github.com/user-attachments/assets/a9da7ec8-46a5-4068-a198-aca38dc159cf" />

