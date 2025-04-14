import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
@anvil.server.callable
def get_cart(id):
  return app_tables.carts.get(user_id=id)

@anvil.server.callable
def create_cart(data):
  now = datatime.now()
  app_tables.carts.add_row(   
    content=data, 
    created_at=now, 
    update_at=now,
    total_amount=data["total_amount"]
  )
  