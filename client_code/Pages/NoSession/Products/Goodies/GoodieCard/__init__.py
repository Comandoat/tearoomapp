from ._anvil_designer import GoodieCardTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class GoodieCard(GoodieCardTemplate):
    def __init__(self, **properties):
      self.init_components(**properties)
      if hasattr(self, 'add_to_cart_button'):
          self.add_to_cart_button.add_event_handler('click', self.add_to_cart_button_click)
      else:
          print("AVERTISSEMENT (GoodieCard): Bouton 'add_to_cart_button' non trouvé.")

    def form_show(self, **event_args):
      goodie = self.item
      img = self.item.get("image")
      if isinstance(img, Media) or isinstance(img, str):
        self.goodie_image.source = img
      else:
        self.goodie_image.source = "https://placehold.co/200x150?text=Image+manquante"
      self.goodie_name.text = goodie["name"]
      self.goodie_price.text = goodie["price"]
      self.goodie_description.text = goodie["description"]
      
    def add_to_cart_button_click(self, **event_args):
      if not self.item:
          Notification("Données produit manquantes.", style="danger").show()
          return
          
      try:
          goodie_id = self.item.get_id()
          product_key = f"goodie:{goodie_id}"
          print(f"GoodieCard: Ajout de {product_key}")
          
          response = anvil.server.call('add_item_to_cart', product_key, 1)
          
          if isinstance(response, dict) and response.get("success"):
              Notification(response.get("message", "Article ajouté au panier !"), title="Succès", style="success", timeout=3).show()
              try: get_open_form().update_cart_indicator()
              except AttributeError: pass
          elif isinstance(response, dict) and response.get("error"):
               Notification(response.get("error"), title="Erreur Panier", style="danger").show()
          else:
               Notification("Réponse inattendue du serveur.", title="Erreur", style="warning").show()
               
      except AttributeError:
          try:
              goodie_id = self.item.get('id')
              if not goodie_id:
                  raise ValueError("Clé 'id' manquante ou vide dans self.item")
              product_key = f"goodie:{goodie_id}"
              response = anvil.server.call('add_item_to_cart', product_key, 1)
              if isinstance(response, dict) and response.get("success"):
                  Notification(response.get("message", "Article ajouté au panier !"), title="Succès", style="success", timeout=3).show()
                  try: get_open_form().update_cart_indicator()
                  except AttributeError: pass
              elif isinstance(response, dict) and response.get("error"):
                  Notification(response.get("error"), title="Erreur Panier", style="danger").show()
              else: Notification("Réponse inattendue du serveur.", title="Erreur", style="warning").show()
          except (AttributeError, ValueError, KeyError) as e:
               Notification("Impossible d'identifier le produit à ajouter.", title="Erreur Interne", style="danger").show()
               print(f"Erreur récupération ID goodie: {e}")
      except anvil.server.PermissionDenied as e:
          Notification(f"Erreur: {e.message}", title="Non Autorisé", style="danger").show()
      except anvil.server.InternalError as e:
          Notification(f"Erreur Serveur: {e.message}", title="Erreur Serveur", style="danger").show()
      except Exception as e:
          Notification(f"Une erreur s'est produite: {e}", title="Erreur", style="danger").show()