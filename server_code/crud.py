# Server module for handling product data (Teas, Goodies)
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_available_teas():
  """Retourne la liste des thés disponibles.
  Ajoute 'id' (Row ID) et 'type' au dictionnaire retourné pour chaque thé.
  """
  available_teas = []
  # Recherche les thés marqués comme disponibles
  for tea_row in app_tables.teas.search(is_available=True):
      tea_dict = dict(tea_row) # Convertit la ligne en dictionnaire
      tea_dict['id'] = tea_row.get_id() # Ajoute le Row ID sous la clé 'id'
      tea_dict['type'] = 'tea' # Ajoute le type de produit
      available_teas.append(tea_dict)
  return available_teas

@anvil.server.callable
def get_available_goodies():
  """Retourne la liste des goodies disponibles.
  Ajoute 'id' (Row ID) et 'type' au dictionnaire retourné pour chaque goodie.
  """
  available_goodies = []
  # Recherche les goodies marqués comme disponibles
  for goodie_row in app_tables.goodies.search(is_available=True):
      goodie_dict = dict(goodie_row) # Convertit la ligne en dictionnaire
      goodie_dict['id'] = goodie_row.get_id() # Ajoute le Row ID sous la clé 'id'
      goodie_dict['type'] = 'goodie' # Ajoute le type de produit
      available_goodies.append(goodie_dict)
  return available_goodies 