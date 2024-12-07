import requests
from django.conf import settings

class UserAuthService:
    BASE_URL = "http://127.0.0.1:8000/auth"  # Ensure this points to 'http://127.0.0.1:8000/auth/'

    @staticmethod
    def get_user_profile(auth_token):
        """
        Fetch the authenticated user's profile from the user management API using JWT token.
        """
        try:
            url = f"{UserAuthService.BASE_URL}/profile/"
            headers = {
                'Authorization': f'Bearer {auth_token}',  # Attach the token here
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error if status is not 200
            return response.json()
        except requests.exceptions.RequestException as e:
            # Log error or handle it as needed
            return {"error": str(e)}
