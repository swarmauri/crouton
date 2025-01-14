import aiohttp
import requests as r
import logging
from urllib.parse import urlencode
from typing import Optional, Any, Dict
from .UUID import UUIDGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CroutonClient:
    def __init__(self, API_ROOT: str, ACCESS_STRING: Optional[str] = None):
        self.API_ROOT = API_ROOT.rstrip('/')  # Ensure no trailing slash
        self.ACCESS_STRING = ACCESS_STRING

    def _build_url(self, resource: str, item_id: Optional[str] = None, query_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Helper method to construct the URL with resource, item_id, and query parameters.
        """
        url = f"{self.API_ROOT}/{resource.strip('/')}"
        
        # Add item ID if provided
        if item_id:
            url += f"/{item_id}"

        # Add query parameters
        if query_params:
            query_string = urlencode(query_params)
            url += f"?{query_string}"

        # Add access string as a query parameter
        if self.ACCESS_STRING:
            separator = '&' if '?' in url else '?'
            url += f"{separator}token={self.ACCESS_STRING.strip('?')}"

        return url

    def get(self, resource: str, item_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> dict:
        """
        Perform a synchronous GET request with optional filters and an item ID.
        """
        url = self._build_url(resource, item_id, filters)

        logger.info(f"Performing synchronous GET request to {url}")
        res = r.get(url)
        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"GET request failed with status {res.status_code}: {res.text}")
            raise ValueError(f"GET request failed with status {res.status_code}: {res.text}")

    async def aget(self, resource: str, item_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform an asynchronous GET request with optional filters and an item ID.
        """
        url = self._build_url(resource, item_id, filters)

        logger.info(f"Performing asynchronous GET request to {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                if res.status == 200:
                    return await res.json()
                else:
                    error_content = await res.text()
                    logger.error(f"GET request failed with status {res.status}: {error_content}")
                    raise ValueError(f"GET request failed with status {res.status}: {error_content}")

    def post(self, resource: str, data_obj: dict) -> dict:
        """
        Perform a synchronous POST request to create a resource.
        """
        if 'id' not in data_obj:
            data_obj['id'] = UUIDGenerator().create()

        url = self._build_url(resource)

        logger.info(f"Performing synchronous POST request to {url} with data {data_obj}")
        res = r.post(url, json=data_obj)
        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"POST request failed with status {res.status_code}: {res.text}")
            raise ValueError(f"POST request failed with status {res.status_code}: {res.text}")

    async def apost(self, resource: str, data_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform an asynchronous POST request to create a resource.
        """
        if 'id' not in data_obj:
            data_obj['id'] = UUIDGenerator().create()

        url = self._build_url(resource)

        logger.info(f"Performing asynchronous POST request to {url} with data {data_obj}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data_obj) as res:
                if res.status == 200:
                    return await res.json()
                else:
                    error_content = await res.text()
                    logger.error(f"POST request failed with status {res.status}: {error_content}")
                    raise ValueError(f"POST request failed with status {res.status}: {error_content}")

    def put(self, resource: str, data_obj: dict, item_id: str) -> dict:
        """
        Perform a synchronous PUT request to update a resource.
        """
        url = self._build_url(resource, item_id)

        logger.info(f"Performing synchronous PUT request to {url} with data {data_obj}")
        res = r.put(url, json=data_obj)
        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"PUT request failed with status {res.status_code}: {res.text}")
            raise ValueError(f"PUT request failed with status {res.status_code}: {res.text}")

    async def aput(self, resource: str, data_obj: Dict[str, Any], item_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform an asynchronous PUT request to update a resource.
        """
        url = self._build_url(resource, item_id)

        logger.info(f"Performing asynchronous PUT request to {url} with data {data_obj}")
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=data_obj) as res:
                if res.status == 200:
                    return await res.json()
                else:
                    error_content = await res.text()
                    logger.error(f"PUT request failed with status {res.status}: {error_content}")
                    raise ValueError(f"PUT request failed with status {res.status}: {error_content}")

    def delete(self, resource: str, item_id: Optional[str] = None) -> dict:
        """
        Perform a synchronous DELETE request to delete a resource.
        """
        url = self._build_url(resource, item_id)

        logger.info(f"Performing synchronous DELETE request to {url}")
        res = r.delete(url)
        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"DELETE request failed with status {res.status_code}: {res.text}")
            raise ValueError(f"DELETE request failed with status {res.status_code}: {res.text}")

    async def adelete(self, resource: str, item_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform an asynchronous DELETE request to delete a resource.
        """
        url = self._build_url(resource, item_id)

        logger.info(f"Performing asynchronous DELETE request to {url}")
        async with aiohttp.ClientSession() as session:
            async with session.delete(url) as res:
                if res.status == 200:
                    return await res.json()
                else:
                    error_content = await res.text()
                    logger.error(f"DELETE request failed with status {res.status}: {error_content}")
                    raise ValueError(f"DELETE request failed with status {res.status}: {error_content}")
