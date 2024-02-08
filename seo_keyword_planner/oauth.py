import google_auth_oauthlib
from google.oauth2.credentials import Credentials
from seo_keyword_planner.env import Environment


def authenticate_oauth_in_browser(env: Environment) -> Credentials:
    return google_auth_oauthlib.get_user_credentials(
        scopes=["https://www.googleapis.com/auth/adwords"],
        client_id=env.OAUTH_CLIENT_ID,
        client_secret=env.OAUTH_CLIENT_SECRET
    )
