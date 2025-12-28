from delta_sdk.utils import logging
import aiohttp
import asyncio
import json



def retry_async_connection(max_retries=1, delay=1, exceptions=(Exception,)):
    def wrapper(func):
        async def inner_wrapper(*args, **kwargs):
            retries_left = max_retries
            while retries_left > 0:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries_left -= 1
                    logging.error(f"Exception: {type(e).__name__} - {e}, Retries left: {retries_left}")
                    if retries_left > 0:
                        await asyncio.sleep(delay)
            raise RuntimeError(f"Failed after {max_retries} attempts")
        return inner_wrapper
    return wrapper

class AsyncHTTPClient:
    def __init__(self, base_url, headers=None, max_retries=1, retry_delay=1):
        self.base_url = base_url
        self.headers = headers or {}
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def close_session(self):
        if self.session:
            await self.session.close()

    @retry_async_connection(max_retries=4, delay=1, exceptions=(aiohttp.ClientConnectionError, aiohttp.ClientError, aiohttp.ClientResponseError))
    async def _request(self, method, endpoint, data=None, json=None, headers=None):
        full_url =  f"{self.base_url}{endpoint}"
        headers = headers or self.headers
        async with self.session.request(method, full_url, data=data, json=json, headers=headers,ssl=False) as response:
            response_status = response.status
            response_text = await response.text()
            # logging.info(f"Response Status: {response_status}")
            if not response_status == 200:
                raise aiohttp.ClientError(f'Response Status: {response_status}, Response Error: {response_text}' )
            # response_data = json.loads(response_text)
            return response_text

    async def post(self, url, data=None, json=None, headers=None):
        return await self._request('POST', url, data=data, json=json, headers=headers)

    async def get(self, url, headers=None):
        return await self._request('GET', url, headers=headers)