from ._anvil_designer import TeasTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .TeaCard import TeaCard

class Teas(TeasTemplate):
   def __init__(self, **properties):
      self.init_components(**properties)
      self.teas_repeating_panel.item_template = TeaCard

      teas = anvil.server.call('get_teas')
      self.teas_repeating_panel.items = teas

    # Any code you write here will run before the form opens.
