import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime 

# This is a server package. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

@anvil.server.callable
def add_user(firstname, lastname, email, phone_number, username, password):
  now = datetime.now()
  app_tables.users.add_row(
    firstname=firstname,
    lastname=lastname,
    email=email,
    phone_number=phone_number,
    username=username,
    password=password,
    created_at=now,
    updated_at=now,
    is_admin=False
  )
  return "user added with success"