import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import json
import csv
import base64
import requests
from datetime import datetime
import time

# Global variables
log_messages = []
progress = 0
update_result = ""

def append_to_log_message_queue(message):
    global log_messages
    log_messages.append(message)
    print(message)

@anvil.server.callable
def process_csv_and_update(file):
    global progress
    progress = 0
    append_to_log_message_queue("process_csv_and_update called")
    try:
        csv_data = file.get_bytes().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(csv_data)
        data = []
        for row in csv_reader:
            purchase_order = {
                "id": int(row["id"]),
                "stage": row["stage"],
                "estimatedArrivalDate": row["estimatedArrivalDate"],
                "estimatedDeliveryDate": row["estimatedDeliveryDate"]
            }
            data.append(purchase_order)
        json_data = json.dumps(data, indent=4)
        append_to_log_message_queue("CSV file processed successfully")
        return update_purchase_orders(json_data)
    except Exception as e:
        append_to_log_message_queue(f"Error processing CSV: {str(e)}")
        return f"Error processing CSV: {str(e)}"

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%m/%d/%y')
        return date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        return date_str

def validate_data(data):
    required_keys = ["id", "stage", "estimatedArrivalDate", "estimatedDeliveryDate"]
    for item in data:
        if not all(key in item for key in required_keys):
            raise ValueError("Invalid data")

def validate_purchase_order(order):
    required_keys = ["id", "stage", "estimatedArrivalDate", "estimatedDeliveryDate"]
    if not all(key in order for key in required_keys):
        raise ValueError("Invalid purchase order data: missing required keys")
    # Add additional validation as needed

def validate_cin7_api_data(order):
    required_keys = ["id", "stage", "estimatedArrivalDate", "estimatedDeliveryDate"]
    if not all(key in order for key in required_keys):
        raise ValueError("Invalid Cin7 API data: missing required keys")
    # Add additional validation as needed


def update_purchase_orders(json_data):
    global progress, update_result
    append_to_log_message_queue("update_purchase_orders called")
    api_key = '4cc465afd3534370bbc4431e770346e1'
    username = 'SignalPowerDelivUS'
    endpoint_url = "https://api.cin7.com/api/v1/PurchaseOrders"
    credentials = base64.b64encode(f'{username}:{api_key}'.encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': 'Basic ' + credentials,
        'Content-Type': 'application/json'
    }

    data = json.loads(json_data)
    total_records = len(data["purchase_orders"])
    updated_records = 0

    for i, order_list in enumerate(data["purchase_orders"], start=1):
      order = order_list[0]
      append_to_log_message_queue(f"Updating record {i}/{total_records}: {json.dumps(order, indent=4)}")
        try:
            response = requests.post(endpoint_url, headers=headers, json=order)
            response.raise_for_status()

            if response.status_code == 200:
                updated_records += 1
                append_to_log_message_queue(f"Successfully updated record {order['id']}")
            else:
                append_to_log_message_queue(f"Failed to update record {order['id']}")
        except requests.exceptions.HTTPError as err:
            try:
                error_message = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            except ValueError:
                error_message = response.text
            append_to_log_message_queue(f"HTTP error occurred: {err}\n"
                                         f"Error updating record {order['id']}:\n"
                                         f"Response Code: {response.status_code}\n"
                                         f"Response Message: {json.dumps(error_message, indent=4)}\n"
                                         f"Request Payload: {json.dumps(order, indent=4)}")
        except Exception as err:
            append_to_log_message_queue(f"Other error occurred: {err}")

        progress = (i / total_records) * 100
        anvil.server.call('update_progress', progress)
        append_to_log_message_queue(f"Progress updated to {progress}%")

    progress = 100
    anvil.server.call('update_progress', progress)
    update_result = f"Successfully updated {updated_records}/{total_records} records."
    append_to_log_message_queue(update_result)
    return update_result

@anvil.server.callable

# def update_purchase_orders(json_data):
#     global progress, update_result
#     append_to_log_message_queue("update_purchase_orders called")

#     api_key = '4cc465afd3534370bbc4431e770346e1'
#     username = 'SignalPowerDelivUS'
#     endpoint_url = 'https://api.cin7.com/api/v1/PurchaseOrders/'
#     credentials = base64.b64encode(f'{username}:{api_key}'.encode('utf-8')).decode('utf-8')
#     headers = {
#         'Authorization': 'Basic ' + credentials,
#         'Content-Type': 'application/json'
#     }

#     try:
#         data = json.loads(json_data)
#         validate_data(data)
#         total_records = len(data)
#         updated_records = 0
#         for i, order in enumerate(data, start=1):
#             try:
#                 validate_cin7_api_data(order)
#                 order["estimatedArrivalDate"] = format_date(order["estimatedArrivalDate"])
#                 order["estimatedDeliveryDate"] = format_date(order["estimatedDeliveryDate"])
#                 append_to_log_message_queue(f"Updating record {i}/{total_records}: {json.dumps(order, indent=4)}")
#                 response = requests.put(f"{endpoint_url}{order['id']}", headers=headers, json=order)
#                 append_to_log_message_queue(f"Sending JSON data: {json.dumps(order, indent=4)}")
#                 append_to_log_message_queue(f"API response status code: {response.status_code}")
#                 append_to_log_message_queue(f"API response text: {response.text}")
#                 response.raise_for_status()
#                 updated_records += 1
#             except requests.exceptions.RequestException as err:
#                 append_to_log_message_queue(f"API request error: {err}")
#             except ValueError as err:
#                 append_to_log_message_queue(f"Invalid Cin7 API data: {err}")
#             except Exception as err:
#                 append_to_log_message_queue(f"Other error occurred: {err}")
#         progress = (i / total_records) * 100
#         anvil.server.call('update_progress', progress)
#         append_to_log_message_queue(f"Progress updated to {progress}%")
#         progress = 100
#         anvil.server.call('update_progress', progress)
#         update_result = f"Successfully updated {updated_records}/{total_records} records."
#         append_to_log_message_queue(update_result)
#         return update_result
#     except Exception as e:
#         append_to_log_message_queue(f"Error updating purchase orders: {str(e)}")
#         return f"Error updating purchase orders: {str(e)}"

# @anvil.server.callable
def update_progress(value):
    global progress
    progress = value
    append_to_log_message_queue(f"update_progress called with value: {value}")

@anvil.server.callable
def get_progress():
    global progress
    append_to_log_message_queue("get_progress called")
    return progress

@anvil.server.callable
def get_update_result():
    global update_result
    append_to_log_message_queue("get_update_result called")
    return update_result

@anvil.server.callable
def get_log_messages():
    global log_messages
    append_to_log_message_queue("get_log_messages called")
    return log_messages


