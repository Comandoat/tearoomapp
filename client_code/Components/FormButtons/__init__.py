from ._anvil_designer import FormButtonsTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class FormButtons(FormButtonsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # Lier un handler au clic du bouton reset INTERNE au template
    # Assurez-vous que le bouton dans le designer de FormButtons s'appelle 'reset_button'
    if hasattr(self, 'reset_button'):
        self.reset_button.add_event_handler('click', self.reset_button_click)

  def reset_button_click(self, **event_args):
    """Cette méthode est appelée quand le bouton reset interne est cliqué."""
    # Lève un événement personnalisé sur CETTE instance du composant FormButtons
    # Le formulaire parent pourra écouter cet événement.
    self.raise_event("x-reset-clicked")
    # Optionnel: Empêcher la propagation si d'autres composants imbriqués écoutent
    # event_args.stop_propagation()
