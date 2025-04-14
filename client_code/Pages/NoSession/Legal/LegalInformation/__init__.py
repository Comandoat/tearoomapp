from ._anvil_designer import LegalInformationTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class LegalInformation(LegalInformationTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def back_home_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    get_open_form().load_page("landing")

