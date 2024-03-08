import pathlib

import joblib
from google.ads.googleads.v15.resources.types.geo_target_constant import (
    GeoTargetConstant,
)

from google.ads.googleads.v15.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v15.services.types.google_ads_service import (
    SearchGoogleAdsRequest,
)
from whaaaaat import prompt, print_json

from seo_keyword_planner.oauth import ClientWithCustomerId


def _query_geo_target_by_name(
    client: ClientWithCustomerId, query: str
) -> list[GeoTargetConstant]:
    service: GoogleAdsServiceClient = client.client.get_service("GoogleAdsService")
    request: SearchGoogleAdsRequest = client.client.get_type("SearchGoogleAdsRequest")
    request.customer_id = client.customer_id

    # Simple case-insensitive match with a regex
    # Syntax: https://github.com/google/re2/wiki/Syntax?sjid=3580655635557203793-SA
    regexp = f"(?i)({query})"
    request.query = f"""
            SELECT geo_target_constant.canonical_name, geo_target_constant.resource_name
            FROM geo_target_constant
            WHERE geo_target_constant.name REGEXP_MATCH '{regexp}'"""

    response = service.search(request)
    return [r.geo_target_constant for r in response]


def _prompt_geo_targets(
    targets: list[GeoTargetConstant], query: str
) -> GeoTargetConstant:
    choices = [target.canonical_name for target in targets]
    questions = {
        "type": "list",
        "name": "geo_targets",
        "message": f"Multiple locations found for query '{query}'. Please select the one you'd like to use. ",
        "choices": choices,
    }

    answers = prompt([questions])
    print_json(answers)
    selected = answers["geo_targets"]
    selected_index = choices.index(selected)
    return targets[selected_index]


geo_target_memory = joblib.Memory(
    pathlib.Path(__file__).parent.parent / ".cache" / "geo_target"
)


@geo_target_memory.cache(ignore=["client"])
def find_geo_target(client: ClientWithCustomerId, query: str) -> GeoTargetConstant:
    found = _query_geo_target_by_name(client, query)
    if len(found) == 0:
        raise ValueError(
            f"No target found with name {query}. "
            f"Please consult https://developers.google.com/google-ads/api/data/geotargets for the complete list"
        )
    if len(found) == 1:
        print(f"Selected geo target: {found[0].canonical_name}")
        return found[0]
    return _prompt_geo_targets(found, query)
