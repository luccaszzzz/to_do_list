import requests
import json
from django.conf import settings


class APIService:
    BASE_URL = settings.API_BASE_URL

    @staticmethod
    def _get_headers(token=None):
        headers = {
            "Content-Type": "application/json",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    @staticmethod
    def register_user(user_data):
        url = f"{APIService.BASE_URL}api/registro/"
        try:
            print(f"Enviando registro para: {url}")
            print(f"Dados: {json.dumps(user_data, indent=2)}")
            response = requests.post(
                url, json=user_data, headers=APIService._get_headers()
            )
            print(f"Status: {response.status_code}")
            print(f"Resposta: {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return None

    @staticmethod
    def login_user(credentials):
        url = f"{APIService.BASE_URL}api/login/"
        try:
            print(f"Enviando login para: {url}")
            print(f"Credenciais: {json.dumps(credentials, indent=2)}")
            response = requests.post(
                url, json=credentials, headers=APIService._get_headers()
            )
            print(f"Status: {response.status_code}")
            print(f"Resposta: {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return None

    @staticmethod
    def refresh_token(refresh_token):
        url = f"{APIService.BASE_URL}api/refresh/"
        try:
            data = {"refresh": refresh_token}
            response = requests.post(url, json=data, headers=APIService._get_headers())
            return response
        except requests.exceptions.RequestException as e:
            return None

    @staticmethod
    def get_user_profile(access_token, user_id=None):
        if user_id:
            url = f"{APIService.BASE_URL}api/usuarios/{user_id}/"
        else:
            url = f"{APIService.BASE_URL}api/usuarios/"

        try:
            response = requests.get(url, headers=APIService._get_headers(access_token))
            return response
        except requests.exceptions.RequestException as e:
            return None

    @staticmethod
    def update_user(access_token, user_id, user_data):
        url = f"{APIService.BASE_URL}api/usuarios/{user_id}/"
        try:
            response = requests.put(
                url, json=user_data, headers=APIService._get_headers(access_token)
            )
            return response
        except requests.exceptions.RequestException as e:
            return None

    @staticmethod
    def delete_user(access_token, user_id):
        url = f"{APIService.BASE_URL}api/usuarios/{user_id}/"
        try:
            response = requests.delete(
                url, headers=APIService._get_headers(access_token)
            )
            return response
        except requests.exceptions.RequestException as e:
            return None
