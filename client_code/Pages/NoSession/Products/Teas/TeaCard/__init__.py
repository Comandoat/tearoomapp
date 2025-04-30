from ._anvil_designer import TeaCardTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class TeaCard(TeaCardTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        if hasattr(self, 'add_to_cart_button'):
            self.add_to_cart_button.add_event_handler('click', self.add_to_cart_button_click)
        else:
            print("AVERTISSEMENT (TeaCard): Bouton 'add_to_cart_button' non trouvé.")

    def form_show(self, **event_args):
        tea = self.item
        print(">>> item reçu dans TeaCard :", self.item)

        self.tea_name.text = tea["name"]
        img = tea.get("image")
        if isinstance(img, Media) or isinstance(img, str):
            self.tea_image.source = img
        else:
          self.tea_image.source = "https://placehold.co/200x150?text=Image+manquante"

        self.tea_price.text = f"{tea['price']} €"
        self.tea_description.text = tea["description"] 

    def add_to_cart_button_click(self, **event_args):
        if not self.item:
            Notification("Données produit manquantes.", style="danger").show()
            return
            
        try:
            tea_id = self.item.get_id()
            product_key = f"tea:{tea_id}"
            print(f"TeaCard: Ajout de {product_key}")
            
            response = anvil.server.call('add_item_to_cart', product_key, 1)
            
            if isinstance(response, dict) and response.get("success"):
                Notification(response.get("message", "Thé ajouté au panier !"), title="Succès", style="success", timeout=3).show()
                try:
                    get_open_form().update_cart_indicator()
                except AttributeError:
                    print("TeaCard: Impossible de trouver update_cart_indicator sur le formulaire ouvert.")
            elif isinstance(response, dict) and response.get("error"):
                 Notification(response.get("error"), title="Erreur Panier", style="danger").show()
            else:
                 Notification("Réponse inattendue du serveur.", title="Erreur", style="warning").show()
                 
        except AttributeError:
            try:
                tea_id = self.item.get('id')
                if not tea_id:
                    raise ValueError("Clé 'id' manquante ou vide dans self.item")
                product_key = f"tea:{tea_id}"
                response = anvil.server.call('add_item_to_cart', product_key, 1)
                if isinstance(response, dict) and response.get("success"):
                    Notification(response.get("message", "Thé ajouté au panier !"), title="Succès", style="success", timeout=3).show()
                    try: get_open_form().update_cart_indicator()
                    except AttributeError: pass
                elif isinstance(response, dict) and response.get("error"):
                    Notification(response.get("error"), title="Erreur Panier", style="danger").show()
                else: Notification("Réponse inattendue du serveur.", title="Erreur", style="warning").show()
            except (AttributeError, ValueError, KeyError) as e:
                 Notification("Impossible d'identifier le produit à ajouter.", title="Erreur Interne", style="danger").show()
                 print(f"Erreur récupération ID thé: {e}")
        except anvil.server.PermissionDenied as e:
            Notification(f"Erreur: {e.message}", title="Non Autorisé", style="danger").show()
        except anvil.server.InternalError as e:
            Notification(f"Erreur Serveur: {e.message}", title="Erreur Serveur", style="danger").show()
        except Exception as e:
            Notification(f"Une erreur s'est produite: {e}", title="Erreur", style="danger").show()
