from ._anvil_designer import TaskItemTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class TaskItemTemplate(TaskItemTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    self.label_task_id.text = str(self.item['task_id'])
    self.label_status.text = self.item['status']
    self.label_progress.text = f"{self.item['progress']}%"
    
    # Any code you write here will run before the form opens.
