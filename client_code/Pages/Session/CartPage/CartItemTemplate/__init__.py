from ._anvil_designer import CartItemTemplateTemplate
from anvil import *
import anvil.server

class CartItemTemplate(CartItemTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Lier les événements des composants internes
    self.quantity_box.add_event_handler('change', self.quantity_box_change)
    self.remove_button.add_event_handler('click', self.remove_button_click)

  # --- Data Binding --- 
  @property
  def item(self):
    # self.item contient le dictionnaire pour cette ligne, 
    # envoyé par CartPage via cart_items_panel.items
    return self._item

  @item.setter
  def item(self, value):
    self._item = value
    # Mettre à jour les composants visuels avec les données de l'item
    self.item_name_label.text = self._item.get('name', 'Produit Inconnu')
    # Afficher le prix unitaire formaté
    self.item_price_label.text = f"{self._item.get('price', 0.0):.2f} €"
    # Afficher la quantité
    self.quantity_box.text = self._item.get('quantity', 1)
    # Afficher le total de ligne
    self.line_total_label.text = f"{self._item.get('line_total', 0.0):.2f} €"
    # Afficher l'image
    image_media = self._item.get('image')
    if image_media:
        self.item_image.source = image_media
    else:
        # Mettre une image par défaut si nécessaire
        self.item_image.source = "_/theme/logo-tearoom-simple-logo.png" 

  # --- Event Handlers --- 
  def quantity_box_change(self, **event_args):
    """Appelé quand la quantité dans la NumberBox change."""
    try:
        new_quantity = int(self.quantity_box.text)
        product_key = self.item.get('product_key')
        
        if not product_key:
            print("Erreur CartItemTemplate: product_key manquant dans self.item")
            return

        if new_quantity == self.item.get('quantity'):
             return # Pas de changement réel

        print(f"CartItemTemplate: Quantité changée pour {product_key} -> {new_quantity}")
        # Lève un événement pour que CartPage gère la mise à jour serveur et UI globale
        self.parent.raise_event('x-quantity-changed', item_key=product_key, new_quantity=new_quantity)
        
    except (ValueError, TypeError):
        # Remettre l'ancienne valeur si l'entrée n'est pas un entier valide
        Notification("Veuillez entrer un nombre entier pour la quantité.", title="Quantité invalide", style="warning", timeout=3).show()
        self.quantity_box.text = self.item.get('quantity', 1)
    except Exception as e:
         Notification(f"Erreur lors de la modification de la quantité: {e}", title="Erreur", style="danger").show()
         # Remettre l'ancienne valeur en cas d'autre erreur
         self.quantity_box.text = self.item.get('quantity', 1)

  def remove_button_click(self, **event_args):
    """Appelé quand le bouton supprimer est cliqué."""
    product_key = self.item.get('product_key')
    if not product_key:
        print("Erreur CartItemTemplate: product_key manquant dans self.item pour suppression")
        return
        
    print(f"CartItemTemplate: Demande de suppression pour {product_key}")
    # Lève un événement pour que CartPage gère la suppression serveur et UI globale
    self.parent.raise_event('x-remove-item', item_key=product_key) 