# --- Importations nécessaires ---
from ._anvil_designer import ProfileTemplate # Suppose un template Anvil nommé Profile
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# Importer les constantes de validation depuis SignUpForm ou les redéfinir ici
# (Il serait préférable de les mettre dans un module partagé)
ALLOWED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# --- Définition de la classe du formulaire ---
class Profile(ProfileTemplate):
  def __init__(self, **properties):
    # Initialiser les composants du designer
    self.init_components(**properties)
    
    # Stocker les données utilisateur initiales
    self.user_data = None 
    
    # Charger les données utilisateur lorsque le formulaire s'affiche
    self.load_user_data() 
    
    # Lier les gestionnaires d'événements aux boutons (adaptez les noms si besoin)
    if hasattr(self, 'save_button'):
        self.save_button.add_event_handler('click', self.save_button_click)
    if hasattr(self, 'delete_account_button'):
        self.delete_account_button.add_event_handler('click', self.delete_account_button_click)
        
    # Lier le handler pour le nouveau FileLoader
    # **ACTION REQUISE : Ajoutez un FileLoader nommé 'profile_picture_uploader' dans le designer**
    if hasattr(self, 'profile_picture_uploader'):
        # Optionnel: Rendre le FileLoader invisible et utiliser un bouton séparé pour le déclencher
        # self.profile_picture_uploader.visible = False 
        # if hasattr(self, 'change_picture_button'):
        #    self.change_picture_button.add_event_handler('click', self.change_picture_button_click)
        
        # Lier l'événement 'change' qui se déclenche après la sélection du fichier
        self.profile_picture_uploader.add_event_handler('change', self.profile_picture_uploader_change)
    else:
        print("AVERTISSEMENT: FileLoader 'profile_picture_uploader' non trouvé dans le formulaire Profile.")

  # --- Chargement des données ---
  def load_user_data(self):
    """Appelle la fonction serveur pour obtenir les données du profil et peuple les champs."""
    # Appelle la fonction serveur qui retourne maintenant la photo aussi
    self.user_data = anvil.server.call('get_user_profile')
    
    if self.user_data:
        # Peupler les champs texte
        self.firstname_textbox.text = self.user_data.get('firstname', '')
        self.lastname_textbox.text = self.user_data.get('lastname', '')
        self.email_textbox.text = self.user_data.get('email', '')
        self.phone_textbox.text = self.user_data.get('phone_number', '')
        self.username_label.text = f"Nom d'utilisateur : {self.user_data.get('username', 'N/A')}"
        
        # --- Afficher la photo de profil directement depuis les données reçues --- 
        if hasattr(self, 'profile_image'):
            profile_photo = self.user_data.get('photo') # Récupère l'objet Media (ou None)
            if profile_photo:
                self.profile_image.source = profile_photo
            else:
                # Assigner une image par défaut si pas de photo
                self.profile_image.source = '_/theme/logo-tearoom-simple-logo.png' 
        # --- Fin affichage photo --- 
            
    else:
        # Gérer le cas où les données ne peuvent pas être chargées (erreur ou déconnexion)
        Notification("Impossible de charger les informations du profil. Vous allez être déconnecté.", title="Erreur", style="danger").show()
        open_form('MainForm') # Recharger pour déconnecter

  # --- Sauvegarde des modifications ---
  def save_button_click(self, **event_args):
    """Appelle la fonction serveur pour mettre à jour le profil."""
    # Récupérer les nouvelles valeurs des champs (adaptez les noms de composants)
    new_data = {
        'firstname': self.firstname_textbox.text,
        'lastname': self.lastname_textbox.text,
        'email': self.email_textbox.text,
        'phone_number': self.phone_textbox.text
    }
    
    # Désactiver le bouton pendant l'appel
    self.save_button.enabled = False
    self.save_button.text = "Sauvegarde..."
    
    try:
        response = anvil.server.call('update_user_profile', new_data)
        if response == "Profil mis à jour avec succès.":
            Notification(response, title="Succès", style="success").show()
            # Recharger les données pour refléter les changements
            self.load_user_data() 
        else:
            # Afficher l'erreur retournée par le serveur
            Notification(response, title="Erreur de mise à jour", style="danger").show()
    except Exception as e:
         Notification(f"Erreur de communication: {e}", title="Erreur", style="danger").show()
    finally:
        # Réactiver le bouton
        self.save_button.enabled = True
        self.save_button.text = "Sauvegarder les modifications"

  # --- Suppression du compte ---
  def delete_account_button_click(self, **event_args):
    """Demande confirmation et appelle la fonction serveur pour supprimer le compte."""
    # Demander confirmation
    if confirm("Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible.", 
               title="Confirmation de suppression", large=True, buttons=[("Supprimer", "delete"), ("Annuler", "cancel")] ) == "delete":
        
        # Désactiver le bouton
        self.delete_account_button.enabled = False
        self.delete_account_button.text = "Suppression..."
        
        # !! Rappel Sécurité : Idéalement, ajouter une étape de re-authentification ici !!
        
        try:
            response = anvil.server.call('delete_my_account')
            if response == "Compte supprimé avec succès.":
                Notification(response, title="Compte Supprimé", style="success").show()
                # Recharger MainForm déclenchera la déconnexion et la redirection
                open_form('MainForm') 
            else:
                Notification(response, title="Erreur de suppression", style="danger").show()
                # Réactiver le bouton en cas d'erreur serveur
                self.delete_account_button.enabled = True
                self.delete_account_button.text = "Supprimer mon compte"
        except Exception as e:
             Notification(f"Erreur de communication: {e}", title="Erreur", style="danger").show()
             self.delete_account_button.enabled = True
             self.delete_account_button.text = "Supprimer mon compte" 

  # --- Gestionnaire pour le changement du FileLoader (upload photo) ---
  def profile_picture_uploader_change(self, **event_args):
    """Valide le fichier sélectionné et appelle le serveur pour mettre à jour la photo."""
    new_file = self.profile_picture_uploader.file
    
    if new_file:
        # 1. Valider le fichier (type et taille)
        if new_file.content_type not in ALLOWED_IMAGE_TYPES:
            Notification(f"Type de fichier non supporté ({new_file.content_type}). Veuillez choisir une image PNG, JPG, GIF ou WEBP.", 
                         title="Format Invalide", style="danger", timeout=5).show()
            self.profile_picture_uploader.clear()
            return
            
        if new_file.length > MAX_FILE_SIZE_BYTES:
            file_size_mb = round(new_file.length / (1024*1024), 2)
            Notification(f"Le fichier est trop volumineux ({file_size_mb} Mo). La taille maximale autorisée est {MAX_FILE_SIZE_MB} Mo.", 
                         title="Fichier Trop Grand", style="danger", timeout=5).show()
            self.profile_picture_uploader.clear()
            return

        # 2. Appeler le serveur pour mettre à jour
        try:
            # Afficher un indicateur de chargement si possible
            if hasattr(self, 'change_picture_button'): self.change_picture_button.enabled = False
            self.profile_picture_uploader.enabled = False # Désactiver pendant l'upload
            
            response = anvil.server.call('update_profile_picture', new_file)
            
            if response == "Photo de profil mise à jour avec succès.":
                Notification(response, title="Succès", style="success").show()
                # Mettre à jour l'image affichée immédiatement
                self.profile_image.source = new_file 
                # Mettre à jour les données locales (si vous les réutilisez ailleurs)
                if self.user_data:
                    self.user_data['photo'] = new_file
                # Vider le FileLoader après succès
                self.profile_picture_uploader.clear()
            else:
                 Notification(response, title="Erreur Serveur", style="danger").show()
                 self.profile_picture_uploader.clear()
                 
        except Exception as e:
            Notification(f"Erreur de communication lors de la mise à jour de la photo: {e}", title="Erreur", style="danger").show()
            self.profile_picture_uploader.clear()
        finally:
            # Réactiver les boutons
            if hasattr(self, 'change_picture_button'): self.change_picture_button.enabled = True
            self.profile_picture_uploader.enabled = True
            
    # else: Fichier a été effacé, pas d'action

  # --- Gestionnaire pour déclencher le FileLoader (si bouton séparé) ---
  # def change_picture_button_click(self, **event_args):
  #    """Déclenche le dialogue de sélection de fichier du FileLoader caché."""
  #    if hasattr(self, 'profile_picture_uploader'):
  #        self.profile_picture_uploader.trigger('click') 