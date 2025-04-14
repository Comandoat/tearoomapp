from ._anvil_designer import CartTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


# CartForm.py
from anvil import *
from .... import state

class Cart(CartTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        #state.register(self.update_cart)
        #self.update_cart()
        self.cart = None

    def get_cart(self, user_id, data):
      try:
          self.cart = anvil.server.call('get_cart', user_id)
          print(self.cart)
          return self.cart
      except Exception as e:
        print(e)
        return "You have no cart"
   
          

    def update_cart(self, data):
        #items = state.get_cart()
        user_id = state.get("user")["id"]
        cart = None
        try:
          cart = anvil.server.call('get_cart', user_id)
          print(cart)
        except Exception as e:
          print(e)
          anvil.server.call('create_cart', data)
          return "Your cart has been updated successfully"
          pass
          

    def form_hide(self, **event_args):
      pass
      #state.unregister(self.update_cart)