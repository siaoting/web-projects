# import inside your project
from nutritionix.nutritionix import NutritionixClient

class Nutrition:
    def __init__(self, APP_ID = '', API_KEY = ''):
        self.nutritionix = NutritionixClient(
            application_id=APP_ID,
            api_key=API_KEY
        )
    def getCals(self, food_item):
        results=self.nutritionix.search(q=food_item, limit=50, offset=0, search_nutrient='calories')['results']
        cals = [result['nutrient_value'] for result in results if result['nutrient_value'] is not None]
        return int(sum(cals)/len(cals)) if len(cals) > 0 else -1
