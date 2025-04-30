import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
# Import pour récupérer les infos utilisateur (assurez-vous que ce chemin est correct)
# Si SessionController est au même niveau que CartController:
from .SessionController import get_user_info
# Si SessionController est dans un autre dossier, ajustez le chemin

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
@anvil.server.callable
def get_cart(id):
  return app_tables.carts.get(user_id=id)

@anvil.server.callable
def create_cart(data):
  now = datatime.now()
  app_tables.carts.add_row(   
    content=data, 
    created_at=now, 
    update_at=now,
    total_amount=data["total_amount"]
  )
  
# --- Fonctions Helper (Internes au serveur) ---

def _get_user_cart(user_row_id):
    """Récupère ou crée le panier pour un utilisateur donné."""
    if not user_row_id:
        return None # Ne devrait pas arriver si appelé après vérification
        
    cart = app_tables.carts.get(user_id=str(user_row_id)) # Stocker le row_id comme string?
    
    if not cart:
        # Créer un nouveau panier si aucun n'existe
        now = datetime.now()
        print(f"Creating new cart for user_id: {user_row_id}")
        cart = app_tables.carts.add_row(
            user_id=str(user_row_id),
            content={},
            total_amount=0.0,
            created_at=now,
            update_at=now # Utiliser update_at et non update_at
        )
    return cart

def _get_product_price(product_key):
    """Récupère le prix d'un produit basé sur sa clé (ex: 'tea:id' ou 'goodie:id')."""
    try:
        product_type, product_id = product_key.split(':', 1)
        
        if product_type == 'tea':
            product = app_tables.teas.get_by_id(product_id)
        elif product_type == 'goodie':
            product = app_tables.goodies.get_by_id(product_id)
        else:
            print(f"_get_product_price: Unknown product type in key '{product_key}'")
            return None
            
        if product and product['is_available']:
            return product['price']
        else:
            print(f"_get_product_price: Product not found or not available for key '{product_key}'")
            return None
            
    except Exception as e:
        print(f"Error in _get_product_price for key '{product_key}': {e}")
        return None

def _calculate_cart_total(cart_content):
    """Calcule le montant total du panier basé sur son contenu."""
    total = 0.0
    if not isinstance(cart_content, dict):
         print("Warning: cart_content is not a dict in _calculate_cart_total")
         return total
         
    for product_key, quantity in cart_content.items():
        price = _get_product_price(product_key)
        if price is not None:
             # Assurer que quantity est un nombre
             try: 
                 item_quantity = int(quantity)
                 if item_quantity > 0:
                     total += price * item_quantity
             except (ValueError, TypeError):
                 print(f"Warning: Invalid quantity '{quantity}' for product '{product_key}' in cart.")
        else:
            # Si un produit n'est plus dispo/trouvé mais est dans le panier, on l'ignore pour le total?
            # Ou on pourrait le supprimer du panier ici.
            print(f"Warning: Product '{product_key}' not found or unavailable during total calculation.")
            pass 
            
    return round(total, 2) # Arrondir à 2 décimales

# --- Fonctions Callable (Appelables par le client) ---

@anvil.server.callable
def get_cart_data():
    """Retourne le contenu et le total du panier de l'utilisateur connecté."""
    user_info = get_user_info()
    if not user_info or not user_info.get('user_row_id'):
        # Gérer comme un panier vide si non connecté (ou lever une erreur)
        return {'content': {}, 'total_amount': 0.0}
        # Ou: raise anvil.server.PermissionDenied("Vous devez être connecté pour voir votre panier.")
        
    user_row_id = user_info['user_row_id']
    cart = _get_user_cart(user_row_id)
    
    if cart:
        # Recalculer au cas où les prix auraient changé / synchro BDD
        current_content = cart['content'] if isinstance(cart['content'], dict) else {}
        calculated_total = _calculate_cart_total(current_content)
        # Mettre à jour le total en BDD si différent (optionnel mais propre)
        if cart['total_amount'] != calculated_total:
            print(f"Updating cart total for user {user_row_id} from {cart['total_amount']} to {calculated_total}")
            cart.update(total_amount=calculated_total, update_at=datetime.now())
            
        return {'content': current_content, 'total_amount': calculated_total}
    else:
        # Ne devrait pas arriver si _get_user_cart fonctionne
        return {'content': {}, 'total_amount': 0.0}

@anvil.server.callable
def add_item_to_cart(product_key, quantity=1):
    """Ajoute un article (ou augmente sa quantité) au panier."""
    user_info = get_user_info()
    if not user_info or not user_info.get('user_row_id'):
        return {"error": "Vous devez être connecté pour ajouter au panier."}
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return {"error": "La quantité doit être positive."}
    except (ValueError, TypeError):
        return {"error": "Quantité invalide."}

    # Vérifier si le produit existe et est dispo AVANT de récupérer/créer le panier
    price = _get_product_price(product_key)
    if price is None:
        return {"error": "Produit non trouvé ou indisponible."}

    user_row_id = user_info['user_row_id']
    cart = _get_user_cart(user_row_id)
    if not cart:
         return {"error": "Impossible de récupérer ou créer le panier."}

    # Mettre à jour le contenu
    current_content = cart['content'] if isinstance(cart['content'], dict) else {}
    current_quantity = current_content.get(product_key, 0)
    new_quantity = current_quantity + quantity
    current_content[product_key] = new_quantity
    
    # Recalculer et mettre à jour
    new_total = _calculate_cart_total(current_content)
    cart.update(content=current_content, total_amount=new_total, update_at=datetime.now())
    
    # Retourner succès avec éventuellement le nouveau total ou nb items
    return {"success": True, "message": "Article ajouté au panier.", "new_total": new_total}

@anvil.server.callable
def update_cart_item_quantity(product_key, new_quantity):
    """Met à jour la quantité d'un article dans le panier."""
    user_info = get_user_info()
    if not user_info or not user_info.get('user_row_id'):
        return {"error": "Vous devez être connecté."}
        
    try:
        new_quantity = int(new_quantity)
    except (ValueError, TypeError):
        return {"error": "Quantité invalide."}

    user_row_id = user_info['user_row_id']
    cart = _get_user_cart(user_row_id)
    if not cart:
         return {"error": "Panier non trouvé."}
         
    current_content = cart['content'] if isinstance(cart['content'], dict) else {}
    if product_key not in current_content:
        return {"error": "Article non trouvé dans le panier."}
        
    if new_quantity <= 0:
        # Si quantité <= 0, on supprime l'article
        del current_content[product_key]
        message = "Article supprimé du panier."
    else:
        current_content[product_key] = new_quantity
        message = "Quantité mise à jour."
        
    # Recalculer et mettre à jour
    new_total = _calculate_cart_total(current_content)
    cart.update(content=current_content, total_amount=new_total, update_at=datetime.now())
    
    return {"success": True, "message": message, "new_total": new_total}

@anvil.server.callable
def remove_item_from_cart(product_key):
    """Supprime un article spécifique du panier."""
    user_info = get_user_info()
    if not user_info or not user_info.get('user_row_id'):
        return {"error": "Vous devez être connecté."}

    user_row_id = user_info['user_row_id']
    cart = _get_user_cart(user_row_id)
    if not cart:
         return {"error": "Panier non trouvé."}
         
    current_content = cart['content'] if isinstance(cart['content'], dict) else {}
    if product_key not in current_content:
        return {"error": "Article non trouvé dans le panier."}
        
    del current_content[product_key]
    
    # Recalculer et mettre à jour
    new_total = _calculate_cart_total(current_content)
    cart.update(content=current_content, total_amount=new_total, update_at=datetime.now())
    
    return {"success": True, "message": "Article supprimé.", "new_total": new_total}
    
@anvil.server.callable
def clear_cart():
    """Vide complètement le panier de l'utilisateur connecté."""
    user_info = get_user_info()
    if not user_info or not user_info.get('user_row_id'):
        return {"error": "Vous devez être connecté."}

    user_row_id = user_info['user_row_id']
    cart = _get_user_cart(user_row_id)
    if not cart:
         # Pas d'erreur si le panier n'existait pas
         return {"success": True, "message": "Panier déjà vide.", "new_total": 0.0}
         
    # Vider le contenu et mettre à jour
    cart.update(content={}, total_amount=0.0, update_at=datetime.now())
    
    return {"success": True, "message": "Panier vidé.", "new_total": 0.0}

@anvil.server.callable
def get_cart_item_count():
    """Retourne le nombre total d'articles dans le panier (somme des quantités)."""
    user_info = get_user_info()
    if not user_info or not user_info.get('user_row_id'):
        return 0
        
    user_row_id = user_info['user_row_id']
    cart = _get_user_cart(user_row_id)
    count = 0
    if cart and isinstance(cart['content'], dict):
        for quantity in cart['content'].values():
             try:
                 count += int(quantity)
             except (ValueError, TypeError): pass # Ignorer quantités invalides
    return count
  