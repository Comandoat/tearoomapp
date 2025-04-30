from ._anvil_designer import CartPageTemplate
from anvil import *
import anvil.server
# Importer le template de ligne
from .CartItemTemplate import CartItemTemplate

class CartPage(CartPageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Assigner le template au RepeatingPanel
    self.cart_items_panel.item_template = CartItemTemplate
    
    # Lier les événements des boutons globaux
    self.clear_cart_button.add_event_handler('click', self.clear_cart_button_click)
    self.checkout_button.add_event_handler('click', self.checkout_button_click)
    
    # Lier les événements personnalisés venant des lignes (CartItemTemplate)
    self.cart_items_panel.set_event_handler('x-quantity-changed', self.handle_quantity_change)
    self.cart_items_panel.set_event_handler('x-remove-item', self.handle_remove_item)
    
    # Charger les données initiales du panier
    self.refresh_cart()

  def refresh_cart(self):
    """Recharge et affiche les données complètes du panier."""
    print("CartPage: Refreshing cart data...")
    try:
        cart_data = anvil.server.call('get_cart_details')
        # Mettre à jour la liste des articles dans le RepeatingPanel
        self.cart_items_panel.items = cart_data.get('items', [])
        # Mettre à jour le total
        self.update_total_label(cart_data.get('total_amount', 0.0))
        # Mettre à jour l'indicateur global
        self.update_main_indicator()
    except Exception as e:
        Notification(f"Erreur lors du chargement du panier: {e}", title="Erreur", style="danger").show()

  def update_total_label(self, total_amount):
    """Met à jour le label du montant total."""
    self.total_label.text = f"Total : {total_amount:.2f} €"

  def update_main_indicator(self):
    """Tente de mettre à jour l'indicateur panier dans MainForm."""
    try:
        get_open_form().update_cart_indicator()
    except AttributeError:
        print("CartPage: Impossible de trouver update_cart_indicator sur le formulaire ouvert.")

  # --- Handlers pour les événements des lignes --- 
  def handle_quantity_change(self, item_key, new_quantity, **event_args):
    """Gère la demande de changement de quantité venant d'une ligne."""
    print(f"CartPage: Handling quantity change for {item_key} to {new_quantity}")
    try:
        response = anvil.server.call('update_cart_item_quantity', item_key, new_quantity)
        if isinstance(response, dict) and response.get("success"):
            Notification(response.get("message", "Quantité mise à jour."), style="success", timeout=2).show()
            # Mettre à jour le total et l'indicateur
            self.update_total_label(response.get("new_total", 0.0))
            self.update_main_indicator()
            # Recharger toute la grille pour refléter le changement de total ligne (ou maj manuelle)
            # Option 1: Recharger tout (plus simple)
            self.refresh_cart() 
            # Option 2: Mettre à jour l'item spécifique dans self.cart_items_panel.items (plus complexe)
        elif isinstance(response, dict) and response.get("error"):
            Notification(response.get("error"), title="Erreur Serveur", style="danger").show()
            # Recharger pour potentiellement corriger l'affichage
            self.refresh_cart()
        else:
            Notification("Réponse inattendue du serveur.", title="Erreur", style="warning").show()
    except Exception as e:
         Notification(f"Erreur lors de la mise à jour de la quantité: {e}", title="Erreur", style="danger").show()
         # Recharger en cas d'erreur
         self.refresh_cart()

  def handle_remove_item(self, item_key, **event_args):
    """Gère la demande de suppression d'article venant d'une ligne."""
    print(f"CartPage: Handling item removal for {item_key}")
    try:
        response = anvil.server.call('remove_item_from_cart', item_key)
        if isinstance(response, dict) and response.get("success"):
            Notification(response.get("message", "Article supprimé."), style="success", timeout=2).show()
            # Mettre à jour le total et l'indicateur
            self.update_total_label(response.get("new_total", 0.0))
            self.update_main_indicator()
            # Recharger la liste des items
            self.refresh_cart() 
        elif isinstance(response, dict) and response.get("error"):
            Notification(response.get("error"), title="Erreur Serveur", style="danger").show()
        else:
            Notification("Réponse inattendue du serveur.", title="Erreur", style="warning").show()
    except Exception as e:
         Notification(f"Erreur lors de la suppression de l'article: {e}", title="Erreur", style="danger").show()

  # --- Handlers pour les boutons globaux --- 
  def clear_cart_button_click(self, **event_args):
    """Vide complètement le panier."""
    if confirm("Êtes-vous sûr de vouloir vider votre panier ?"): 
        try:
            response = anvil.server.call('clear_cart')
            if isinstance(response, dict) and response.get("success"):
                Notification(response.get("message", "Panier vidé."), style="success").show()
                self.refresh_cart() # Recharge pour afficher le panier vide
            elif isinstance(response, dict) and response.get("error"):
                 Notification(response.get("error"), title="Erreur Serveur", style="danger").show()
            else:
                 Notification("Réponse inattendue.", title="Erreur", style="warning").show()
        except Exception as e:
              Notification(f"Erreur lors du vidage du panier: {e}", title="Erreur", style="danger").show()

  def checkout_button_click(self, **event_args):
    """Action déclenchée lors du clic sur le bouton 'Passer la commande'."""
    # Vérifier si le panier est vide
    if not self.cart_items_panel.items:
        Notification("Votre panier est vide.", title="Panier Vide", style="info").show()
        return

    # Placeholder pour la future logique de paiement/confirmation
    # TODO: Intégrer la logique de paiement réelle ici
    Notification("La fonction de paiement n'est pas encore implémentée.", title="Fonctionnalité à venir", style="info", timeout=5).show()
    
    # Optionnel: Naviguer vers une page de confirmation ou de paiement si elle existe
    # print("Redirection vers la page de paiement...")
    # open_form('PaymentForm') # Exemple 