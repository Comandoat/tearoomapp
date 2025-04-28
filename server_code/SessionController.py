import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .UsersController.crud import is_locked, verifier_mot_de_passe
from datetime import datetime

@anvil.server.callable
def login_user(email, password):
    """Vérifie les identifiants de l'utilisateur et établit une session."""
    user = app_tables.users.get(email=email)
    
    # 1. Vérifier si l'utilisateur existe
    if user is None:
        # Message générique pour ne pas indiquer si l'email existe ou non
        return "Email ou mot de passe invalide."
    
    # 2. Vérifier si le compte est verrouillé
    if is_locked(email): # Utilise la fonction is_locked déjà présente
      return "Votre compte a été verrouillé. Veuillez contacter l'administrateur."

    # 3. Récupérer le hash du mot de passe stocké
    stored_password_hash = user['password']
    if not stored_password_hash: # Vérifier si un hash existe (sécurité additionnelle)
        print(f"Alerte: Aucun hash de mot de passe trouvé pour l'utilisateur {email}")
        return "Erreur lors de la connexion. Veuillez contacter le support."

    # 4. Vérifier le mot de passe fourni contre le hash stocké
    is_password_valid = verifier_mot_de_passe(stored_password_hash, password)
    
    if not is_password_valid:
        # Ici aussi, message générique
        # TODO: Implémenter un mécanisme de limitation de tentatives pour prévenir le brute-force
        return "Email ou mot de passe invalide."

    # 5. Connexion réussie : Mettre à jour last_login et définir la session
    try:
        user.update(last_login=datetime.now())
        set_user_info(user['email'], user['id']) # Utilise la fonction set_user_info existante
        return f"Bienvenue {user['firstname']} {user['lastname']}" # Ou retourner un objet utilisateur / succès
    except Exception as e:
        print(f"Erreur lors de la mise à jour de last_login ou de la session pour {email}: {e}")
        return "Erreur interne lors de la connexion."

@anvil.server.callable
def logout_user():
  anvil.server.session.clear()
  print(f"SESSION ITEMS AFTER LOGOUT: {anvil.server.session.items()}")

@anvil.server.callable
def set_user_info(email, user_id):
    # Stocker l'identifiant unique de l'utilisateur plutôt que l'email si possible
    # Assurez-vous que user['id'] existe et est unique (il est ajouté par Anvil par défaut)
    anvil.server.session['user_email'] = email
    anvil.server.session['user_id'] = user_id
    print(f"SESSION ITEMS SET: {anvil.server.session.items()}")

@anvil.server.callable
def get_user_info():
    # Récupérer l'id stocké dans la session
    user_id = anvil.server.session.get('user_id')
    if user_id:
        # On pourrait retourner plus d'infos sécurisées si besoin
        return {"user_email": anvil.server.session.get('user_email'), "user_id": user_id}
    return None # Ou {} pour indiquer aucune session active
