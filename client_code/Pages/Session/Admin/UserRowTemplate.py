from ._anvil_designer import UserRowTemplateTemplate
from anvil import *

class UserRowTemplate(UserRowTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  # --- Data Binding ---
  # Cette méthode est appelée par Anvil pour peupler la ligne
  # self.item contient le dictionnaire de données pour CETTE ligne 
  # (passé via user_grid.items dans AdminPanel)
  @property
  def item(self):
    return self._item

  @item.setter
  def item(self, value):
    self._item = value
    # Mettre à jour les labels avec les données de self.item
    self.email_label.text = self._item.get('email', 'N/A')
    self.firstname_label.text = self._item.get('firstname', '')
    self.lastname_label.text = self._item.get('lastname', '')
    self.username_label.text = self._item.get('username', 'N/A')
    # Afficher Oui/Non pour les booléens pour plus de clarté
    self.is_active_label.text = "Oui" if self._item.get('is_active', True) else "Non"
    self.is_admin_label.text = "Oui" if self._item.get('is_admin', False) else "Non"
    self.account_locked_label.text = "Oui" if self._item.get('account_locked', False) else "Non"
    # Note: Le row_id est dans self._item mais pas affiché ici

  # --- Event Handler ---
  def row_click(self, **event_args):
    """Cette méthode est appelée lorsque la ligne (son panel) est cliquée."""
    # Lève un événement personnalisé sur le formulaire parent (AdminPanel)
    # en passant les données de cette ligne (self.item)
    self.parent.raise_event('x-user-selected', item=self.item)
