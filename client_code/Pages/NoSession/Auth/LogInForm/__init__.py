from ._anvil_designer import LogInFormTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .... import state

class LogInForm(LogInFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    #state.register(self.on_state_change)
    #self.on_state_change()
  def form_hide(self, **event_args):
    #state.unregister(self.on_state_change)  
    pass
  def on_state_change(self):
    #print(f"Utilisateur actuel : {state.get('user')}")
    pass




