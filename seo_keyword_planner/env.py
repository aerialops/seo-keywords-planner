from dotenv import dotenv_values
from pydantic import BaseModel


class Environment(BaseModel):
    OAUTH_CLIENT_ID: str
    OAUTH_CLIENT_SECRET: str
    GOOGLE_ADS_DEV_TOKEN: str
    GOOGLE_ADS_CUSTOMER_ID: str


def parse_env() -> Environment:
    env_dict = dotenv_values(".env.local")
    return Environment.parse_obj(env_dict)
