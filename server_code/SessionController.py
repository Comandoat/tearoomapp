import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from UsersController.crud import is_locked

@anvil.server.callable
def login_user(email, password):
    user = app_tables.users.get(email=email)
    if user is None:
        return "Invalid Data"
    if is_locked(email):
      return "Your accounted as been locked by an administrator"

    is_password_valid = password == user['password']
    if not is_password_valid:
        return "Invalid Data"

    set_user_info(user['email'], user["id"])
    return f"Welcome back {user['firstname']} {user['lastname']}"

@anvil.server.callable
def logout_user():
  anvil.server.session.clear()
  print(f"SESSION ITEMS: {anvil.server.session.items()}")

@anvil.server.callable
def set_user_info(email, id):
    anvil.server.session['user_email'] = email
    anvil.server.session['user_id'] = id
    print(f"SESSION ITEMS: {anvil.server.session.items()}")

@anvil.server.callable
def get_user_info():
    return {"user_email":anvil.server.session.get('user_email'), "user_id":anvil.server.session.get('id')}
