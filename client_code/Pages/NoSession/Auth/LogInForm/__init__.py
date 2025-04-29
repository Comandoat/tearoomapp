from ._anvil_designer import LogInFormTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
# Supprimez l'import de state s'il n'est pas utilisé
# from .... import state 

class LogInForm(LogInFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    # Assumons que les champs email/password sont dans self.credentials_fields
    # et le bouton de soumission dans self.log_in_form_buttons
    # Adaptez ces noms si nécessaire selon votre designer Anvil
    if hasattr(self, 'log_in_form_buttons') and hasattr(self.log_in_form_buttons, 'submit_button'):
        self.log_in_form_buttons.submit_button.add_event_handler('click', self.login_button_click)
    
    # Si les champs sont directement sur le formulaire:
    # if hasattr(self, 'login_button'): 
    #    self.login_button.add_event_handler('click', self.login_button_click)

  def login_button_click(self, **event_args):
    """Handles the click of the login button."""
    # Assurez-vous que ces noms de composants correspondent à votre designer
    email = self.credentials_fields.email_field.text
    password = self.credentials_fields.password_field.text

    if not email or not password:
        Notification("Veuillez entrer l'email et le mot de passe.", style="warning", title="Champs requis").show()
        return

    # Disable button
    button = event_args['sender']
    button.enabled = False
    button.text = "Connexion..."

    try:
        response = anvil.server.call('login_user', email, password)

        if isinstance(response, str) and response.startswith("Bienvenue"):
            Notification(response, style="success", title="Connexion réussie").show()
            # Recharger le formulaire principal pour refléter l'état connecté
            open_form('MainForm') 
        elif isinstance(response, str) and (response == "Email ou mot de passe invalide." or response.startswith("Votre compte a été verrouillé.")):
            Notification(response, style="danger", title="Échec de la connexion").show()
        else:
             Notification(f"Réponse inattendue du serveur: {response}", style="danger", title="Erreur Inattendue").show()
             
    except anvil.server.ExternalError as e:
        Notification(f"Erreur serveur: {e.message}", style="danger", title="Erreur Serveur").show()
    except Exception as e:
        Notification(f"Une erreur est survenue: {e}", style="danger", title="Erreur de Communication").show()
    finally:
        # Re-enable button
        button.enabled = True
        button.text = "Se connecter"

  # Supprimez les fonctions on_state_change et form_hide si state n'est pas utilisé
  # def form_hide(self, **event_args):
  #   pass
  # def on_state_change(self):
  #   pass




