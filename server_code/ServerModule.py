import anvil.users
import anvil.server
import json
import csv
import base64
import requests
from datetime import datetime
import asyncio
import aiohttp
from anvil.tables import app_tables 

log_messages = []
progress = 0
update_result = ""
ki = ""

def append_to_log_message_queue(message):
    global log_messages
    log_messages.append(message)
    print(message) 

@anvil.server.callable
def process_csv_and_update(file):
    # Launch background task to process CSV
    anvil.server.launch_background_task('background_csv_processing', file)

@anvil.server.background_task
def background_csv_processing(file):
    global progress, update_result
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
                "estimatedArrivalDate": format_date(row["estimatedArrivalDate"]),
                "estimatedDeliveryDate": format_date(row["estimatedDeliveryDate"])
            }
            data.append(purchase_order)

        json_data = json.dumps({"purchase_orders": data}, indent=4)
        append_to_log_message_queue("CSV file processed successfully")
        
        # Call the asynchronous function for updating
        asyncio.run(update_purchase_orders(json_data))
      
        # Save the result and date to the database
        save_result_to_database(update_result)
      
        return update_result
      
    except Exception as e:
        error_message = f"Error processing CSV: {str(e)}"
        append_to_log_message_queue(error_message)
        return error_message

def save_result_to_database(result):
    # Save the result and the current date to the database
    app_tables.logs.add_row(
        result=result,
        date=datetime.now()
    )
    append_to_log_message_queue("Result saved to the database.")
  
def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        return date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        return date_str

async def update_purchase_orders(json_data):
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

    try:
        data = json.loads(json_data)
        total_records = len(data["purchase_orders"])

        append_to_log_message_queue(f"Sending bulk update for {total_records} records.")
        
        # Use aiohttp for asynchronous HTTP request
        async with aiohttp.ClientSession() as session:
            async with session.put(endpoint_url, headers=headers, json=data["purchase_orders"]) as response:
                response_text = await response.text()

                if response.status == 200:
                    update_result = f"Successfully updated {total_records} records."
                    append_to_log_message_queue(update_result)
                else:
                    update_result = f"Failed to update records. Response Code: {response.status}"
                    append_to_log_message_queue(update_result)
                
    except aiohttp.ClientError as err:
        append_to_log_message_queue(f"HTTP error occurred: {err}")
        update_result = "Error updating records. Check logs for more details."
    except Exception as err:
        append_to_log_message_queue(f"Other error occurred: {err}")
        update_result = "Error updating records. Check logs for more details."

    progress = 100
    append_to_log_message_queue("Progress updated to 100%")

    return update_result

@anvil.server.callable
def get_log_messages():
    global log_messages
    append_to_log_message_queue("get_log_messages called")
    return log_messages

@anvil.server.callable
def test(status):
    global ki  
    ki = status
  
@anvil.server.callable
def stat():
  return 'Success! Your file is being uploaded in the background'

@anvil.server.callable
def get_update_logs():
    # Fetch all rows from the UpdatesLog table
    logs = app_tables.logs.search()
    # Convert to a list of dictionaries for easy handling on the client side
    log_list = [{"result": log["result"], "date": log["date"].strftime('%Y-%m-%d %H:%M:%S')} for log in logs]
    return log_list