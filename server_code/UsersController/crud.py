import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime 
import re
import math
from collections import Counter
from zxcvbn import zxcvbn
from argon2 import PasswordHasher, exceptions as argon_exceptions
import secrets
import string


# This is a server package. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

# --- Fonctions de validation et sécurité du mot de passe ---

ENTROPIE_MINIMALE_BITS = 50  # Recommandé : entre 50 et 60 bits minimum

def entropie(mot_de_passe):
    """Calcule une estimation d'entropie en fonction de l'alphabet utilisé."""
    alphabet_size = 0
    if re.search(r'[a-z]', mot_de_passe):
        alphabet_size += 26
    if re.search(r'[A-Z]', mot_de_passe):
        alphabet_size += 26
    if re.search(r'[0-9]', mot_de_passe):
        alphabet_size += 10
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', mot_de_passe):
        alphabet_size += len('!@#$%^&*(),.?":{}|<>')

    if alphabet_size == 0:
        return 0  # Aucun caractère reconnu

    return len(mot_de_passe) * math.log2(alphabet_size)

def calculer_entropie_estimee(mot_de_passe):
    """Alias pour compatibilité avec l'insertion demandée."""
    return entropie(mot_de_passe)

def valider_mot_de_passe(mot_de_passe):
    """Vérifie les critères de complexité de base du mot de passe."""
    if len(mot_de_passe) < 12:
        return False, "Le mot de passe doit contenir au moins 12 caractères."
    if not re.search(r"[A-Z]", mot_de_passe):
        return False, "Le mot de passe doit contenir au moins une majuscule."
    if not re.search(r"[a-z]", mot_de_passe):
        return False, "Le mot de passe doit contenir au moins une minuscule."
    if not re.search(r"[0-9]", mot_de_passe):
        return False, "Le mot de passe doit contenir au moins un chiffre."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', mot_de_passe):
        return False, "Le mot de passe doit contenir au moins un caractère spécial."


    # Vérification de l'entropie absolue recommandée
    entropie_totale = calculer_entropie_estimee(mot_de_passe)
    if entropie_totale < ENTROPIE_MINIMALE_BITS:
        return False, f"Entropie insuffisante ({entropie_totale:.2f} bits). Minimum requis : {ENTROPIE_MINIMALE_BITS} bits."

    return True, "Critères de complexité et entropie respectés."

def evaluer_force_mot_de_passe(mot_de_passe):
    """Évalue la force du mot de passe en utilisant zxcvbn."""
    result = zxcvbn(mot_de_passe)
    score = result['score'] # Score de 0 à 4
    # suggestions = result['feedback']['suggestions']
    if score < 3: # On exige un score d'au moins 3 sur 4
        return False, f"Mot de passe jugé trop faible (score {score}/4). Essayez un mot de passe plus complexe et moins courant."
    return True, f"Mot de passe jugé suffisamment fort (score {score}/4)."

def hacher_mot_de_passe(mot_de_passe):
    """Hache le mot de passe en utilisant Argon2."""
    ph = PasswordHasher() # Utilise les paramètres par défaut recommandés
    return ph.hash(mot_de_passe)

def verifier_mot_de_passe(mot_de_passe_hache, mot_de_passe_fourni):
    """Vérifie si le mot de passe fourni correspond au hash stocké."""
    ph = PasswordHasher()
    try:
        ph.verify(mot_de_passe_hache, mot_de_passe_fourni)
        return True
    except argon_exceptions.VerifyMismatchError:
        return False
    except Exception as e:
        print(f"Erreur lors de la vérification du mot de passe : {e}")
        return False # Ou gérer l'erreur autrement

def generer_mot_de_passe_aleatoire(longueur=16):
    """Génère un mot de passe aléatoire fort."""
    caracteres = string.ascii_letters + string.digits + string.punctuation
    while True:
        mdp = ''.join(secrets.choice(caracteres) for i in range(longueur))
        # S'assurer qu'il contient tous les types de caractères requis par valider_mot_de_passe
        if (re.search(r"[A-Z]", mdp) and
            re.search(r"[a-z]", mdp) and
            re.search(r"[0-9]", mdp) and
            re.search(r"[!@#$%^&*(),.?\"/:{}|<>]", mdp)):
            # Vérifier aussi l'entropie et la force zxcvbn
            valide_complexite, _ = valider_mot_de_passe(mdp)
            valide_force, _ = evaluer_force_mot_de_passe(mdp)
            if valide_complexite and valide_force:
                return mdp

# --- Fonctions callable Anvil ---

# Regex pour la validation basique de l'email
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
# Regex pour une validation simple de numéro de téléphone (ex: chiffres, +, -, espaces, (), longueur 8-15)
# Adaptez cette regex si vous avez des formats plus spécifiques en tête
PHONE_REGEX = r"^\+?[\d\s\-\(\)]{8,15}$"

@anvil.server.callable
def add_user(firstname, lastname, email, phone_number, username, password, password_confirm, profile_picture=None):
  """Ajoute un utilisateur après validation et hachage du mot de passe, incluant la photo de profil."""
  
  # 0. Valider le format de l'email
  if not re.match(EMAIL_REGEX, email):
      return "Erreur : Le format de l'adresse email est invalide."
      
  # 0. Valider le format du numéro de téléphone (si fourni)
  if phone_number and not re.match(PHONE_REGEX, phone_number):
      return "Erreur : Le format du numéro de téléphone est invalide."

  # 1. Vérifier si l'utilisateur existe déjà
  if app_tables.users.get(email=email):
      return "Erreur : Un compte existe déjà avec cet email."
  if app_tables.users.get(username=username):
      return "Erreur : Ce nom d'utilisateur est déjà pris."

  # 2. Confirmer que les mots de passe correspondent
  if password != password_confirm:
      return "Erreur : Les mots de passe ne correspondent pas."

  # 3. Valider la complexité et l'entropie du mot de passe
  valide_complexite, message_complexite = valider_mot_de_passe(password)
  if not valide_complexite:
      return f"Erreur : {message_complexite}"

  # 4. Évaluer la force avec zxcvbn
  valide_force, message_force = evaluer_force_mot_de_passe(password)
  if not valide_force:
      return f"Erreur : {message_force}"
      
  # 5. Hacher le mot de passe
  try:
      password_hash = hacher_mot_de_passe(password)
  except Exception as e:
      print(f"Erreur lors du hachage du mot de passe pour {email}: {e}")
      return "Erreur interne lors de la création du compte. Veuillez réessayer."

  # 6. Ajouter l'utilisateur à la base de données
  try:
    now = datetime.now()
    app_tables.users.add_row(
      firstname=firstname,
      lastname=lastname,
      email=email,
      phone_number=phone_number, 
      username=username,
      password=password_hash, 
      photo=profile_picture, 
      created_at=now,
      updated_at=now,
      account_locked=False,
      is_admin=False,
      email_verified=False 
    )
    return "Compte créé avec succès ! Veuillez vérifier votre email."
  except Exception as e:
    print(f"Erreur lors de l'ajout de l'utilisateur {email} à la BDD: {e}")
    return "Erreur interne lors de la création du compte. Veuillez réessayer."


@anvil.server.callable
def is_locked(email):
  """Vérifie si un compte utilisateur est verrouillé."""
  # Attention : Ne pas révéler si l'email existe ou non directement
  try:
      user = app_tables.users.get(email=email)
      if user and user['account_locked']:
          return True
      return False
  except Exception as e:
      print(f"Erreur lors de la vérification du statut de verrouillage pour {email}: {e}")
      # Retourner False ou gérer l'erreur pour ne pas bloquer indûment
      return False

@anvil.server.callable
def suggest_password():
    """Génère et suggère un mot de passe aléatoire fort."""
    return generer_mot_de_passe_aleatoire()

@anvil.server.callable
def get_user_profile():
    """Récupère les informations du profil (y compris la photo) de l'utilisateur connecté."""
    user_info = anvil.server.call('get_user_info') 
    if not user_info:
        return None 
        
    user_row_id = user_info.get('user_row_id')
    if not user_row_id:
         print("Erreur: user_row_id non trouvé dans la session pour get_user_profile")
         return None

    user = app_tables.users.get_by_id(user_row_id)
    if user:
        # Retourner les champs nécessaires, y compris la photo
        profile_data = {
            'firstname': user['firstname'],
            'lastname': user['lastname'],
            'email': user['email'],
            'phone_number': user['phone_number'],
            'username': user['username'],
            # Ajouter la photo (peut être None si aucune photo n'est définie)
            'photo': user['photo'] 
        }
        return profile_data
    else:
        print(f"Erreur: Utilisateur non trouvé avec row_id {user_row_id} pour get_user_profile")
        anvil.server.call('logout_user')
        return None

@anvil.server.callable
def update_user_profile(new_data):
    """Met à jour les informations du profil de l'utilisateur connecté."""
    user_info = anvil.server.call('get_user_info')
    if not user_info:
        return "Erreur : Vous devez être connecté pour modifier votre profil."
        
    user_row_id = user_info.get('user_row_id')
    if not user_row_id:
         return "Erreur : Impossible d'identifier l'utilisateur."

    user = app_tables.users.get_by_id(user_row_id)
    if not user:
        return "Erreur : Utilisateur non trouvé."

    # Valider les nouvelles données (email, téléphone)
    new_email = new_data.get('email')
    new_phone = new_data.get('phone_number')
    
    if new_email and not re.match(EMAIL_REGEX, new_email):
        return "Erreur : Le format de la nouvelle adresse email est invalide."
        
    # Vérifier si le nouvel email est déjà utilisé par un AUTRE utilisateur
    if new_email and new_email != user['email']:
        existing_user = app_tables.users.get(email=new_email)
        if existing_user:
            return "Erreur : Cette adresse email est déjà utilisée par un autre compte."
            
    if new_phone and not re.match(PHONE_REGEX, new_phone):
         return "Erreur : Le format du nouveau numéro de téléphone est invalide."

    # Mettre à jour les champs autorisés
    try:
        update_dict = {
            'firstname': new_data.get('firstname', user['firstname']), # Garde l'ancien si non fourni
            'lastname': new_data.get('lastname', user['lastname']),
            'email': new_email if new_email else user['email'],
            'phone_number': new_phone if new_phone else user['phone_number'],
            'updated_at': datetime.now()
            # Ne pas autoriser la modification du username ici par défaut
        }
        user.update(**update_dict)
        # Mettre à jour l'email dans la session si modifié
        if new_email and new_email != user_info.get('user_email'):
             anvil.server.session['user_email'] = new_email
             
        return "Profil mis à jour avec succès."
    except Exception as e:
        print(f"Erreur lors de la mise à jour du profil pour user {user_row_id}: {e}")
        return "Erreur interne lors de la mise à jour du profil."

@anvil.server.callable
def update_profile_picture(new_photo_media):
    """Met à jour la photo de profil de l'utilisateur connecté."""
    # 1. Vérifier la connexion et obtenir l'ID utilisateur
    user_info = anvil.server.call('get_user_info')
    if not user_info:
        return "Erreur : Vous devez être connecté pour modifier votre photo."
        
    user_row_id = user_info.get('user_row_id')
    if not user_row_id:
         return "Erreur : Impossible d'identifier l'utilisateur."

    # 2. Récupérer l'utilisateur
    user = app_tables.users.get_by_id(user_row_id)
    if not user:
        return "Erreur : Utilisateur non trouvé."

    # 3. Valider l'objet media (vérification basique)
    if not new_photo_media or not hasattr(new_photo_media, 'get_bytes'):
        return "Erreur : Fichier invalide fourni pour la photo."
        
    # !! Optionnel : Re-valider type/taille côté serveur par sécurité !!
    # content_type = new_photo_media.content_type
    # length = new_photo_media.length
    # if content_type not in ALLOWED_IMAGE_TYPES:
    #    return f"Erreur serveur: Type de fichier non supporté ({content_type})"
    # if length > MAX_FILE_SIZE_BYTES:
    #    return f"Erreur serveur: Fichier trop volumineux ({length} octets)"

    # 4. Mettre à jour la photo dans la table
    try:
        user.update(photo=new_photo_media, updated_at=datetime.now())
        # TODO : Si l'intégrité des photos est implémentée, mettre à jour photo_hash ici
        # photo_bytes = new_photo_media.get_bytes()
        # new_hash = calculate_hash(photo_bytes) # Fonction de hachage à définir
        # user.update(photo=new_photo_media, photo_hash=new_hash, updated_at=datetime.now())
        
        return "Photo de profil mise à jour avec succès."
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la photo pour user {user_row_id}: {e}")
        return "Erreur interne lors de la mise à jour de la photo."

@anvil.server.callable
# @anvil.server.require_user
def delete_my_account():
    """Supprime définitivement (hard delete) le compte de l'utilisateur connecté."""
    # !! Sécurité : Idéalement, demander une re-authentification (mot de passe) avant cette action !!
    
    user_info = anvil.server.call('get_user_info')
    if not user_info:
        return "Erreur : Vous devez être connecté pour supprimer votre compte."
        
    user_row_id = user_info.get('user_row_id')
    if not user_row_id:
         return "Erreur : Impossible d'identifier l'utilisateur."

    user = app_tables.users.get_by_id(user_row_id)
    if not user:
        # L'utilisateur n'existe plus, on peut juste déconnecter
        anvil.server.call('logout_user') 
        return "Erreur : Utilisateur non trouvé (peut-être déjà supprimé)."
        
    try:
        # Hard delete : Supprimer la ligne de la table
        user.delete()
        
        # Optionnel: Supprimer les stats associées si cette table est utilisée
        # try:
        #    stats = app_tables.users_stats.get(user_email=user_info.get('user_email'))
        #    if stats:
        #        stats.delete()
        # except Exception as stats_e:
        #    print(f"Avertissement: Erreur lors de la suppression des stats pour user {user_row_id}: {stats_e}")
            
        # Déconnecter l'utilisateur (important car la session contient peut-être encore le row_id)
        anvil.server.call('logout_user')
        return "Compte définitivement supprimé avec succès."
        
    except Exception as e:
        print(f"Erreur lors de la suppression définitive du compte pour user {user_row_id}: {e}")
        return "Erreur interne lors de la suppression du compte."


# --- Fonctions Admin --- 

# --- Helper function (non-callable directement par le client) ---
def _is_caller_admin():
    """Vérifie si l'utilisateur effectuant l'appel est un admin."""
    print("DEBUG (_is_caller_admin): Entering function")
    user_info = None
    try:
        print("DEBUG (_is_caller_admin): Calling get_user_info...")
        # Appel à la fonction dans SessionController
        user_info = anvil.server.call('get_user_info') 
        print(f"DEBUG (_is_caller_admin): get_user_info returned: {user_info}")
    except Exception as e_getinfo:
        print(f"DEBUG (_is_caller_admin): ERROR calling get_user_info: {e_getinfo}")
        # Si l'erreur se produit ici, la cause est probablement dans get_user_info ou l'appel lui-même
        return False
        
    if not user_info or not user_info.get('user_row_id'):
        print("DEBUG (_is_caller_admin): No user_info or user_row_id found in session.")
        return False # Non connecté ou session invalide
    
    user_row_id = user_info['user_row_id']
    print(f"DEBUG (_is_caller_admin): Found user_row_id: {user_row_id}")
    admin_user = None
    try:
        print(f"DEBUG (_is_caller_admin): Getting user row by id: {user_row_id}")
        admin_user = app_tables.users.get_by_id(user_row_id)
        print(f"DEBUG (_is_caller_admin): User row fetched: {admin_user is not None}")
    except Exception as e_getbyid:
         print(f"DEBUG (_is_caller_admin): ERROR getting user by ID: {e_getbyid}")
         return False
         
    # Vérifier que l'utilisateur existe, est admin et est actif
    if admin_user and admin_user['is_admin'] and admin_user.get('is_active', True):
        print("DEBUG (_is_caller_admin): User is admin and active. Returning True.")
        return True
        
    print("DEBUG (_is_caller_admin): User is not admin or not active. Returning False.")
    return False

# --- Fonctions callable pour l'admin --- 

@anvil.server.callable
def is_current_user_admin():
    """Fonction simple pour que le client vérifie le statut admin."""
    print("DEBUG (is_current_user_admin): Callable function entered. Calling helper...")
    result = _is_caller_admin()
    print(f"DEBUG (is_current_user_admin): Helper returned {result}. Returning to client.")
    return result

@anvil.server.callable
def admin_get_all_users():
    """Retourne une liste simplifiée de tous les utilisateurs pour l'admin."""
    if not _is_caller_admin():
        raise anvil.server.PermissionDenied("Accès réservé aux administrateurs.")
        
    user_list = []
    # Itérer sur tous les utilisateurs
    for user in app_tables.users.search():
        user_list.append({
            'email': user['email'],
            'firstname': user['firstname'],
            'lastname': user['lastname'],
            'username': user['username'],
            'is_admin': user['is_admin'],
            # Gérer si la colonne is_active n'existe pas encore partout
            'is_active': user.get('is_active', True) if user['email'] != f"deleted_{user.get_id()}@example.com" else False, 
            'account_locked': user.get('account_locked', False),
            'row_id': user.get_id() # Important pour les actions futures
        })
    return user_list

@anvil.server.callable
def admin_get_user_details(user_row_id):
    """Retourne toutes les données modifiables d'un utilisateur spécifique."""
    if not _is_caller_admin():
        raise anvil.server.PermissionDenied("Accès réservé aux administrateurs.")
        
    user = app_tables.users.get_by_id(user_row_id)
    if not user:
        return None # Ou lever une erreur: raise ValueError("Utilisateur non trouvé")
        
    # Retourner toutes les colonnes pertinentes (sauf le hash du mot de passe)
    user_details = dict(user) 
    user_details.pop('password', None) # Exclure le mot de passe
    user_details['row_id'] = user.get_id() # Ajouter row_id pour référence facile
    return user_details
    
@anvil.server.callable
def admin_update_user(user_row_id, update_data):
    """Met à jour les données d'un utilisateur spécifié par l'admin."""
    if not _is_caller_admin():
        raise anvil.server.PermissionDenied("Accès réservé aux administrateurs.")

    user_to_update = app_tables.users.get_by_id(user_row_id)
    if not user_to_update:
        return f"Erreur : Utilisateur avec ID {user_row_id} non trouvé."

    # --- Validation et Nettoyage des Données Reçues --- 
    validated_data = {}
    allowed_fields = ['firstname', 'lastname', 'email', 'phone_number', 'username', 
                      'is_admin', 'is_active', 'account_locked'] 
    
    current_admin_info = anvil.server.call('get_user_info')
    current_admin_row_id = current_admin_info.get('user_row_id') if current_admin_info else None

    for field in allowed_fields:
        if field in update_data:
            value = update_data[field]
            
            # Validation spécifique
            if field == 'email':
                if not re.match(EMAIL_REGEX, value):
                    return "Erreur : Format d'email invalide."
                if value != user_to_update['email'] and app_tables.users.get(email=value):
                    return "Erreur : Cette adresse email est déjà utilisée."
            elif field == 'phone_number':
                 if value and not re.match(PHONE_REGEX, value): 
                     return "Erreur : Format de téléphone invalide."
            elif field in ['is_admin', 'is_active', 'account_locked']:
                 if not isinstance(value, bool):
                     return f"Erreur : Le champ {field} doit être un booléen (True/False)."
                 if field == 'is_admin' and user_row_id == current_admin_row_id and not value:
                     return "Erreur : Un administrateur ne peut pas se retirer ses propres droits."
                     
            validated_data[field] = value

    if not validated_data:
        return "Erreur : Aucune donnée valide fournie pour la mise à jour."

    validated_data['updated_at'] = datetime.now()

    # --- Mise à jour ---
    try:
        user_to_update.update(**validated_data)
        return "Utilisateur mis à jour avec succès."
    except Exception as e:
        print(f"Erreur admin lors de la mise à jour de user {user_row_id}: {e}")
        return "Erreur interne lors de la mise à jour de l'utilisateur."
