from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server

class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # L'affichage est géré par les liaisons de données ou mis à jour quand self.item change.
    # Cependant, on peut appeler update_display pour initialiser si pas de liaisons directes
    self.update_display()

  def update_display(self):
    """Met à jour les labels et boutons en fonction de self.item."""
    if self.item:
      self.email_label.text = self.item.get('email', 'N/A')
      self.name_label.text = f"{self.item.get('firstname', '')} {self.item.get('lastname', '')}".strip()
      
      # Statut combiné
      status_parts = []
      is_active = self.item.get('is_active', True)
      is_admin = self.item.get('is_admin', False)
      is_locked = self.item.get('account_locked', False)
      
      if is_admin:
        status_parts.append("Admin")
      if is_locked:
        status_parts.append("Verrouillé")
      if not is_active:
        status_parts.append("Désactivé")
      elif not status_parts: # Si ni admin, ni verrouillé, ni désactivé
        status_parts.append("Actif")
        
      self.status_label.text = ", ".join(status_parts)

      # Mettre à jour le bouton Activer/Désactiver
      if not is_active:
          self.activate_button.text = "Réactiver"
          self.activate_button.role = "secondary" # Ou un autre style
      else:
          self.activate_button.text = "Désactiver"
          self.activate_button.role = "" # Style par défaut
          
      # On pourrait désactiver le bouton pour l'admin actuel s'il est affiché
      # current_user = anvil.users.get_user() # Attention: N'utilise pas le service Users ici
      # if current_user and self.item.get('email') == current_user['email']:
      #    self.activate_button.enabled = False
      #    self.edit_button.enabled = False # On ne modifie pas soi-même ici


  def activate_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    action = "Réactiver" if not self.item.get('is_active', True) else "Désactiver"
    user_email = self.item.get('email', 'Inconnu')
    
    # Ne pas permettre à un admin de se désactiver lui-même via ce bouton
    try:
      # Appel synchrone car on a besoin de la réponse pour la confirmation
      current_user_info = anvil.server.call_s('get_user_info') 
      if current_user_info and current_user_info.get('user_email') == user_email:
        alert("Vous ne pouvez pas désactiver votre propre compte depuis cette interface.")
        return
    except Exception as e:
        print(f"Erreur lors de la vérification de l'utilisateur actuel: {e}")
        # Continuer prudemment ou arrêter?

    if confirm(f"Êtes-vous sûr de vouloir {action.lower()} l'utilisateur {user_email}?"):
        try:
            # Utiliser raise_event_async pour ne pas bloquer l'UI pendant l'appel serveur
            self.parent.raise_event_async("x_deactivate_user", user_item=self.item)
        except Exception as e:
            # Gérer l'erreur si raise_event échoue (rare)
            print(f"Erreur lors du déclenchement de x_deactivate_user: {e}")
            anvil.Notification(f"Erreur lors de la tentative de {action.lower()}.").show()

  def edit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Pour l'instant, ce bouton est désactivé dans le template
    # Plus tard, il pourrait ouvrir un formulaire de modification
    # self.parent.raise_event("x_edit_user", user_item=self.item)
    anvil.Notification("La fonction de modification sera bientôt disponible.").show()
    pass

components:
- name: email_label
  properties: {}
  type: Label
  layout_properties: {column: A}
- name: name_label
  properties: {}
  type: Label
  layout_properties: {column: B}
- name: status_label
  properties: {align: right}
  type: Label
  layout_properties: {column: C}
- name: activate_button
  properties: {text: Activer/Désactiver}
  type: Button
  layout_properties: {column: D}
- name: edit_button
  properties: {text: Modifier, enabled: false} # Désactivé pour l'instant
  type: Button
  layout_properties: {column: E}
container: {type: DataRowPanel} 