# --- Importations nécessaires ---
from ._anvil_designer import AdminPanelTemplate # Doit correspondre au nom du formulaire créé
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class AdminPanel(AdminPanelTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Stocker l'ID de l'utilisateur sélectionné
        self.selected_user_row_id = None
        
        # Configurer le DataGrid
        self.user_grid.columns = [
            # Clé = nom de colonne dans les données reçues, Titre = affiché
            {"id": "email", "title": "Email", "data_key": "email"},
            {"id": "firstname", "title": "Prénom", "data_key": "firstname"},
            {"id": "lastname", "title": "Nom", "data_key": "lastname"},
            {"id": "username", "title": "Username", "data_key": "username"},
            {"id": "is_active", "title": "Actif?", "data_key": "is_active"},
            {"id": "is_admin", "title": "Admin?", "data_key": "is_admin"},
            {"id": "account_locked", "title": "Verrouillé?", "data_key": "account_locked"},
            # La colonne row_id n'a pas besoin d'être visible mais est dans les données
        ]
        self.user_grid.add_event_handler('row_selected', self.user_grid_row_selected)
        
        # Lier le bouton de sauvegarde (Assurez-vous que le bouton existe et s'appelle 'save_user_button')
        if hasattr(self, 'save_user_button'):
           self.save_user_button.add_event_handler('click', self.save_user_button_click)
        else:
            print("AVERTISSEMENT (AdminPanel): Bouton 'save_user_button' non trouvé.")
        
        # Initialiser et cacher le panneau d'édition
        self.clear_edit_panel() 
        
        # Charger la liste des utilisateurs au démarrage
        self.load_user_list()

    def load_user_list(self):
        """Charge ou recharge la liste des utilisateurs dans le DataGrid."""
        try:
            user_list_data = anvil.server.call('admin_get_all_users')
            self.user_grid.items = user_list_data
            # Optionnel: Rafraîchir l'affichage du panneau d'édition si un utilisateur était sélectionné
            if self.selected_user_row_id:
                # Retrouver la ligne mise à jour (ou simplement désélectionner) 
                matching_rows = [r for r in user_list_data if r['row_id'] == self.selected_user_row_id]
                if matching_rows:
                    self.user_grid_row_selected(matching_rows[0]) # Re-sélectionner pour rafraîchir le panel
                else:
                    self.clear_edit_panel() # L'utilisateur a pu être supprimé
            else: 
                self.clear_edit_panel() 
        except anvil.server.PermissionDenied as e:
            Notification(f"Accès refusé au panneau d'administration.", title="Accès Refusé", style="danger").show()
            open_form('MainForm') 
        except Exception as e:
            Notification(f"Erreur lors du chargement de la liste des utilisateurs: {e}", title="Erreur", style="danger").show()

    def clear_edit_panel(self):
        """Réinitialise le panneau d'édition."""
        self.selected_user_row_id = None
        # Assurez-vous que les composants du panneau existent
        if hasattr(self, 'edit_panel'): self.edit_panel.visible = False
        if hasattr(self, 'edit_firstname_textbox'): self.edit_firstname_textbox.text = ""
        if hasattr(self, 'edit_lastname_textbox'): self.edit_lastname_textbox.text = ""
        if hasattr(self, 'edit_email_textbox'): self.edit_email_textbox.text = ""
        if hasattr(self, 'edit_phone_textbox'): self.edit_phone_textbox.text = ""
        if hasattr(self, 'edit_username_textbox'): self.edit_username_textbox.text = ""
        if hasattr(self, 'edit_is_admin_checkbox'): self.edit_is_admin_checkbox.checked = False
        if hasattr(self, 'edit_is_active_checkbox'): self.edit_is_active_checkbox.checked = False
        if hasattr(self, 'edit_account_locked_checkbox'): self.edit_account_locked_checkbox.checked = False
        if hasattr(self, 'edit_row_id_label'): self.edit_row_id_label.text = "ID: -"

    def user_grid_row_selected(self, row, **event_args):
        """Gère la sélection d'une ligne dans le DataGrid."""
        if row and hasattr(self, 'edit_panel'): # Vérifier si ligne sélectionnée et panel existe
            self.selected_user_row_id = row.get('row_id') # Utiliser .get pour éviter KeyError
            if not self.selected_user_row_id:
                 Notification("Impossible de récupérer l'ID de l'utilisateur sélectionné.", title="Erreur Interne", style="danger").show()
                 self.clear_edit_panel()
                 return
                 
            if hasattr(self, 'edit_row_id_label'): self.edit_row_id_label.text = f"ID: {self.selected_user_row_id}"
            
            # Charger les détails complets de l'utilisateur sélectionné
            try:
                # Mettre le panel visible immédiatement pour montrer le chargement?
                self.edit_panel.visible = True 
                details = anvil.server.call('admin_get_user_details', self.selected_user_row_id)
                if details:
                    if hasattr(self, 'edit_firstname_textbox'): self.edit_firstname_textbox.text = details.get('firstname', '')
                    if hasattr(self, 'edit_lastname_textbox'): self.edit_lastname_textbox.text = details.get('lastname', '')
                    if hasattr(self, 'edit_email_textbox'): self.edit_email_textbox.text = details.get('email', '')
                    if hasattr(self, 'edit_phone_textbox'): self.edit_phone_textbox.text = details.get('phone_number', '')
                    if hasattr(self, 'edit_username_textbox'): self.edit_username_textbox.text = details.get('username', '')
                    if hasattr(self, 'edit_is_admin_checkbox'): self.edit_is_admin_checkbox.checked = details.get('is_admin', False)
                    if hasattr(self, 'edit_is_active_checkbox'): self.edit_is_active_checkbox.checked = details.get('is_active', True)
                    if hasattr(self, 'edit_account_locked_checkbox'): self.edit_account_locked_checkbox.checked = details.get('account_locked', False)
                    # Charger d'autres champs ici
                else:
                    Notification("Impossible de charger les détails de cet utilisateur (non trouvé ou supprimé).", title="Erreur", style="warning").show()
                    self.clear_edit_panel()
            except anvil.server.PermissionDenied as e:
                 Notification(f"Accès refusé.", title="Erreur d'autorisation", style="danger").show()
                 self.clear_edit_panel()
            except Exception as e:
                 Notification(f"Erreur lors du chargement des détails: {e}", title="Erreur", style="danger").show()
                 self.clear_edit_panel()
        else:
             self.clear_edit_panel() # Désélection

    def save_user_button_click(self, **event_args):
        """Sauvegarde les modifications apportées à l'utilisateur sélectionné."""
        if not self.selected_user_row_id:
            Notification("Veuillez d'abord sélectionner un utilisateur dans la liste.", title="Aucune sélection", style="warning").show()
            return

        # Récupérer les données modifiées depuis les champs d'édition
        update_data = {}
        if hasattr(self, 'edit_firstname_textbox'): update_data['firstname'] = self.edit_firstname_textbox.text
        if hasattr(self, 'edit_lastname_textbox'): update_data['lastname'] = self.edit_lastname_textbox.text
        if hasattr(self, 'edit_email_textbox'): update_data['email'] = self.edit_email_textbox.text
        if hasattr(self, 'edit_phone_textbox'): update_data['phone_number'] = self.edit_phone_textbox.text
        if hasattr(self, 'edit_username_textbox'): update_data['username'] = self.edit_username_textbox.text
        if hasattr(self, 'edit_is_admin_checkbox'): update_data['is_admin'] = self.edit_is_admin_checkbox.checked
        if hasattr(self, 'edit_is_active_checkbox'): update_data['is_active'] = self.edit_is_active_checkbox.checked
        if hasattr(self, 'edit_account_locked_checkbox'): update_data['account_locked'] = self.edit_account_locked_checkbox.checked
        # Ajouter d'autres champs si modifiables

        # Désactiver bouton
        self.save_user_button.enabled = False
        self.save_user_button.text = "Sauvegarde..."

        try:
            response = anvil.server.call('admin_update_user', self.selected_user_row_id, update_data)
            Notification(response, title="Résultat Mise à Jour", style=("success" if "succès" in response.lower() else "danger")).show()
            # Recharger la liste pour voir les changements
            self.load_user_list() 
        except anvil.server.PermissionDenied as e:
             Notification(f"Accès refusé.", title="Erreur d'autorisation", style="danger").show()
        except Exception as e:
             Notification(f"Erreur lors de la sauvegarde: {e}", title="Erreur", style="danger").show()
        finally:
            # Réactiver bouton
            self.save_user_button.enabled = True
            self.save_user_button.text = "Sauvegarder Modifications" 