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
    if hasattr(self, 'suggest_password_button'):
        self.suggest_password_button.add_event_handler('click', self.suggest_password_click)

  def submit_click(self, **event_args):
    firstname = self.name_fields.firstname_field.text 
    lastname = self.name_fields.lastname_field.text
    email = self.credentials_fields.email_field.text
    phone_number = self.phone_number.text
    username = self.username_field.text
    password = self.credentials_fields.password_field.text
    confirmed_password = self.confirmed_password_field.text 
    

    if not firstname or not lastname or not email or not password or not confirmed_password:
      Notification("Every field must be filled", style="danger").show()
      return

    if password != confirmed_password:
      Notification("The passwords are not identical", style="danger").show()
      return  

    self.sign_up_form_buttons.submit_button.enabled = False
    self.sign_up_form_buttons.submit_button.text = "Création en cours..."

    try:
      response = anvil.server.call('add_user', 
                                  firstname, 
                                  lastname, 
                                  email, 
                                  phone_number, 
                                  username, 
                                  password, 
                                  confirmed_password)
      
      if isinstance(response, str) and response.startswith("Erreur :"): 
        Notification(response, style="danger", title="Échec de l'inscription").show()
      elif response == "Compte créé avec succès ! Veuillez vérifier votre email.":
        Notification(response, style="success", title="Inscription réussie").show()
        self.name_fields.firstname_field.text = ""
        self.name_fields.lastname_field.text = ""
        self.credentials_fields.email_field.text = ""
        self.credentials_fields.password_field.text = ""
        self.confirmed_password_field.text = ""
        self.phone_number.text = ""
        self.username_field.text = ""
        get_open_form().load_page("login")
      else:
         Notification(f"Réponse inattendue du serveur: {response}", style="danger", title="Erreur Inattendue").show()

    except anvil.server.ExternalError as e:
        Notification(f"Erreur serveur: {e.message}", style="danger", title="Erreur Serveur").show()
    except Exception as e:
      Notification(f"Une erreur est survenue: {e}", style="danger", title="Erreur de Communication").show()
    finally:
       self.sign_up_form_buttons.submit_button.enabled = True
       self.sign_up_form_buttons.submit_button.text = "S'inscrire"

  def suggest_password_click(self, **event_args):
      try:
          suggested_password = anvil.server.call('suggest_password')
          self.credentials_fields.password_field.text = suggested_password
          self.confirmed_password_field.text = suggested_password
          Notification("Mot de passe suggéré inséré.", style="info", timeout=2).show()
      except Exception as e:
          Notification(f"Erreur lors de la suggestion: {e}", style="danger").show()
