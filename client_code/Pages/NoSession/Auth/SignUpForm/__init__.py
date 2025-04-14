from ._anvil_designer import SignUpFormTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server



class SignUpForm(SignUpFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.sign_up_form_buttons.submit_button.add_event_handler('click', self.submit_click)

  def submit_click(self):
    firstname = self.name_fields.firstname_field.text 
    lastname = self.name_fields.lastname_field.text
    email = self.credentials_fields.email_field.text
    password = self.credentials_fields.password_field.text
    confirmed_password = self.confirmed_password_field.text 

    if not firstname or not lastname or not email or not password or not confirmed_password:
      Notification("Every field must be filled", style="danger").show()
      return

    if password != confirmed_password:
      Notification("The passwords are not identical", style="danger").show()
      return  

    try:
      response = anvil.server.call('add_user', firstname, lastname, email, password)
      Notification(response, style="success").show()

      self.name_fields.firstname_field.text = ""
      self.name_fields.lastname_field.text = ""
      self.credentials_fields.email_field.text = ""
      self.credentials_fields.password_field.text = ""
      self.confirmed_password_field.text = ""

      get_open_form().load_page("login")

    except Exception as e:
      Notification(f"Error while communicating with the server: {e}", style="danger").show()
