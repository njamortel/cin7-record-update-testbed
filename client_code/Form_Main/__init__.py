from ._anvil_designer import Form_MainTemplate
from anvil import *
import anvil.server
import anvil.media
from anvil import server
from anvil.tables import app_tables

class Form_Main(Form_MainTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.repeating_panel_1.items = app_tables.logs.search()
        self.csv_file = None
        self.progress = 0
      
    def file_loader_1_change(self, file, **event_args):
        self.csv_file = file
        self.txtProgress.text = "File uploaded successfully."
      
    def start_process_click(self, **event_args):
        if self.csv_file:
            self.txtProgress.text = "Processing started"
            try:
                anvil.server.call('process_csv_and_update', self.csv_file)
                self.txtProgress.text = anvil.server.call('stat')
                self.file_loader_1.text = 'Upload'
                self.csv_file = None
               
            except Exception as e:
                self.txtProgress.text = f"Error: {str(e)}"
    
        else:
            self.txtProgress.text = "Please upload a CSV file first."

            
       

