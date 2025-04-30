from ._anvil_designer import ListClientsTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class ListClients(ListClientsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    # Enregistrer le gestionnaire d'événements personnalisé
    self.user_repeating_panel.set_event_handler('x_deactivate_user', self.handle_deactivate_user)
    # Charger les utilisateurs au démarrage
    self.load_users()

  def load_users(self):
    """Charge la liste des utilisateurs depuis le serveur."""
    try:
      # Utiliser anvil.server.call_s pour un chargement initial synchrone peut être ok,
      # mais async est préférable pour ne pas bloquer l'UI si la liste est longue.
      # users = anvil.server.call_s('admin_get_all_users')
      # self.user_repeating_panel.items = users
      
      # Version asynchrone
      def success_callback(users):
          self.user_repeating_panel.items = users
          print(f"{len(users)} utilisateurs chargés.")

      def failure_callback(err):
          print(f"Erreur lors du chargement des utilisateurs: {err}")
          Notification(f"Erreur de chargement: {err}", style="danger", timeout=5).show()
          self.user_repeating_panel.items = [] # Vider la liste en cas d'erreur
          
      anvil.server.call_s('admin_get_all_users',
                      success_callback=success_callback,
                      failure_callback=failure_callback)
                      
    except anvil.server.PermissionDenied as e:
        alert(f"Accès refusé: {e}")
        # Rediriger ou cacher le composant?
        open_form('Pages.NoSession.Landing') # Exemple: retour à l'accueil
    except Exception as e:
      print(f"Erreur inattendue dans load_users: {e}")
      Notification("Une erreur inattendue est survenue.", style="danger").show()
      self.user_repeating_panel.items = []

  def handle_deactivate_user(self, user_item, **event_args):
      """Gère l'événement pour désactiver/réactiver un utilisateur."""
      user_id = user_item.get('row_id')
      user_email = user_item.get('email', 'Inconnu')
      action_text = "réactivation" if not user_item.get('is_active', True) else "désactivation"
      
      if not user_id:
          Notification("Impossible d'identifier l'utilisateur.", style="warning").show()
          return
          
      print(f"Tentative de {action_text} pour l'utilisateur ID: {user_id}, Email: {user_email}")
      
      try:
          # Appel asynchrone pour ne pas bloquer
          def success_callback(result):
              print(f"Résultat serveur pour {action_text} de {user_email}: {result}")
              Notification(result, style="success").show()
              # Recharger la liste pour refléter le changement
              self.load_users()
              
          def failure_callback(err):
              print(f"Erreur serveur lors de la {action_text} de {user_email}: {err}")
              Notification(f"Erreur lors de la {action_text}: {err}", style="danger").show()
              # Recharger quand même pour voir si l'état a changé malgré l'erreur?
              self.load_users()
              
          anvil.server.call_s('admin_deactivate_user', user_id,
                           success_callback=success_callback,
                           failure_callback=failure_callback)
                           
      except anvil.server.PermissionDenied as e:
          alert(f"Action refusée: {e}")
          # Probablement pas nécessaire ici car l'appel initial à load_users aurait échoué
      except Exception as e:
          print(f"Erreur inattendue dans handle_deactivate_user: {e}")
          Notification(f"Erreur inattendue lors de la {action_text}.", style="danger").show()
          # Recharger pour être sûr de l'état actuel
          self.load_users()

  # Placeholder pour la gestion de l'édition (si le bouton est activé plus tard)
  # def handle_edit_user(self, user_item, **event_args):
  #   user_email = user_item.get('email', 'Inconnu')
  #   print(f"Événement x_edit_user reçu pour : {user_email}")
  #   # Ouvrir un formulaire de modification avec les détails de user_item
  #   # details = anvil.server.call('admin_get_user_details', user_item.get('row_id'))
  #   # if details:
  #   #    # Ouvrir un popup/formulaire avec les détails
  #   #    pass
