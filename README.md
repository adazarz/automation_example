The aim of the program is to automate describing customer items. It takes the data from excel file, processes them and uses to change documents' texts and reason codes in the ERP system. It takes from excel file customer numbers, bill of exchange numbers, their sums and invoice numbers that are planned for payment with these bills of exchange. It also checks if there are no inconsistencies in the customer numbers.

How the program reads data from excel

At the beginning it asks about the saving date, it proposes the current one:

<img width="1048" height="309" alt="image" src="https://github.com/user-attachments/assets/23267e2f-5a14-4901-a1ee-2e1a82cd0730" />

As the program in independent of excel, it’s necessary to save the file for a program to be able to read it.
<img width="1090" height="258" alt="image" src="https://github.com/user-attachments/assets/acb1334e-a882-4bb1-ad82-48e67c4fd820" />

The program skips the lines with ci-joint and avance, speaking precisely all the lines where the detail is among (lower or upper case):

<img width="740" height="39" alt="image" src="https://github.com/user-attachments/assets/9d687a2a-9f3a-4c95-aafc-0f7d05e3bcaa" />

<img width="1004" height="65" alt="image" src="https://github.com/user-attachments/assets/8afd5d1a-1927-4b4f-ad2d-fc5c093fa5c2" />

<img width="1090" height="371" alt="image" src="https://github.com/user-attachments/assets/50f2b2e2-2248-44c1-8292-21eff334d692" />

If a detail is among:
<img width="638" height="34" alt="image" src="https://github.com/user-attachments/assets/5a5ad957-8317-4099-bc71-1b850447a054" />

the program will code the detail as 0 and later try to describe all the items on the account:

<img width="1010" height="60" alt="image" src="https://github.com/user-attachments/assets/3ba0278d-ecc6-4375-957a-3b471a26bfc0" />
<img width="1090" height="162" alt="image" src="https://github.com/user-attachments/assets/c40bcc1f-c1ca-4e2a-b75b-d9856e5b26fb" />

If there are inconsistencies in the numbers of customers, it will warn you about this at the beginning:
<img width="671" height="59" alt="image" src="https://github.com/user-attachments/assets/a5cc9971-2cf3-4fd1-a794-1e8ce21fbaf0" />
<img width="1090" height="267" alt="image" src="https://github.com/user-attachments/assets/f86ceb5b-4e33-438f-945c-1fba284c005b" />

The program treats everything that isn’t a number in detail column just as a separation of items’ numbers:
<img width="501" height="148" alt="image" src="https://github.com/user-attachments/assets/403c44a1-e1cd-4095-8d7e-5887e8e8f2c3" />

<img width="1090" height="141" alt="image" src="https://github.com/user-attachments/assets/6c67a675-537b-488c-88ea-21ce176d2b4c" />

For BOEs with the same detail, bank abbreviation and fairly consecutive numbers, it concatenates the references like so:
<img width="1148" height="97" alt="image" src="https://github.com/user-attachments/assets/5cdf967c-6602-4cb9-90cd-36ebe1376e44" />
<img width="940" height="185" alt="image" src="https://github.com/user-attachments/assets/b4b000ba-7226-49dd-814d-15829c26030c" />

If the bank abbreviations are different, it joins them like so:
<img width="1090" height="113" alt="image" src="https://github.com/user-attachments/assets/53c047c7-d7d5-4cf0-a560-596e32cbc4a3" />
<img width="1065" height="142" alt="image" src="https://github.com/user-attachments/assets/475b259f-8128-441e-9c1f-a6a0cf348b4a" />

If the number of BOEs with the same detail is large enough (more than four) and their reference numbers are precisely consecutive, it joins them with a dash:
<img width="1090" height="122" alt="image" src="https://github.com/user-attachments/assets/bf61d9d7-aad9-42d8-b00c-5fc7a226f493" />

The program also understands the details written in such a way:
<img width="1090" height="292" alt="image" src="https://github.com/user-attachments/assets/46503d4a-f7df-435a-b58f-3ee8f6bf4883" />
<img width="1090" height="154" alt="image" src="https://github.com/user-attachments/assets/dba8f40d-a297-49c4-9f45-d641a491ec27" />

If there are big differences in invoice numbers lengths, it will elaborate the shorter endings in order to avoid filtering out unnecessary invoices:

For detail written in such a way: 22222/23/24/25

<img width="779" height="128" alt="image" src="https://github.com/user-attachments/assets/4a759282-1fa6-47fe-8a29-db73dd3ce570" />

The program uses clipboard to paste the invoice numbers into filtering window in the ERP system, so be ware of using copy/paste during the program work.

<img width="1090" height="322" alt="image" src="https://github.com/user-attachments/assets/cef66560-78c0-4cc8-9936-f8507a024cb6" />
