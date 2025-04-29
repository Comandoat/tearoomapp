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

@anvil.server.callable
def add_user(firstname, lastname, email, phone_number, username, password, password_confirm):
  """Ajoute un utilisateur après validation et hachage du mot de passe."""
  
  # 0. Vérifier si l'utilisateur existe déjà
  if app_tables.users.get(email=email):
      return "Erreur : Un compte existe déjà avec cet email."
  if app_tables.users.get(username=username):
      return "Erreur : Ce nom d'utilisateur est déjà pris."

  # 1. Confirmer que les mots de passe correspondent
  if password != password_confirm:
      return "Erreur : Les mots de passe ne correspondent pas."

  # 2. Valider la complexité et l'entropie
  valide_complexite, message_complexite = valider_mot_de_passe(password)
  if not valide_complexite:
      return f"Erreur : {message_complexite}"

  # 3. Évaluer la force avec zxcvbn
  valide_force, message_force = evaluer_force_mot_de_passe(password)
  if not valide_force:
      return f"Erreur : {message_force}"
      
  # 4. Hacher le mot de passe
  try:
      password_hash = hacher_mot_de_passe(password)
  except Exception as e:
      print(f"Erreur lors du hachage du mot de passe pour {email}: {e}")
      # Ne pas donner de détails précis à l'utilisateur pour des raisons de sécurité
      return "Erreur interne lors de la création du compte. Veuillez réessayer."

  # 5. Ajouter l'utilisateur à la base de données
  try:
    now = datetime.now()
    app_tables.users.add_row(
      firstname=firstname,
      lastname=lastname,
      email=email,
        phone_number=phone_number, # S'assurer que ce champ est bien géré/validé côté client aussi
      username=username,
        # Ne JAMAIS stocker le mot de passe en clair
        password=password_hash, # Stocker le hash Argon2
      created_at=now,
      updated_at=now,
      account_locked=False,
        is_admin=False, # Par défaut, non admin
        email_verified=False # L'email n'est pas encore vérifié
        # Ajouter d'autres champs par défaut si nécessaire
      )
    # Potentiellement, envoyer un email de vérification ici
    return "Compte créé avec succès ! Veuillez vérifier votre email."
  except Exception as e:
    print(f"Erreur lors de l'ajout de l'utilisateur {email} à la BDD: {e}")
    # Ne pas donner de détails précis à l'utilisateur
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
