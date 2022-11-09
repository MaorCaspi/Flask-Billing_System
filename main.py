import requests
from flask import Flask
from flask_restful import Api, Resource, reqparse
from urllib import request

PROCESSOR_URL = "http://127.0.0.1:5000"
SRC_BANK_ACCOUNT = "424158"

app = Flask(__name__)
api = Api(app)

perform_advance_args = reqparse.RequestParser() # Validate body parames for perform advance
perform_advance_args.add_argument("dst_bank_account", type=str, help="dst_bank_account is required", required=True)
perform_advance_args.add_argument("amount", type=float, help="amount is required", required=True)

def did_transaction_succeeded(transaction_id):
    '''
    The function recive transaction_id and check the transaction status.
    : If the trunsaction status is success -> return True, else return False.
    '''
    try:
        with request.urlopen(PROCESSOR_URL) as f:
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

    
def perform_debit(dst_bank_account, amount):
    '''
    The function perform a debit to dst_bank_account by amounts.
    : If the trunsaction status is success -> return True, else return False.
    '''
    parameters_to_processor = {
                                "src_bank_account" : SRC_BANK_ACCOUNT,
                                "dst_bank_account" : dst_bank_account,
                                "amount" : amount,
                                "direction": "debit"
                              }
                              
    try:
        res = requests.post(PROCESSOR_URL, json = parameters_to_processor)
        if res.status_code == 200 :
            transaction_id = res.text[1:-2] # Remove the quotation marks and the new line and save it
            if not did_transaction_succeeded(transaction_id): # If the debit transaction failed
                print("!!!!!!!!!!")###########################
        else:
            raise Exception("There was an error on the Processor server while tring perform transaction: " + res.text)
    except:
            raise Exception("The Processor server is unavailable")


class Advance(Resource):
    def post(self):
        '''
        The system credits the customer with the amount.
        :In the following 12 weeks, the system performs debits of amount/12 once a week.
        :A failed debit is moved to the end of the repayment plan (a week from the last payment).
        '''
        args = perform_advance_args.parse_args()
        perform_debit(args["dst_bank_account"], args["amount"]) ################

        return("OK", 200)

api.add_resource(Advance, "/")

if __name__ == "__main__":
	app.run(debug = False, port = 3000)