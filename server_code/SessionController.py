import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .UsersController.crud import is_locked, verifier_mot_de_passe
from datetime import datetime
import functools # Ajout

# Nouveau décorateur
def admin_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_info = get_user_info() # Utilise la fonction existante pour récupérer l'ID
        if not user_info:
            raise anvil.server.PermissionDenied("Accès refusé: Utilisateur non connecté.")

        # Récupérer l'utilisateur par son Row ID stocké en session
        user = app_tables.users.get_by_id(user_info['user_row_id']) 
        if not user or not user['is_admin']:
            # Vous pouvez logguer la tentative d'accès si nécessaire
            print(f"Tentative d'accès admin non autorisée par l'utilisateur ID: {user_info.get('user_row_id', 'Inconnu')} Email: {user_info.get('user_email', 'Inconnu')}")
            raise anvil.server.PermissionDenied("Accès refusé: Privilèges administrateur requis.")

        # Si l'utilisateur est admin, exécute la fonction originale
        return func(*args, **kwargs)
    return wrapper

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
        # Utiliser user.get_id() pour obtenir l'identifiant unique de la ligne Anvil
        set_user_info(user['email'], user.get_id()) 
        return f"Bienvenue {user['firstname']} {user['lastname']}" # Ou retourner un objet utilisateur / succès
    except Exception as e:
        # L'erreur originale se produisait ici car user['id'] n'existe pas
        print(f"Erreur lors de la mise à jour de last_login ou de la session pour {email}: {e}")
        return "Erreur interne lors de la connexion."

@anvil.server.callable
def logout_user():
  """Efface les informations utilisateur spécifiques de la session serveur."""
  try:
    # Essayer de supprimer les clés spécifiques que nous avons définies
    if 'user_row_id' in anvil.server.session:
      del anvil.server.session['user_row_id']
    if 'user_email' in anvil.server.session:
      del anvil.server.session['user_email']
    print(f"Custom session keys cleared after logout.")
  except Exception as e:
    # En cas d'erreur lors de la suppression des clés (ne devrait pas arriver souvent)
    print(f"Error clearing custom session keys during logout: {e}")
    # Tentative de fallback pour effacer toute la session, même si cela peut échouer
    # Commentez/décommentez si nécessaire pour tester
    # try:
    #   anvil.server.session.clear()
    # except Exception as clear_err:
    #   print(f"Fallback session.clear() also failed: {clear_err}")
      
  # Note: Si vous utilisez également le service Users d'Anvil (anvil.users),
  # vous pourriez aussi appeler anvil.users.logout() ici.
  # anvil.users.logout()

@anvil.server.callable
def set_user_info(email, user_row_id):
    """Stocke l'email et le Row ID de l'utilisateur dans la session."""
    # Stocker l'identifiant unique de la ligne (Row ID)
    anvil.server.session['user_email'] = email
    anvil.server.session['user_row_id'] = user_row_id # Utiliser une clé différente
    # Modification du print pour éviter .items() et afficher les valeurs directement
    print(f"SESSION ITEMS SET: user_email='{anvil.server.session.get('user_email')}', user_row_id='{anvil.server.session.get('user_row_id')}'")

@anvil.server.callable
def get_user_info():
    """Récupère les informations utilisateur (email et Row ID) depuis la session."""
    try:
        # Essayer d'accéder directement aux clés
        user_row_id = anvil.server.session['user_row_id']
        user_email = anvil.server.session['user_email']
        # Vérifier si les valeurs sont valides (pas juste None ou vides si cela peut arriver)
        if user_row_id and user_email:
            return {"user_email": user_email, "user_row_id": user_row_id}
        else:
            # Si une clé existe mais est vide/None
            print("get_user_info: Session keys found but empty/None.")
            return None
    except KeyError:
        # Si une des clés ('user_row_id' ou 'user_email') n'existe pas dans la session
        print("get_user_info: Session keys not found (KeyError).")
        return None
    except Exception as e:
        # Attraper d'autres erreurs potentielles liées à l'accès session
        print(f"get_user_info: Unexpected error accessing session: {e}")
        # Ici, l'erreur originale était peut-être "get"
        return None
