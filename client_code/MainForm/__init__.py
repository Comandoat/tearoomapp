from ._anvil_designer import MainFormTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# Ces imports sont corrects
from ..Pages.NoSession.Landing import Landing
from ..Pages.NoSession.Legal.TermsOfService import TermsOfService
from ..Pages.NoSession.Legal.CookiesPolicy import CookiesPolicy
from ..Pages.NoSession.Legal.PrivatePolicy import PrivatePolicy
from ..Pages.NoSession.Legal.LegalInformation import LegalInformation
from ..Pages.NoSession.Products.Teas import Teas
from ..Pages.NoSession.Products.Goodies import Goodies
from ..Pages.NoSession.Auth.SignUpForm import SignUpForm
from ..Pages.NoSession.Auth.LogInForm import LogInForm
from ..Pages.Session.Profile import Profile
from ..Pages.Session.Admin.AdminPanel import AdminPanel

class MainForm(MainFormTemplate):
  def __init__(self, **properties):
    self.user = None # Stocker les infos utilisateur si connecté
    self.is_admin = False # <<< Ajouter pour stocker le statut admin
    self.init_components(**properties)
    self.check_login_status() # Vérifier si l'utilisateur est déjà connecté
    if not self.user:
        # Si non connecté, charger la page d'accueil par défaut
        self.load_page("landing") 
    else:
        # Charger le profil par défaut si connecté et non-admin
        # Ou charger le panel admin si admin ? (à décider)
        if self.is_admin:
             self.load_page("admin") # Charger admin par défaut si admin
        else:
             self.load_page("profile") # Charge le profil par défaut si connecté

  def check_login_status(self):
    """Vérifie la session serveur et met à jour l'état et l'UI."""
    user_info = anvil.server.call('get_user_info')
    self.is_admin = False # Réinitialiser par défaut
    if user_info:
        self.user = user_info
        # <<< Vérifier si l'utilisateur est admin >>>
        try:
            # Appel serveur pour vérifier le statut admin
            self.is_admin = anvil.server.call('is_current_user_admin')
        except Exception as e:
             print(f"Erreur lors de la vérification du statut admin: {e}")
             self.is_admin = False
                 
        # Mettre à jour l'UI pour l'état connecté
        # Assurez-vous que ces noms de liens/boutons existent dans votre designer
        if hasattr(self, 'login_link'): self.login_link.visible = False
        if hasattr(self, 'signup_link'): self.signup_link.visible = False
        if hasattr(self, 'logout_link'): self.logout_link.visible = True
        # Ajoutez d'autres éléments d'UI si nécessaire (ex: lien vers profil)
        if hasattr(self, 'profile_link'): self.profile_link.visible = True 
        if hasattr(self, 'welcome_label'): 
            self.welcome_label.visible = True
            # Vous pourriez récupérer plus d'infos (prénom) pour personnaliser
            # self.welcome_label.text = f"Bienvenue {self.user['firstname']}" 
            self.welcome_label.text = f"Connecté: {self.user['user_email']}"
        # Attacher le handler ici s'il n'est pas déjà dans le designer
        self.logout_link.set_event_handler('click', self.logout_link_click)
        if hasattr(self, 'profile_link'): 
             # Attacher le handler ici s'il n'est pas déjà dans le designer
             self.profile_link.set_event_handler('click', self.profile_link_click)
        # <<< Afficher/masquer lien admin >>>
        # Assurez-vous d'avoir un lien nommé 'admin_link' dans le designer
        if hasattr(self, 'admin_link'): 
            self.admin_link.visible = self.is_admin
            if self.is_admin:
                 # Lier le handler au clic
                 self.admin_link.set_event_handler('click', self.admin_link_click)
        
        # <<< Afficher indicateur panier et mettre à jour >>>
        if hasattr(self, 'cart_indicator_label'):
             self.cart_indicator_label.visible = True
             # Lier le clic pour aller au panier (si pas déjà fait)
             self.cart_indicator_label.set_event_handler('click', self.cart_indicator_click)
             # Mettre à jour le compteur
             self.update_cart_indicator()
        else:
            print("AVERTISSEMENT (MainForm): Label 'cart_indicator_label' non trouvé.")
    else:
        self.user = None
        # Mettre à jour l'UI pour l'état déconnecté
        if hasattr(self, 'login_link'): self.login_link.visible = True
        if hasattr(self, 'signup_link'): self.signup_link.visible = True
        if hasattr(self, 'logout_link'): self.logout_link.visible = False
        if hasattr(self, 'profile_link'): self.profile_link.visible = False
        if hasattr(self, 'welcome_label'): self.welcome_label.visible = False
        if hasattr(self, 'admin_link'): self.admin_link.visible = False # Cacher si déconnecté
        if hasattr(self, 'cart_indicator_label'): self.cart_indicator_label.visible = False

  def update_cart_indicator(self):
    """Met à jour le texte de l'indicateur du panier."""
    if self.user and hasattr(self, 'cart_indicator_label'): # Vérifier si connecté et si le label existe
        try:
            item_count = anvil.server.call('get_cart_item_count')
            self.cart_indicator_label.text = f"Panier ({item_count})"
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'indicateur panier: {e}")
            # Afficher un état d'erreur ou juste le texte par défaut?
            self.cart_indicator_label.text = "Panier (?)"
    # else: Pas connecté ou label non trouvé, ne rien faire

  def load_page(self, page_name):
    self.content_panel.clear()

    if page_name == "landing":
      self.content_panel.add_component(Landing()) 
    elif page_name == "legal":
      self.content_panel.add_component(LegalInformation())
    elif page_name == "terms":
      self.content_panel.add_component(TermsOfService())
    elif page_name == "private":
      self.content_panel.add_component(PrivatePolicy())
    elif page_name == "cookies":
      self.content_panel.add_component(CookiesPolicy())
    elif page_name == "teas":
      self.content_panel.add_component(Teas())
    elif page_name == "goodies":
      self.content_panel.add_component(Goodies())
    elif page_name == "signup" and not self.user:
      signup_form = SignUpForm()
      signup_form.role = "custom-wide"
      self.content_panel.add_component(signup_form)
    elif page_name == "login" and not self.user:
      login_form = LogInForm()
      login_form.role = "custom-wide"
      self.content_panel.add_component(login_form)
    elif page_name == "profile" and self.user:
        # S'assurer que self.user est bien chargé avant d'ajouter la page Profile
        if self.user:
             self.content_panel.add_component(Profile())
        else:
             # Rediriger vers login si on essaie d'accéder à profile sans être connecté
             print("Accès non autorisé à la page profil, redirection vers login.")
             self.load_page("login") 
    elif page_name == "admin" and self.is_admin: # Vérifier si admin ici aussi
        self.content_panel.add_component(AdminPanel())
    else:
        # Rediriger vers landing si la page demandée n'est pas accessible
        if page_name == "admin" and not self.is_admin:
             print("Accès non autorisé au panneau admin. Redirection vers la page d'accueil.")
        elif page_name == "profile" and not self.user:
             print("Accès non autorisé au profil. Redirection vers login.")
             self.load_page("login") # Rediriger vers login si profil demandé sans être connecté
             return # Eviter de charger Landing en plus
        else:
             print(f"Tentative de chargement de page '{page_name}' inconnue. Redirection vers la page d'accueil.")
        self.content_panel.add_component(Landing()) # Fallback sur landing

  def terms_of_service_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.load_page("terms")

  def legal_information_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.load_page("legal")

  def private_policy_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.load_page("private")

  def cookies_policy_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.load_page("cookies")

  def landing_link_click(self, **event_args):
    self.load_page("landing")

  def goodies_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.load_page("goodies")

    
  def teas_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.load_page("teas")

  def login_link_click(self, **event_args):
     if not self.user:
       self.load_page("login")

  def signup_link_click(self, **event_args):
    if not self.user:
        self.load_page("signup")
  
  def logout_link_click(self, **event_args):
    """Handles the click of the logout link."""
    if self.user: # Vérifier si l'utilisateur est bien connecté
        try:
            anvil.server.call('logout_user')
            Notification("Vous avez été déconnecté.", style="info").show()
            # Recharger le formulaire principal pour refléter l'état déconnecté
            open_form('MainForm')
        except Exception as e:
            Notification(f"Erreur lors de la déconnexion: {e}", style="danger").show()

  def profile_link_click(self, **event_args):
    """Handles the click of the profile link."""
    if self.user:
        self.load_page("profile")

  def admin_link_click(self, **event_args):
    """Handles the click of the admin link."""
    if self.is_admin:
        self.load_page("admin")

  def cart_indicator_click(self, **event_args):
      """Gère le clic sur l'indicateur du panier pour charger la page panier."""
      if self.user:
          print("Chargement page panier...")
          # Décommentez ceci lorsque CartPage.py existe
          # self.load_page("cart") 
          pass # Ne rien faire tant que la page n'existe pas


