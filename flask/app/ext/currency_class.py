import requests

class currency_class:
    def __init__(self,api_key):
        self.api_url = 'https://openexchangerates.org/api/latest.json?app_id='+str(api_key)

    def get_rates(self):
        current_rates = requests.get(self.api_url).json()
        return dict(current_rates['rates'])