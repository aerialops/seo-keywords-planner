import json
from typing import Optional

from google.auth.exceptions import GoogleAuthError
import google_auth_oauthlib
import keyring
from google.ads.googleads.client import GoogleAdsClient
from pydantic import BaseModel
from whaaaaat import prompt, print_json
from google.ads.googleads.v15.services.services.customer_service import (
    CustomerServiceClient,
)
from google.oauth2.credentials import Credentials
from seo_keyword_planner.env import Environment

SERVICE_NAME = "seo-keyword-planner"


class StoredCredentials(BaseModel):
    refresh_token: str
    customer_id: str


class ClientWithCustomerId(BaseModel):
    customer_id: str
    client: GoogleAdsClient

    class Config:
        arbitrary_types_allowed = True


def authenticate_oauth_in_browser(env: Environment) -> Credentials:
    return google_auth_oauthlib.get_user_credentials(
        scopes=["https://www.googleapis.com/auth/adwords"],
        client_id=env.OAUTH_CLIENT_ID,
        client_secret=env.OAUTH_CLIENT_SECRET,
    )


def find_customer_id(client: GoogleAdsClient) -> str:
    service: CustomerServiceClient = client.get_service("CustomerService")
    customers = service.list_accessible_customers().resource_names
    customer_ids = [
        service.parse_customer_path(customer_resource)["customer_id"]
        for customer_resource in customers
    ]
    if len(customer_ids) == 1:
        return customer_ids[0]

    questions = [
        {
            "type": "list",
            "name": "customer_id",
            "message": "Multiple customers found for this account. Please select the one you'd like to use",
            "choices": customer_ids,
        },
    ]
    answers = prompt(questions)
    print_json(answers)
    return answers["customer_id"]


def create_client(env: Environment, refresh_token: str) -> GoogleAdsClient:
    return GoogleAdsClient.load_from_dict(
        {
            # This is a convenience option to make protobuf easier to work with at the cost
            # of some performance
            # https://developers.google.com/google-ads/api/docs/client-libs/python/protobuf-messages#use_cases_for_proto-plus_and_protobuf_messages
            "use_proto_plus": True,
            "developer_token": env.GOOGLE_ADS_DEV_TOKEN,
            "client_id": env.OAUTH_CLIENT_ID,
            "client_secret": env.OAUTH_CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
    )


def try_load_from_storage(env: Environment) -> Optional[ClientWithCustomerId]:
    stored_json = keyring.get_password(SERVICE_NAME, env.OAUTH_CLIENT_ID)

    try:
        stored_token = StoredCredentials.model_validate_json(stored_json)
        return ClientWithCustomerId(customer_id=stored_token.customer_id,
                                    client=create_client(env, stored_token.refresh_token))
    except Exception:
        return None


def load_client_or_prompt_login(env: Environment) -> ClientWithCustomerId:
    stored_client = try_load_from_storage(env)

    if stored_client:
        return stored_client

    credentials = authenticate_oauth_in_browser(env)
    client = create_client(env, credentials.refresh_token)
    customer_id = find_customer_id(client)

    keyring.set_password(SERVICE_NAME, env.OAUTH_CLIENT_ID, StoredCredentials(
        customer_id=customer_id,
        refresh_token=credentials.refresh_token,
    ).model_dump_json())
    return ClientWithCustomerId(customer_id=customer_id, client=client)
