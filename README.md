## Flask-Billing_System

### Intrudaction
Rest API for money transfers between banks.<br/>

### This API have single API call:
perform_advance (dst_bank_account, amount) -(a POST reuest)<br/>
The system credits the customer with the amount.<br/>
In the following 12 weeks, the system performs debits of amount/12 once a week.<br/>
A failed debit is moved to the end of the repayment plan (a week from the last payment).

### Notes
This server has default port number 3000.<br/>
To run the server please install all the libraries at the requirements.txt file, and then run the file main.py<br/>
In order to ensure the execution of future transactions, the use of the apscheduler library was implemented, which saves the tasks that created in an external SQLAlchemy database file.<br/>
This API make use in a separate API project "Flask-Transactions_System" a system that create transactions and allows to download a transactions report five days back.

### Links
Documentation page:<br/>
https://documenter.getpostman.com/view/20844564/2s8YeptYRb<br/><br/>
Flask-Transactions_System:<br/>
https://github.com/MaorCaspi/Flask-Transactions_System<br/><br/>

Author: Maor Caspi<br/>
Date: December 2022
