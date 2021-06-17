import requests


class Postman(object):
    params_get = {}
    params_post = {}
    base_url = ""

    def __init__(self):
        self.params_get = {
            "key": "gulugulugulu",
            "branch": "BANJARMASIN",
            "category": "CCTV"
        }
        self.params_post = {
            "key": "gulugulugulu"
        }
        self.base_url = "http://localhost:5001"

    def set_base_url(self, base_url: str):
        self.base_url = base_url

    def set_param_post(self, params: dict):
        self.params_post = params

    def set_param_get(self, params: dict):
        self.params_get = params

    def get_ip_list(self) -> list:
        # {{url}}/api/v1/general-ip?branch=BANJARMASIN&category=cctv

        url = f"{self.base_url}/api/v1/general-ip"
        x = requests.get(url, params=self.params_get, timeout=2.50)
        if x.status_code == 200:
            json_response = x.json()
            return json_response["data"]
        else:
            return []

    def post_ip_status(self, cctv_list: list, code: int) -> str:
        # {{url}}/api/v1/general-ip-state?key=example
        url = f"{self.base_url}/api/v1/general-ip-state?key=example"
        body = {
            "ip_addresses": cctv_list,
            "ping_code": code,
            "category": "CCTV"
        }
        x = requests.post(url, json=body, params=self.params_post)
        if x.status_code == 200:
            return x.text
        else:
            return "Error"
