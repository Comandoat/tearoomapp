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
    self.suggest_password_button.add_event_handler('click', self.suggest_password_click)

  def submit_click(self, **event_args):
    firstname = self.name_fields.firstname_field.text 
    lastname = self.name_fields.lastname_field.text
    email = self.credentials_fields.email_field.text
    phone_number = self.phone_number.text
    username = self.username_field.text
    password = self.credentials_fields.password_field.text
    confirmed_password = self.confirmed_password_field.text 
    
    if not all([firstname, lastname, email, username, password, confirmed_password]):
      Notification("Tous les champs obligatoires doivent être remplis.", title="Erreur de formulaire", style="danger").show()
      return

    if password != confirmed_password:
      Notification("Les mots de passe saisis ne sont pas identiques.", title="Erreur", style="danger").show()
      return

    self.sign_up_form_buttons.submit_button.enabled = False
    self.sign_up_form_buttons.submit_button.icon = "fa:spinner"
    self.sign_up_form_buttons.submit_button.text = "Création..."

    try:
      response = anvil.server.call('add_user', 
                                   firstname=firstname, 
                                   lastname=lastname, 
                                   email=email, 
                                   phone_number=phone_number, 
                                   username=username, 
                                   password=password, 
                                   password_confirm=confirmed_password)
      
      if response.startswith("Compte créé avec succès"):
        Notification(response, title="Succès", style="success", timeout=5).show()
        self.name_fields.firstname_field.text = ""
        self.name_fields.lastname_field.text = ""
        self.credentials_fields.email_field.text = ""
        self.credentials_fields.password_field.text = ""
        self.confirmed_password_field.text = ""
        self.phone_number.text = ""
        self.username_field.text = ""
        get_open_form().load_page("login")
      else:
        Notification(response, title="Échec de l'inscription", style="danger", timeout=10).show()

    except anvil.server.InternalError as e:
        Notification(f"Une erreur interne est survenue côté serveur. Veuillez réessayer plus tard.", title="Erreur Serveur", style="danger").show()
        print(f"Server InternalError: {e}")
    except Exception as e:
      Notification(f"Erreur de communication avec le serveur: {e}", title="Erreur Réseau", style="danger").show()
      print(f"Communication Error: {e}")
    finally:
        self.sign_up_form_buttons.submit_button.enabled = True
        self.sign_up_form_buttons.submit_button.icon = ""
        self.sign_up_form_buttons.submit_button.text = "S'inscrire"

  def suggest_password_click(self, **event_args):
      self.suggest_password_button.enabled = False
      try:
          suggested_password = anvil.server.call('suggest_password')
          self.credentials_fields.password_field.text = suggested_password
          self.confirmed_password_field.text = suggested_password
          Notification("Un mot de passe fort a été suggéré et pré-rempli.", title="Suggestion", style="info", timeout=3).show()
      except Exception as e:
          Notification(f"Erreur lors de la suggestion du mot de passe: {e}", title="Erreur", style="danger").show()
          print(f"Suggest Password Error: {e}")
      finally:
          self.suggest_password_button.enabled = True
