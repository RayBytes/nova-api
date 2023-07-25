from typing import Union, Optional

class Request:
    def __init__(self,
        method: str,
        url: str,
        json_payload: Optional[Union[dict, list]]=None,
        headers: dict=None
    ):
        self.method = method
        self.url = url
        self.json = json_payload
        self.headers = headers or {}
