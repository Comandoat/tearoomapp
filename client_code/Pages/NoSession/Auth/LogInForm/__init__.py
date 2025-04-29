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
    # Utilisation des noms de composants spécifiques fournis
    if hasattr(self, 'form_buttons_1') and hasattr(self.form_buttons_1, 'submit_button'):
        self.form_buttons_1.submit_button.add_event_handler('click', self.login_button_click)
    # Ajouter un handler pour le reset_button si nécessaire
    # if hasattr(self, 'form_buttons_1') and hasattr(self.form_buttons_1, 'reset_button'):
    #     self.form_buttons_1.reset_button.add_event_handler('click', self.reset_button_click)

  def login_button_click(self, **event_args):
    """Handles the click of the login button."""
    # Utilisation des noms de composants spécifiques fournis
    # Assurez-vous que credentials_fields_1 contient bien email_field et password_field
    email = self.credentials_fields_1.email_field.text
    password = self.credentials_fields_1.password_field.text

    if not email or not password:
        Notification("Veuillez entrer l'email et le mot de passe.", style="warning", title="Champs requis").show()
        return

    # Disable button (le bouton est passé dans event_args)
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
             
    except anvil.server.InternalError as e:
        Notification(f"Erreur serveur: {e.message}", style="danger", title="Erreur Serveur").show()
    except anvil.server.PermissionDenied as e:
        Notification(f"Accès refusé: {e.message}", style="danger", title="Non autorisé").show()
    except Exception as e:
        Notification(f"Une erreur de communication est survenue: {e}", style="danger", title="Erreur").show()
    finally:
        # Re-enable button
        button.enabled = True
        button.text = "Se connecter" 

  # Ajoutez cette méthode si vous voulez implémenter le bouton reset
  # def reset_button_click(self, **event_args):
  #   """Handles the click of the reset button."""
  #   self.credentials_fields_1.email_field.text = ""
  #   self.credentials_fields_1.password_field.text = ""

  # Supprimez les fonctions on_state_change et form_hide si state n'est pas utilisé
  # def form_hide(self, **event_args):
  #   pass
  # def on_state_change(self):
  #   pass




