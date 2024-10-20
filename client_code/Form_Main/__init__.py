from ._anvil_designer import Form_MainTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.media

class Form_Main(Form_MainTemplate):
    def __init__(self, **properties):
        anvil.users.login_with_form()
        self.init_components(**properties)
        self.csv_file = None

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
          
            self.txtProgress.text = "Processing started"
            self.rich_text_Log.content += "Processing started\n"
            try:
                result = anvil.server.call('process_csv_and_update', self.csv_file)
                self.txtProgress.text = result
                self.rich_text_Log.content += result + "\n"  
            except Exception as e:
                self.txtProgress.text = f"Error: {str(e)}"
                self.rich_text_Log.content += f"Error: {str(e)}\n"
        else:
          
            self.txtProgress.text = "" 
            self.rich_text_Log.content = "" 
            self.txtProgress.text = "Please upload a CSV file first."
            self.rich_text_Log.content += "Please upload a CSV file first.\n"
