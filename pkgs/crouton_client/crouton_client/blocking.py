import requests as r
import logging
from .UUID import UUIDGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CroutonClient:
    def __init__(self, API_ROOT, ACCESS_STRING = None):
        self.API_ROOT = API_ROOT
        self.ACCESS_STRING = ACCESS_STRING


    def api_get_call(self, resource: str, item_id: str = None, filter_key: str = None, filter_value: str = None):
        url = self.API_ROOT + resource

        # Add the item_id if provided (for specific resource requests)
        if item_id:
            url += f'/{item_id}'
            
            # If item_id is present, just add the access string
            if self.ACCESS_STRING:
                url += f"/<token={self.ACCESS_STRING.strip('?')}>"
            else:
                url += ""
        else:
            # If item_id is not present, add the filters and then the access string
            query_params = {}

            if filter_key and filter_value:
                query_params[filter_key] = filter_value  

            # Construct the query string from the dictionary (filters only)
            query_string = ":".join([f"{key}>{value}" for key, value in query_params.items()])

            # Append the access string with a slash if it exists
            if self.ACCESS_STRING:
                if query_string:
                    query_string += f"/<token={self.ACCESS_STRING.strip('?')}>"
                else:
                    query_string = f"/<token={self.ACCESS_STRING.strip('?')}>"
            else:
                # If no access token, leave the query string as is (just the filters)
                pass
            
            # Add the query string to the URL if it's not empty
            if query_string:
                url += "/?query=" + query_string


        # Perform the GET request
        res = r.get(url)
        if res.status_code == 200:
            return res.json()
        else:
            # logger.error(f"GET request failed with status {res.status_code}: {res.json()}")
            raise ValueError(res.status_code)


    def api_post_call(self, resource: str, data_obj: dict):
        if 'id' not in data_obj:
            data_obj.update({'id': UUIDGenerator().create()})
        
        url = self.API_ROOT + resource

        # Add the access string if it's present
        if self.ACCESS_STRING:
            url += f"/<token={self.ACCESS_STRING.strip('?')}>"
        else:
            pass

        res = r.post(url, json=data_obj)

        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"POST request failed with status {res.status_code}: {res.json()}")
            raise ValueError(res.status_code)


    def api_put_call(self, resource: str, data_obj: dict, item_id: str):
        url = self.API_ROOT + resource

        if item_id:
            url += f'/{item_id}'
        
        # Append the access string if it's present
        if self.ACCESS_STRING:
            url += f"/<token={self.ACCESS_STRING.strip('?')}>"
        else:
            pass
        
        # Perform the PUT request with the constructed URL
        res = r.put(url, json=data_obj)

        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"PUT request failed with status {res.status_code}: {res.json()}")
            raise ValueError(res.status_code)

    def api_delete_call(self, resource: str, item_id: str = None):
        url = self.API_ROOT + resource
            
        if item_id:
            url += f'/{item_id}'
        # Append the access string if it's present
        if self.ACCESS_STRING:
            url += f"/<token={self.ACCESS_STRING.strip('?')}>"
        
        # Perform the DELETE request with the constructed URL
        res = r.delete(url)
            
        # Check if the request was successful
        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"DELETE request failed with status {res.status_code}: {res.json()}")
            raise ValueError(res.status_code)
