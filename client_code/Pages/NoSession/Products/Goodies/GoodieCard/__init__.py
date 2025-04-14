from ._anvil_designer import GoodieCardTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..... import state

class GoodieCard(GoodieCardTemplate):
    def __init__(self, **properties):
      self.init_components(**properties)

    def form_show(self, **event_args):
      goodie = self.item
      img = self.item.get("image")
      if isinstance(img, Media) or isinstance(img, str):
        self.goodie_image.source = img
      else:
        self.goodie_image.source = "https://placehold.co/200x150?text=Image+manquante"
      self.goodie_name.text = goodie["name"]
      self.goodie_price.text = goodie["price"]
      self.goodie_description.text = goodie["description"]
      
    def button_add_click(self, **event_args):
      #state.add_to_cart(self.item)
      pass