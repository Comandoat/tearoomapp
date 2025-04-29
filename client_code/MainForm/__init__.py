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

class MainForm(MainFormTemplate):
  def __init__(self, **properties):
    self.user = None # Stocker les infos utilisateur si connecté
    self.init_components(**properties)
    self.check_login_status() # Vérifier si l'utilisateur est déjà connecté
    if not self.user:
        # Si non connecté, charger la page d'accueil par défaut
        self.load_page("landing") 
    else:
        # Optionnel: Charger une page par défaut pour l'utilisateur connecté
        # Par exemple, la page de profil ou un tableau de bord
        self.load_page("profile") # Charge le profil par défaut si connecté

  def check_login_status(self):
    """Vérifie la session serveur et met à jour l'état et l'UI."""
    user_info = anvil.server.call('get_user_info')
    if user_info:
        self.user = user_info
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
    else:
        self.user = None
        # Mettre à jour l'UI pour l'état déconnecté
        if hasattr(self, 'login_link'): self.login_link.visible = True
        if hasattr(self, 'signup_link'): self.signup_link.visible = True
        if hasattr(self, 'logout_link'): self.logout_link.visible = False
        if hasattr(self, 'profile_link'): self.profile_link.visible = False
        if hasattr(self, 'welcome_label'): self.welcome_label.visible = False

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
    else:
        # Rediriger vers landing si la page demandée n'est pas accessible
        print(f"Tentative de chargement de page '{page_name}' non autorisée ou inconnue.")
        self.content_panel.add_component(Landing())
        # Ou afficher un message d'erreur
        # self.content_panel.add_component(Label(text="Page non trouvée ou accès non autorisé."))

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


