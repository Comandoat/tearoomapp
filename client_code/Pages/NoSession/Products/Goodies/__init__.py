from ._anvil_designer import GoodiesTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .GoodieCard import GoodieCard

class Goodies(GoodiesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    goodies = anvil.server.call('get_goodies')
    self.goodies_repeating_panel.item_template = GoodieCard
    goodies = anvil.server.call('get_goodies')
    
    if not anvil.server.is_app_online():
      self.goodies_repeating_panel.items = [
          {"name": "Pancake", "price": 2.50, "image": "https://images.pexels.com/photos/376464/pexels-photo-376464.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "description": "Pancakes of Mami Jaja"},
          {"name": "Crêpe", "price": 4.80, "image":"https://images.pexels.com/photos/2613471/pexels-photo-2613471.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "description": "French Crêopes By Laurent Pi"}
      ]
      return
    self.goodies_repeating_panel.items = goodies

    # Any code you write here will run before the form opens.
