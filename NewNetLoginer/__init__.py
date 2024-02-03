#!/usr/bin/env python

import ddddocr
import json
import onnxruntime
import os
import psutil
import requests
import sys
from io import BytesIO
from dotenv import dotenv_values
from urllib.parse import urlparse, parse_qs

NET_AUTH_BASEURL = "https://net-auth.shanghaitech.edu.cn:19008"

class NetAuthenticator:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.session = requests.Session()

    def load_config(self):
        config = dotenv_values(".env")
        try:
            self.user_id = config['EGATE_ID']
            self.password = config["EGATE_PASSWORD"]
            self.interface = config["INTERFACE"]
        except KeyError:
            print(f"Environment not set. Please check if you have copied .env from .env.example!")
            sys.exit(1)
        print("User ID:", self.user_id)
        print("Password:", self.password)
        print("Interface:", self.interface)

    def get_ip_address(self):
        network_interfaces = psutil.net_if_addrs()

        if self.interface in network_interfaces:
            self.ip_address = network_interfaces[self.interface][0].address
            print(f"IP address of {self.interface}: {self.ip_address}")
        else:
            print("Error getting IP address for network interface: " + self.interface)
            sys.exit(1)

    def get_push_page_id_and_ssid(self):
        verify_url = f"{NET_AUTH_BASEURL}/portal?uaddress={self.ip_address}&ac-ip=0"
        print("Verify URL:", verify_url)
    
        redirected_verify = self.session.get(verify_url, allow_redirects=True)
        parsed_redirected_url = urlparse(redirected_verify.url)
        query_params = parse_qs(parsed_redirected_url.query)

        self.push_page_id = query_params.get("pushPageId", [None])[0]
        self.ssid = query_params.get("ssid", [None])[0]

        print("Get pushPageId:", self.push_page_id)
        print("Get ssid:", self.ssid)

    def get_verify_code(self):
        image_url = f"{NET_AUTH_BASEURL}/portalauth/verificationcode?uaddress={self.ip_address}"
        onnxruntime.set_default_logger_severity(3)

        response = self.session.get(image_url)
        img_bytes = BytesIO(response.content).read()

        ocr = ddddocr.DdddOcr()
        verify_code = ocr.classification(img_bytes)
        print("Verify code:", verify_code)
        return verify_code

    def perform_login(self):
        self.load_config()
        self.get_ip_address()
        self.get_push_page_id_and_ssid()
    
        login_data = {
            "userName": self.user_id,
            "userPass": self.password,
            "uaddress": self.ip_address,
            "validCode": self.get_verify_code(),
            "pushPageId": self.push_page_id,
            "ssid": self.ssid,
            "agreed": "1",
            "authType": "1"
        }

        login_response = self.session.post(f"{NET_AUTH_BASEURL}/portalauth/login", data=login_data)
        response_data = login_response.json()

        if response_data.get("success") == True:
            print("Successfully logged in")
        else:
            print("Login was not successful, please check manually")

def main():
    authenticator = NetAuthenticator()
    authenticator.perform_login()

if __name__ == "__main__":
    main()
