from google.ads.googleads.client import GoogleAdsClient
import google_auth_oauthlib
from keyword_planner.env import parse_env
from keyword_planner.oauth import authenticate_oauth_in_browser


def main():
    env = parse_env()
    credentials = authenticate_oauth_in_browser(env)
    print(credentials.__dict__)
    client = GoogleAdsClient.load_from_dict({
        # This is a convinience option to make protobuf easier to work with at the cost
        # of some performance
        # https://developers.google.com/google-ads/api/docs/client-libs/python/protobuf-messages#use_cases_for_proto-plus_and_protobuf_messages
        'use_proto_plus': True,
        'developer_token': env.GOOGLE_ADS_DEV_TOKEN,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'refresh_token': credentials.refresh_token
    })


if __name__ == '__main__':
    main()
