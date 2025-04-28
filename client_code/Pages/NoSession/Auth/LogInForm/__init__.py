from ._anvil_designer import LogInFormTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
# Supprimer l'import de state s'il n'est pas utilisé ici
# from .... import state 

class LogInForm(LogInFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    # Lier l'événement click du bouton de connexion
    # Assurez-vous que 'login_button' est le bon nom du bouton dans le designer
    self.login_button.add_event_handler('click', self.login_button_click)
    # Optionnel: Mettre le focus sur le champ email au chargement
    # self.email_textbox.focus()

  # Supprimer les méthodes non utilisées liées à 'state' si non requises
  # def form_hide(self, **event_args):
  #   pass
  # def on_state_change(self):
  #   pass

  def login_button_click(self, **event_args):
    """Handles the click event of the login button."""
    # Assurez-vous que les noms 'email_textbox' et 'password_textbox' correspondent au designer
    email = self.email_textbox.text
    password = self.password_textbox.text

    if not email or not password:
        Notification("Veuillez saisir votre email et votre mot de passe.", title="Champs requis", style="warning").show()
        return

    # Indicateur de chargement
    self.login_button.enabled = False
    self.login_button.text = "Connexion..."
    self.login_button.icon = "fa:spinner"

    try:
        # Appel de la fonction serveur
        response = anvil.server.call('login_user', email, password)

        # Gérer la réponse
        if response.startswith("Bienvenue"):
            Notification(response, title="Succès", style="success").show()
            # La navigation vers la page de session doit être gérée ici
            # Cela peut impliquer d'ouvrir un nouveau formulaire principal pour la session
            # ou de recharger le formulaire actuel avec un état différent.
            # Exemple simple : recharger le formulaire principal (peut nécessiter une logique plus complexe)
            open_form('Client Code.MainForm') # Ou le nom de votre formulaire principal de session
        elif response == "Email ou mot de passe invalide.":
            Notification(response, title="Échec de la connexion", style="danger").show()
        elif response.startswith("Votre compte a été verrouillé"):
            Notification(response, title="Compte Verrouillé", style="danger").show()
        else:
            # Gérer d'autres erreurs potentielles retournées par le serveur
            Notification(f"Erreur inattendue: {response}", title="Erreur", style="danger").show()

    except anvil.server.InternalError as e:
        Notification(f"Une erreur interne est survenue côté serveur. Veuillez réessayer plus tard.", title="Erreur Serveur", style="danger").show()
        print(f"Server InternalError: {e}")
    except Exception as e:
        Notification(f"Erreur de communication avec le serveur: {e}", title="Erreur Réseau", style="danger").show()
        print(f"Communication Error: {e}")
    finally:
        # Réactiver le bouton
        self.login_button.enabled = True
        self.login_button.text = "Se connecter"
        self.login_button.icon = ""




