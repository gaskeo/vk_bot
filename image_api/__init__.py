import requests
from constants import IMAGE_HEADERS


URL = "https://rapidapi.p.rapidapi.com/api/Search/ImageSearchAPI"


class ImageSearcher:
    def __init__(self):
        self.headers = IMAGE_HEADERS

    def find_image(self, text):
        querystring = {"q": text,
                       "pageNumber": 1,
                       "pageSize": 10,
                       "autoCorrect": True,
                       "safeSearch": True}
        try:
            response: dict = requests.get(URL, headers=self.headers, params=querystring).json()
        except Exception as e:
            print(e)
            return []
        if response.get("value", 0):
            ans = [image["url"] for image in response["value"]]
            return ans

        print(response)
        return []