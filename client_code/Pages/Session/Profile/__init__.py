# --- Importations nécessaires ---
from ._anvil_designer import ProfileTemplate # Suppose un template Anvil nommé Profile
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

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

  # --- Chargement des données ---
  def load_user_data(self):
    """Appelle la fonction serveur pour obtenir les données du profil et peuple les champs."""
    self.user_data = anvil.server.call('get_user_profile')
    
    if self.user_data:
        # Peupler les champs du formulaire (adaptez les noms de composants)
        self.firstname_textbox.text = self.user_data.get('firstname', '')
        self.lastname_textbox.text = self.user_data.get('lastname', '')
        self.email_textbox.text = self.user_data.get('email', '')
        self.phone_textbox.text = self.user_data.get('phone_number', '')
        self.username_label.text = f"Nom d'utilisateur : {self.user_data.get('username', 'N/A')}" # Afficher username (non modifiable ici)
        # Afficher la photo de profil si elle existe
        # user_row = app_tables.users.get_by_id(anvil.server.call('get_user_info')['user_row_id']) # Alternative pour récupérer la photo
        # if user_row and user_row['photo']:
        #    self.profile_image.source = user_row['photo']
        # else:
        #    self.profile_image.source = '_/theme/logo-placeholder.png' # Image par défaut
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