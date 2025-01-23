import httpx
import logging
from urllib.parse import urlencode
from typing import Optional, Any, Dict
from .UUID import UUIDGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CroutonClient:
    def __init__(self, API_ROOT: str, ACCESS_STRING: Optional[str] = None, timeout: Optional[float] = 10.0):
        self.API_ROOT = API_ROOT.rstrip('/')  # Ensure no trailing slash
        self.ACCESS_STRING = ACCESS_STRING
        self.timeout = timeout

        # Initialize synchronous client
        self._sync_client = httpx.Client(timeout=self.timeout)

        # Initialize asynchronous client
        self._async_client = httpx.AsyncClient(timeout=self.timeout)

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
        try:
            res = self._sync_client.get(url)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"GET request failed with status {e.response.status_code}: {e.response.text}")
            raise ValueError(f"GET request failed with status {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise ValueError(f"An error occurred while requesting {e.request.url!r}: {e}") from e

    async def aget(self, resource: str, item_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform an asynchronous GET request with optional filters and an item ID.
        """
        url = self._build_url(resource, item_id, filters)

        logger.info(f"Performing asynchronous GET request to {url}")
        try:
            res = await self._async_client.get(url)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"GET request failed with status {e.response.status_code}: {e.response.text}")
            raise ValueError(f"GET request failed with status {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise ValueError(f"An error occurred while requesting {e.request.url!r}: {e}") from e

    def post(self, resource: str, data_obj: dict) -> dict:
        """
        Perform a synchronous POST request to create a resource.
        """
        if 'id' not in data_obj:
            data_obj['id'] = UUIDGenerator().create()

        url = self._build_url(resource)

        logger.info(f"Performing synchronous POST request to {url} with data {data_obj}")
        try:
            res = self._sync_client.post(url, json=data_obj)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"POST request failed with status {e.response.status_code}: {e.response.text}")
            raise ValueError(f"POST request failed with status {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise ValueError(f"An error occurred while requesting {e.request.url!r}: {e}") from e

    async def apost(self, resource: str, data_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform an asynchronous POST request to create a resource.
        """
        if 'id' not in data_obj:
            data_obj['id'] = UUIDGenerator().create()

        url = self._build_url(resource)

        logger.info(f"Performing asynchronous POST request to {url} with data {data_obj}")
        try:
            res = await self._async_client.post(url, json=data_obj)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"POST request failed with status {e.response.status_code}: {e.response.text}")
            raise ValueError(f"POST request failed with status {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise ValueError(f"An error occurred while requesting {e.request.url!r}: {e}") from e

    def put(self, resource: str, data_obj: dict, item_id: str) -> dict:
        """
        Perform a synchronous PUT request to update a resource.
        """
        url = self._build_url(resource, item_id)

        logger.info(f"Performing synchronous PUT request to {url} with data {data_obj}")
        try:
            res = self._sync_client.put(url, json=data_obj)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"PUT request failed with status {e.response.status_code}: {e.response.text}")
            raise ValueError(f"PUT request failed with status {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise ValueError(f"An error occurred while requesting {e.request.url!r}: {e}") from e

    async def aput(self, resource: str, data_obj: Dict[str, Any], item_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform an asynchronous PUT request to update a resource.
        """
        url = self._build_url(resource, item_id)

        logger.info(f"Performing asynchronous PUT request to {url} with data {data_obj}")
        try:
            res = await self._async_client.put(url, json=data_obj)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"PUT request failed with status {e.response.status_code}: {e.response.text}")
            raise ValueError(f"PUT request failed with status {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise ValueError(f"An error occurred while requesting {e.request.url!r}: {e}") from e

    def delete(self, resource: str, item_id: Optional[str] = None) -> dict:
        """
        Perform a synchronous DELETE request to delete a resource.
        """
        url = self._build_url(resource, item_id)

        logger.info(f"Performing synchronous DELETE request to {url}")
        try:
            res = self._sync_client.delete(url)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"DELETE request failed with status {e.response.status_code}: {e.response.text}")
            raise ValueError(f"DELETE request failed with status {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise ValueError(f"An error occurred while requesting {e.request.url!r}: {e}") from e

    async def adelete(self, resource: str, item_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform an asynchronous DELETE request to delete a resource.
        """
        url = self._build_url(resource, item_id)

        logger.info(f"Performing asynchronous DELETE request to {url}")
        try:
            res = await self._async_client.delete(url)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"DELETE request failed with status {e.response.status_code}: {e.response.text}")
            raise ValueError(f"DELETE request failed with status {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise ValueError(f"An error occurred while requesting {e.request.url!r}: {e}") from e

    def __del__(self):
        """
        Ensure that the clients are properly closed when the instance is destroyed.
        """
        try:
            self._sync_client.close()
        except Exception as e:
            logger.warning(f"Failed to close synchronous client: {e}")

    async def aclose(self):
        """
        Close the asynchronous client. Should be called when done with async operations.
        """
        await self._async_client.aclose()
