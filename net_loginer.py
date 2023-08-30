#!/usr/bin/env python

import sys
import psutil
import ddddocr
import onnxruntime
import requests
import json
from io import BytesIO
from urllib.parse import urlparse, parse_qs

NET_AUTH_BASEURL = "https://net-auth.shanghaitech.edu.cn:19008"

class NetAuthenticator:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.session = requests.Session()

    def get_ip_address(self, interface):
        network_interfaces = psutil.net_if_addrs()

        if interface in network_interfaces:
            ipv4_address = network_interfaces[interface][0].address
            return ipv4_address
        else:
            print("Error getting IP address for network interface: " + interface)
            sys.exit(1)

    def load_config(self):
        try:
            with open(self.config_file, 'r') as config_file:
                config_data = json.load(config_file)
                self.user_id = config_data["id"]
                self.password = config_data["password"]
                self.interface = config_data["interface"]
                print("User ID:", self.user_id)
                print("Password:", self.password)
                print("Interface:", self.interface)

        except FileNotFoundError:
            print(f"Config file not found. Please create config.json by copying config.json.example.")
            sys.exit(1)

    def get_ip_and_verify_url(self):
        self.ip_address = self.get_ip_address(self.interface)
        
        if not self.ip_address:
            print(f"No IP address found for interface {self.interface}.")
            sys.exit(1)

        print(f"IP address of {self.interface}: {self.ip_address}")

        self.verify_url = f"{NET_AUTH_BASEURL}/portal?uaddress={self.ip_address}&ac-ip=0"
        print("Verify URL:", self.verify_url)

    def get_push_page_id_and_ssid(self):

        redirected_verify_url = self.session.get(self.verify_url, allow_redirects=True).url
        parsed_redirected_url = urlparse(self.session.get(redirected_verify_url).url)
        query_params = parse_qs(parsed_redirected_url.query)

        self.push_page_id = query_params.get("pushPageId", [None])[0]
        self.ssid = query_params.get("ssid", [None])[0]

        print("pushPageId:", self.push_page_id)
        print("ssid:", self.ssid)

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
        self.get_ip_and_verify_url()
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

if __name__ == "__main__":
    authenticator = NetAuthenticator()
    authenticator.perform_login()
