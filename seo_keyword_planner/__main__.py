from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v15.services.services.keyword_plan_idea_service import KeywordPlanIdeaServiceClient
from google.ads.googleads.v15.services.types.keyword_plan_idea_service import GenerateKeywordIdeasRequest
from google.ads.googleads.v15.enums.types.keyword_plan_network import KeywordPlanNetworkEnum
from sqlalchemy import DateTime

from seo_keyword_planner.database import session
from seo_keyword_planner.env import parse_env
from seo_keyword_planner.geo_target import query_geo_target_by_name
from seo_keyword_planner.models.keyword_idea import KeywordIdea
from seo_keyword_planner.oauth import authenticate_oauth_in_browser
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", help="A Keyword or phrase to generate ideas from. For example: startup law.")
    parser.add_argument("--url", help="A specific url to generate ideas from. For example: www.example.com/cars.")
    parser.add_argument("--location", default='United States',
                        help="The human-readable name of the location to target. For example: United States, Seattle")

    return parser.parse_args()


def main():
    env = parse_env()
    args = parse_args()

    credentials = authenticate_oauth_in_browser(env)
    client = GoogleAdsClient.load_from_dict({
        # This is a convenience option to make protobuf easier to work with at the cost
        # of some performance
        # https://developers.google.com/google-ads/api/docs/client-libs/python/protobuf-messages#use_cases_for_proto-plus_and_protobuf_messages
        'use_proto_plus': True,
        'developer_token': env.GOOGLE_ADS_DEV_TOKEN,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'refresh_token': credentials.refresh_token
    })

    service: KeywordPlanIdeaServiceClient = client.get_service('KeywordPlanIdeaService')
    request: GenerateKeywordIdeasRequest = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = env.GOOGLE_ADS_CUSTOMER_ID
    # https://developers.google.com/google-ads/api/data/codes-formats#languages
    request.language = 'languageConstants/1000'
    request.include_adult_keywords = False
    request.geo_target_constants = query_geo_target_by_name(args.location, client, env)
    request.keyword_plan_network = KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH

    # Copied from https://developers.google.com/google-ads/api/docs/keyword-planning/generate-keyword-ideas#python
    # To generate keyword ideas with only a page_url and no keywords we need
    # to initialize a UrlSeed object with the page_url as the "url" field.
    if not args.keywords and args.url:
        request.url_seed.url = args.url

    # To generate keyword ideas with only a list of keywords and no page_url
    # we need to initialize a KeywordSeed object and set the "keywords" field
    # to be a list of StringValue objects.
    if args.keywords and not args.url:
        request.keyword_seed.keywords.extend(args.keywords.split(' '))

    # To generate keyword ideas using both a list of keywords and a page_url we
    # need to initialize a KeywordAndUrlSeed object, setting both the "url" and
    # "keywords" fields.
    if args.keywords and args.url:
        request.keyword_and_url_seed.url = args.url
        request.keyword_and_url_seed.keywords.extend(args.keywords)

    response = service.generate_keyword_ideas(request)
    session.add_all([KeywordIdea(
        # Storing all possible information
        keyword=idea.text,
        original_keywords=args.keywords,
        original_url=args.url,
        competition=idea.keyword_idea_metrics.competition.name,
        competition_index=idea.keyword_idea_metrics.competition_index,
        low_top_of_page_bid_micros=idea.keyword_idea_metrics.low_top_of_page_bid_micros,
        high_top_of_page_bid_micros=idea.keyword_idea_metrics.high_top_of_page_bid_micros,
        average_cpc_micros=idea.keyword_idea_metrics.average_cpc_micros,
        close_variants=', '.join(idea.close_variants),
        concepts=', '.join((f"{concept.concept_group}/{concept.name}" for concept in idea.keyword_annotations.concepts)),
    ) for idea in response])
    session.commit()


if __name__ == '__main__':
    main()
