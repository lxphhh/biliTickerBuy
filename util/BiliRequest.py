import json
import loguru
import requests
from util.CookieManager import CookieManager


class BiliRequest:
    def __init__(
        self, headers=None, cookies=None, cookies_config_path=None, proxy=None
    ):
        self.session = requests.Session()
        self.session.proxies = proxy or {}
        self.cookieManager = CookieManager(cookies_config_path, cookies)
        self.headers = headers or {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": "",
            "referer": "https://show.bilibili.com/",
            "priority": "u=1, i",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        }

    def get(self, url, data=None, isJson=False):
        self.headers["cookie"] = self.cookieManager.get_cookies_str()
        if isJson:
            self.headers["Content-Type"] = "application/json"
            data = json.dumps(data)
        else:
            self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        response = self.session.get(url, data=data, headers=self.headers)
        response.raise_for_status()
        if response.json().get("msg", "") == "请先登录":
            self.headers["cookie"] = self.cookieManager.get_cookies_str_force()
            self.get(url, data)
        return response

    def post(self, url, data=None, isJson=False):
        self.headers["cookie"] = self.cookieManager.get_cookies_str()
        if isJson:
            self.headers["content-type"] = "application/json"
            data = json.dumps(data)
        else:
            self.headers["content-type"] = "application/x-www-form-urlencoded"
        response = self.session.post(url, data=data, headers=self.headers)
        response.raise_for_status()
        if response.json().get("msg", "") == "请先登录":
            self.headers["cookie"] = self.cookieManager.get_cookies_str_force()
            self.post(url, data)
        return response

    def get_request_name(self):
        try:
            if not self.cookieManager.have_cookies():
                loguru.logger.warning("获取用户名失败，请重新登录")
                return "未登录"
            result = self.get("https://api.bilibili.com/x/web-interface/nav").json()
            return result["data"]["uname"]
        except Exception as e:
            loguru.logger.exception(e)
            return "未登录"
