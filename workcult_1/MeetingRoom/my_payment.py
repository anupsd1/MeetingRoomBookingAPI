import razorpay, requests
client = razorpay.Client(auth=("rzp_live_RUZd9hmSQpstnm", "ySdmpH4vKgloCSqlZa0squvq"))


def get_customer(customer_id):
    razorpay_client = client.customer.fetch(customer_id=customer_id)
    print(razorpay_client)


def create_invoice(company_id, minutes):
    hours = minutes / 60
    razorpay_client = client.customer.fetch(customer_id=company_id)
    mydata = {
        "type": "invoice",
        "invoice_number": "0086",
        "customer_id": str(razorpay_client["id"]),
        "line_items": [
            {
                "name": "Meeting Room",
                "description": "Booked for " + str(hours),
                "amount": 399,
                "currency": "INR",
                "quantity": 1
            }
        ],
        "sms_notify": 1,
        "email_notify": 1
    }

    razorpay_invoice = client.invoice.create(data=mydata)
    print(razorpay_invoice)


def make_curl_request():
    url = 'https://www.googleapis.com/qpxExpress/v1/trips/search?key=mykeyhere'
    payload = open("request.json")
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=payload, headers=headers)

def do_payment(company_name, email, total_amount):
# def do_payment(request):
    # print(str(client))
    # for key, value in client:
    #     print(str(key) + ": " + str(value))
    # print(dir(client))
    # print(iter(client))


    payload = {
        "customer": {
            "name": company_name,
            "email": email,
            # "contact": "9823274481"
        },
        "type": "link",

        "amount": int(total_amount) * 100,
        "currency": "INR",
        "description": "Meeting Room",
        "sms_notify": 0,
        # "email_notify": 1
    }
    # url = 'https://api.razorpay.com/v1/invoices/'
    #
    #
    # headers = {'Accept-Charset': 'UTF-8'}
    # r = requests.post(auth=("rzp_live_RUZd9hmSQpstnm", "ySdmpH4vKgloCSqlZa0squvq"), url=url,  data=payload, headers=headers)
    # print("R CODE = " + str(r))
    # print("R = " + str(r.json()))
    obj = client.invoice.create(payload)
    print("OBJ = " + str(obj))

def do_payment2(request):
    payload = {
        "customer": {
            "name": "Acme Enterprises",
            "email": "anup95dev@gmail.com",
            "contact": "9823274481"
        },
        "type": "link",
        "amount": "800.00",
        "currency": "INR",
        "description": "Meeting Room",
        "sms_notify": 1,
        "email_notify": 1
    }
    r = client.payment.create(payload)
    print("RESPONSE = " + str(r))


def do_payment3(request):
    payload = {
        "amount": "400",
        "currency": "INR",
        "payment_capture": 1
        # notes(optional)  : notes for order (optional)
    }

    retu = client.order.create(data=payload)

    print(str(retu))