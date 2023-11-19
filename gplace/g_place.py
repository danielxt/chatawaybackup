import os
import requests
import random
from typing import List, Tuple


class GPlaceFinder:
    def __init__(
        self,
        url="https://places.googleapis.com/v1/places:searchText",
        gplaces_api_key=None,
    ) -> None:
        self.url = url
        self.gplaces_api_key = (
            gplaces_api_key
            if gplaces_api_key is not None
            else os.environ.get("GPLACES_API_KEY")
        )

    def query(self, query: str, num_return=2) -> Tuple[List[dict], List[dict]]:
        """Search for information about places or restaurants"""
        headers = {
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types,places.photos",
            "X-Goog-Api-Key": self.gplaces_api_key,
            "Content-Type": "application/json",
        }
        payload = {"textQuery": query}
        response = requests.post(self.url, headers=headers, json=payload)
        if response.status_code == 200:
            items = response.json()["places"]
            items = random.sample(items, min(num_return, len(items)))
            exc = []
            non_exc = []
            for item in items:
                i = {
                    "name": item["displayName"]["text"],
                    "address": item["formattedAddress"],
                    "location": item["location"],
                    "photo": item.get("photos", [{}])[0].get("name", "")
                }
                try:
                    for typ in item["types"]:
                        if typ == "restaurant" or typ == "food":
                            exc.append(i)
                            break
                        elif typ == "point_of_interest" or typ == "establishment":
                            non_exc.append(i)
                            break
                except KeyError:
                    print(f"No type key found")
            return exc, non_exc
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return [], False
