from ._anvil_designer import Form_MainTemplate
from anvil import *
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.media
import time

class Form_Main(Form_MainTemplate):
    def __init__(self, **properties):
        anvil.users.login_with_form()
        self.init_components(**properties)
        self.csv_file = None
        self.task_id = None  # To store the background task ID
        self.timer_1.interval = 1  # Polling interval of 1 second
        self.timer_1.enabled = False  # Timer is initially disabled
        self.seconds_counter = 0  # Counter to track the 30-second delay separately

    def file_loader_1_change(self, file, **event_args):
        self.csv_file = file
        self.txtProgress.text = ""
        self.rich_text_Log.content = ""
        self.txtProgress.text = "File uploaded successfully."
        self.rich_text_Log.content += "File uploaded successfully.\n"

    def start_process_click(self, **event_args):
        if self.csv_file:
            self.txtProgress.text = ""
            self.rich_text_Log.content = ""
          
            self.txtProgress.text = "Your file is being uploaded in the background. You can continue using the app, and we'll notify you once the upload is complete!"
            self.rich_text_Log.content += "Processing started\n"
            try:
                # Start the background task and get the task ID
                self.task_id = anvil.server.call('process_csv_and_update', self.csv_file)
                self.seconds_counter = 0  # Reset the counter
                self.timer_1.enabled = True  # Enable the timer to start polling for both task and delay
            except Exception as e:
                self.txtProgress.text = f"Error: {str(e)}"
                self.rich_text_Log.content += f"Error: {str(e)}\n"
        else:
            self.txtProgress.text = "" 
            self.rich_text_Log.content = "" 
            self.txtProgress.text = "Please upload a CSV file first."
            self.rich_text_Log.content += "Please upload a CSV file first.\n"

    def timer_1_tick(self, **event_args):
        """This method is called at intervals to check the task status and track the 30-second timer."""
        # Increment the counter and check if 30 seconds have passed
        self.seconds_counter += 1
        if self.seconds_counter == 30:
            # After 30 seconds, update the message to "SUCCESS UPLOADING"
            self.txtProgress.text = "SUCCESS UPLOADING"
            self.rich_text_Log.content += "SUCCESS UPLOADING\n"
            self.timer_1.enabled = False  # Disable the timer

        # Check the background task status
        if self.task_id:
            try:
                task = anvil.server.get_background_task(self.task_id)
                if task.is_completed():
                    result = task.get_return_value()
                    self.txtProgress.text = result
                    self.rich_text_Log.content += result + "\n"
                    self.timer_1.enabled = False  # Disable the timer when task is complete
                elif task.get_state() == 'failed':
                    result = f"Task failed: {task.get_return_value()}"
                    self.txtProgress.text = result
                    self.rich_text_Log.content += result + "\n"
                    self.timer_1.enabled = False  # Disable the timer on failure
                else:
                    # Task is still running, update progress or log
                    self.txtProgress.text = "Processing..."
                    self.rich_text_Log.content += "Task is still running...\n"
            except Exception as e:
                self.txtProgress.text = f"Error: {str(e)}"
                self.rich_text_Log.content += f"Error: {str(e)}\n"
                self.timer_1.enabled = False  # Disable the timer on error
