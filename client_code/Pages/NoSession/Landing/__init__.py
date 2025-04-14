from ._anvil_designer import LandingTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .. import login_user
from ... import state
from anvil_extras import *

class Landing(LandingTemplate):

  def on_state_change(self):
    print(f"Utilisateur actuel : {state.get('user')}")

  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    state.register(self.on_state_change)
    self.on_state_change()
    self.display_teas()
    self.display_goodies()
 
  def display_goodies(self):
    try:
      goodies = anvil.server.call('get_goodies')
      for goodie in goodies:
        self.landing_goodies_carousel_flow_panel.add_component(Image(source=goodie['image']))
    except Exception as e:
      alert(f"Erreur lors du chargement des images : {e}")

    
  def display_teas(self):
    try:
      teas = anvil.server.call('get_teas')
      for tea in teas:
        self.landing_teas_carousel_flow_panel.add_component(Image(source=tea['image']))
    except Exception as e:
      alert(f"Erreur lors du chargement des images : {e}")
   

  
  def form_hide(self, **event_args):
      state.unregister(self.on_state_change)

  def button_sign_in_click(self, **event_args):
    get_open_form().load_page("login")

 
  def button_sign_up_click(self, **event_args):
    get_open_form().load_page("signup")

  def goodies_list_button_click(self, **event_args):
    get_open_form().load_page("goodies")
  
  def teas_list_button_click(self, **event_args):
    get_open_form().load_page("teas")
   