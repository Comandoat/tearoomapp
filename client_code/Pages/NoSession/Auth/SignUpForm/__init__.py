from ._anvil_designer import SignUpFormTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# Définir les types MIME et la taille maximale autorisés
ALLOWED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

class SignUpForm(SignUpFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.sign_up_form_buttons.submit_button.add_event_handler('click', self.submit_click)
    if hasattr(self, 'suggest_password_button'):
        self.suggest_password_button.add_event_handler('click', self.suggest_password_click)
    
    # Attacher le gestionnaire d'événement change au FileLoader
    if hasattr(self, 'profile_picture_field'):
        self.profile_picture_field.add_event_handler('change', self.profile_picture_field_change)

    # --- Lier le gestionnaire pour l'événement reset venant de FormButtons --- 
    # Utiliser set_event_handler pour écouter les événements levés par le composant enfant
    self.sign_up_form_buttons.set_event_handler('x-reset-clicked', self.reset_form_fields)

  def reset_form_fields(self, **event_args):
    """Vide tous les champs du formulaire d'inscription."""
    # Vider les champs texte
    if hasattr(self.name_fields, 'firstname_field'): self.name_fields.firstname_field.text = ""
    if hasattr(self.name_fields, 'lastname_field'): self.name_fields.lastname_field.text = ""
    if hasattr(self.credentials_fields, 'email_field'): self.credentials_fields.email_field.text = ""
    if hasattr(self.credentials_fields, 'password_field'): self.credentials_fields.password_field.text = ""
    if hasattr(self, 'confirmed_password_field'): self.confirmed_password_field.text = ""
    if hasattr(self, 'phone_number'): self.phone_number.text = ""
    if hasattr(self, 'username_field'): self.username_field.text = ""
    # Vider le FileLoader
    if hasattr(self, 'profile_picture_field'): self.profile_picture_field.clear()
    # Optionnel: Vider les labels d'erreur ou notifications si nécessaire
    print("SignUp Form fields cleared.") # Pour débogage

  def profile_picture_field_change(self, **event_args):
    """Vérifie le fichier chargé lorsque l'utilisateur sélectionne une image."""
    file = self.profile_picture_field.file
    
    if file:
        
        # Vérification du type de fichier
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            Notification(f"Type de fichier non supporté ({file.content_type}). Veuillez choisir une image PNG, JPG, GIF ou WEBP.", 
                         title="Format Invalide", style="danger", timeout=5).show()
            self.profile_picture_field.clear()
            return
            
        # Vérification de la taille du fichier
        if file.length > MAX_FILE_SIZE_BYTES:
            file_size_mb = round(file.length / (1024*1024), 2)
            Notification(f"Le fichier est trop volumineux ({file_size_mb} Mo). La taille maximale autorisée est {MAX_FILE_SIZE_MB} Mo.", 
                         title="Fichier Trop Grand", style="danger", timeout=5).show()
            self.profile_picture_field.clear()
            return
        
    else:
        pass

  def submit_click(self, **event_args):
    """This method is called when the submit button is clicked"""
    firstname = self.name_fields.firstname_field.text 
    lastname = self.name_fields.lastname_field.text
    email = self.credentials_fields.email_field.text
    phone_number = self.phone_number.text
    username = self.username_field.text
    password = self.credentials_fields.password_field.text
    confirmed_password = self.confirmed_password_field.text 
    # Récupérer l'objet Media depuis le FileLoader
    # Assurez-vous que profile_picture_field est bien le nom de votre composant FileLoader
    profile_pic_media = self.profile_picture_field.file if self.profile_picture_field.file else None
    
    if not all([firstname, lastname, email, username, password, confirmed_password]):
        Notification("Veuillez remplir tous les champs obligatoires.", style="warning", title="Champ manquant").show()
        return

    if password != confirmed_password:
        Notification("Les mots de passe ne sont pas identiques.", style="warning", title="Erreur de confirmation").show()
        return

    # Si un fichier est présent mais n'a pas passé la validation (ne devrait pas arriver si clear() a fonctionné)
    if self.profile_picture_field.file and not profile_pic_media:
         Notification("Veuillez sélectionner une image de profil valide.", title="Image Invalide", style="warning").show()
         return

    self.sign_up_form_buttons.submit_button.enabled = False
    self.sign_up_form_buttons.submit_button.text = "Création en cours..."

    try:
      # Appeler la fonction serveur en ajoutant l'objet media
      response = anvil.server.call('add_user', 
                                  firstname, 
                                  lastname, 
                                  email, 
                                  phone_number, 
                                  username, 
                                  password, 
                                  confirmed_password, 
                                  profile_pic_media) # Ajout du paramètre
      
      if isinstance(response, str) and response.startswith("Erreur :"): 
        Notification(response, style="danger", title="Échec de l'inscription").show()
      elif response == "Compte créé avec succès ! Veuillez vérifier votre email.":
        Notification(response, style="success", title="Inscription réussie").show()
        # Vider aussi le champ de fichier
        self.profile_picture_field.clear()
        # ... (vider les autres champs) ...
        self.name_fields.firstname_field.text = ""
        self.name_fields.lastname_field.text = ""
        self.credentials_fields.email_field.text = ""
        self.credentials_fields.password_field.text = ""
        self.confirmed_password_field.text = ""
        self.phone_number.text = ""
        self.username_field.text = ""
        get_open_form().load_page("login")
      else:
         Notification(f"Réponse inattendue du serveur: {response}", style="danger", title="Erreur Inattendue").show()

    except anvil.server.InternalError as e:
        Notification(f"Erreur serveur: {e.message}", style="danger", title="Erreur Serveur").show()
    except anvil.server.PermissionDenied as e:
         Notification(f"Accès refusé: {e.message}", style="danger", title="Non autorisé").show()
    except Exception as e:
      Notification(f"Une erreur de communication est survenue: {e}", style="danger", title="Erreur").show()
    finally:
       self.sign_up_form_buttons.submit_button.enabled = True
       self.sign_up_form_buttons.submit_button.text = "S'inscrire"

  def suggest_password_click(self, **event_args):
      try:
          suggested_password = anvil.server.call('suggest_password')
          self.credentials_fields.password_field.text = suggested_password
          self.confirmed_password_field.text = suggested_password
          Notification("Mot de passe suggéré inséré.", style="info", timeout=2).show()
      except anvil.server.InternalError as e:
          Notification(f"Erreur serveur lors de la suggestion: {e.message}", style="danger").show()
      except Exception as e:
          Notification(f"Erreur de communication lors de la suggestion: {e}", style="danger").show()
