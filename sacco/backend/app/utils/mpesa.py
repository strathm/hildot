import requests
import base64
from datetime import datetime
from flask import current_app, jsonify

def get_mpesa_access_token():
    """
    Get access token for M-Pesa API using the provided consumer key and secret.
    """
    consumer_key = current_app.config['MPESA_CONSUMER_KEY']
    consumer_secret = current_app.config['MPESA_CONSUMER_SECRET']
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    try:
        response = requests.get(api_url, auth=(consumer_key, consumer_secret))
        response.raise_for_status()  # Raise HTTPError for bad responses
        response_data = response.json()
        return response_data.get("access_token")
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error getting access token: {e}")
        return None  # Return None or handle the error as needed

def initiate_stk_push(phone_number, amount, account_reference, transaction_desc):
    """
    Initiate an M-Pesa STK Push transaction.
    """
    access_token = get_mpesa_access_token()
    
    if not access_token:
        return jsonify({"error": "Failed to retrieve M-Pesa access token."}), 400  # Return an error response

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    business_short_code = current_app.config['MPESA_BUSINESS_SHORTCODE']
    passkey = current_app.config['MPESA_PASSKEY']
    
    # Ensure the password is correctly base64-encoded
    password = base64.b64encode(f"{business_short_code}{passkey}{timestamp}".encode()).decode()

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": current_app.config['MPESA_CALLBACK_URL'],
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()  # Return the API response as JSON
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error initiating STK Push: {e}")
        return jsonify({"error": "Failed to initiate STK Push."}), 400  # Return an error response
