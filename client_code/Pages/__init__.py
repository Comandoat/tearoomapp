import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
# This is a package.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from .. import Package1


class SharedStateManager:
    def __init__(self):
        self._state = {
          "user": "Boris A",
          "cart": []
        }
        self._listeners = []

    def get(self, key):
        return self._state.get(key)

    def set(self, key, value):
        self._state[key] = value
        self._notify()

    def _notify(self):
        for callback in self._listeners:
            callback()

    def register(self, callback):
        self._listeners.append(callback)

    def unregister(self, callback):
        self._listeners.remove(callback)

    """Cart Management"""

    def add_to_cart(self, item):
        self._state["cart"].append(item)
        self._notify()

    def get_cart(self):
        return self._state["cart"]

state = SharedStateManager()
