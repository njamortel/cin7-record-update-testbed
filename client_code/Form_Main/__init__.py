from ._anvil_designer import Form_MainTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.media

class Form_Main(Form_MainTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.csv_file = None
        self.timer_1.interval = 1  # Set the timer interval to 1 second
        self.log_displayed = []  # To track which log messages have already been displayed

    def file_loader_1_change(self, file, **event_args):
        self.csv_file = file
        self.txtProgress.text = "File uploaded successfully."
        self.rich_text_Log.content += "File uploaded successfully.\n"

    def start_process_click(self, **event_args):
        if self.csv_file:
            self.txtProgress.text = "Processing started"
            self.rich_text_Log.content += "Processing started\n"
            try:
                # Call the server function and enable the timer to fetch logs
                anvil.server.call('process_csv_and_update', self.csv_file)
                self.timer_1.enabled = True  # Start the timer to track progress and logs
            except Exception as e:
                self.txtProgress.text = f"Error: {str(e)}"
                self.rich_text_Log.content += f"Error: {str(e)}\n"
        else:
            self.txtProgress.text = "Please upload a CSV file first."
            self.rich_text_Log.content += "Please upload a CSV file first.\n"

    def timer_1_tick(self, **event_args):
        try:
            # Fetch and display new log messages
            log_messages = anvil.server.call('get_log_messages')
            for message in log_messages:
                if message not in self.log_displayed:
                    self.rich_text_Log.content += message + '\n'
                    self.log_displayed.append(message)

            # Stop the timer if we detect "Processing finished" or logs contain the completion message
            if any("Processing finished" in message for message in log_messages):
                self.timer_1.enabled = False
                self.txtProgress.text = "Processing complete"
        except Exception as e:
            self.txtProgress.text = f"Error: {str(e)}"
            self.rich_text_Log.content += f"Error: {str(e)}\n"
            self.timer_1.enabled = False
