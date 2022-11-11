import requests, datetime
from flask import Flask
from flask_restful import reqparse
from urllib import request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from config import Config

app = Flask(__name__)

def did_transaction_succeeded(transaction_id):
    """
    The function recive transaction_id and check the transaction status.
    If the trunsaction status is success -> return True, else return False.
    """
    try:
        with request.urlopen(Config.PROCESSOR_URL) as f:
            report_from_processor = f.read().decode('utf-8')
            index_of_transaction_id_on_report = report_from_processor.rfind(transaction_id)

            if index_of_transaction_id_on_report == -1 : # If the transaction_id not fount in the report
                raise Exception
            
            line = report_from_processor[index_of_transaction_id_on_report:].splitlines()[0]
            transaction_status = line[line.find(',')+1:] # success/fail
            
            if transaction_status == "success":
                return True
            return False
    
    except:
            raise Exception("Problem with getting the report from the Processor server")

    
def perform_debit(dst_bank_account, amount, end_repayment_plan_date):
    """
    The function perform a debit to dst_bank_account by amounts.
    If the trunsaction status is success -> return True, else return False.
    """
    parameters_to_processor = {
                                "src_bank_account" : Config.SRC_BANK_ACCOUNT,
                                "dst_bank_account" : dst_bank_account,
                                "amount" : amount,
                                "direction": "debit"
                              }
                              
    try:
        res = requests.post(Config.PROCESSOR_URL, json = parameters_to_processor)
        if res.status_code == 200 :
            transaction_id = res.text[1:-2] # Remove the quotation marks and the new line and save it
            if not did_transaction_succeeded(transaction_id): # If the debit transaction failed
                try:
                    scheduler.add_job(perform_debit, 'date', run_date=end_repayment_plan_date, args=[dst_bank_account, amount, end_repayment_plan_date])
                except:
                    raise Exception("Failed to send job to scheduler")
        else:
            raise Exception("There was an error on the Processor server while tring perform transaction: " + res.text)
    except:
            raise Exception("The Processor server is unavailable")

scheduler = BackgroundScheduler(jobstores = {'default': SQLAlchemyJobStore(url=Config.DB_URL)}, job_defaults={'misfire_grace_time': None})
scheduler.start()

@app.route('/', methods=['POST'])
def perform_advance():
    """
    The system credits the customer with the amount.
    In the following 12 weeks, the system performs debits of amount/12 once a week.
    A failed debit is moved to the end of the repayment plan (a week from the last payment).
    """

    parser = reqparse.RequestParser() # Validate body parames for perform advance
    parser.add_argument("dst_bank_account", type=str, help="dst_bank_account is required", required=True)
    parser.add_argument("amount", type=float, help="amount is required", required=True)

    args = parser.parse_args()
    end_repayment_plan_date = datetime.datetime.now() + datetime.timedelta(7*12,0) # Run in the following 12 weeks
    for i in range(12):
        run_start_date = datetime.datetime.now() + datetime.timedelta(7*i,0) # Run in the following 12 weeks
        try:
            scheduler.add_job(perform_debit, 'date', run_date=run_start_date, args=[args["dst_bank_account"], args["amount"]/12, end_repayment_plan_date])
        except:
            raise Exception("Failed to send job to scheduler")

        return("OK", 200)

if __name__ == "__main__":
	app.run(debug = False, port = Config.FLASK_PORT_NUMBER)