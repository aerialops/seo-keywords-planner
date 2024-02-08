from google.ads.googleads.client import GoogleAdsClient

from google.ads.googleads.v15.services.services.google_ads_service import GoogleAdsServiceClient
from google.ads.googleads.v15.services.types.google_ads_service import SearchGoogleAdsRequest

from seo_keyword_planner.env import Environment


def query_geo_target_by_name(name: str, client: GoogleAdsClient, env: Environment):
    service: GoogleAdsServiceClient = client.get_service("GoogleAdsService")
    request: SearchGoogleAdsRequest = client.get_type("SearchGoogleAdsRequest")
    request.customer_id = env.GOOGLE_ADS_CUSTOMER_ID

    regexp = f'(?i)(^{name}$)'
    request.query = f"""
            SELECT geo_target_constant.name, geo_target_constant.resource_name
            FROM geo_target_constant
            WHERE geo_target_constant.name REGEXP_MATCH '{regexp}'"""

    response = list(service.search(request))
    print(f'Matched {len(response)} regions', [r.geo_target_constant.name for r in response])
    return [r.geo_target_constant.resource_name for r in response]