from ._anvil_designer import TeaCardTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..... import state

class TeaCard(TeaCardTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

    def form_show(self, **event_args):
        tea = self.item
        print(">>> item reçu dans TeaCard :", self.item)

        self.tea_name.text = tea["name"]
        img = tea.get("image")
        if isinstance(img, Media) or isinstance(img, str):
            self.tea_image.source = img
        else:
          self.tea_image.source = "https://placehold.co/200x150?text=Image+manquante"

        self.tea_price.text = f"{tea['price']} €"
        self.tea_description.text = tea["description"] 

    def button_add_click(self, **event_args):
        state.add_to_cart(self.item)
