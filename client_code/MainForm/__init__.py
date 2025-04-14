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

class MainForm(MainFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.load_page("landing")

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
    elif page_name == "signup":
      signup_form = SignUpForm()
      signup_form.role = "custom-wide"
      self.content_panel.add_component(signup_form)
    elif page_name == "login":
      login_form = LogInForm()
      login_form.role = "custom-wide"
      self.content_panel.add_component(login_form)


  
  
  def terms_of_service_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    get_open_form().load_page("terms")


  def legal_information_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    get_open_form().load_page("legal")


  def private_policy_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    get_open_form().load_page("private")


  def cookies_policy_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    get_open_form().load_page("cookies")

  def landing_link_click(self, **event_args):
    get_open_form().load_page("landing")

  def goodies_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    get_open_form().load_page("goodies")

    
  def teas_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    get_open_form().load_page("teas")

  def login_link_click(self, **event_args):
     get_open_form().load_page("login")
  


