import requests
from constants import IMAGE_START_PARAMS

URL = "https://www.googleapis.com/customsearch/v1"


class ImageSearcher:
    def __init__(self):
        self.start_params = IMAGE_START_PARAMS

    def find_image(self, text):
        querystring = {
            "searchType": "image",
            "q": text
        }
        querystring.update(self.start_params)
        try:
            response = requests.get(URL, params=querystring)

            json = response.json()
        except Exception as e:
            print(e)
            return []
        if json.get("items", 0):
            ans = [image["link"] for image in json["items"]]
            return ans

        print(json)
        return []
