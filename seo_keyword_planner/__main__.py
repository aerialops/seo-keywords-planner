from typing import Optional

from google.ads.googleads.v15.services.services.keyword_plan_idea_service import (
    KeywordPlanIdeaServiceClient,
)
from google.ads.googleads.v15.services.types.keyword_plan_idea_service import (
    GenerateKeywordIdeasRequest,
    GenerateKeywordIdeaResult,
)
from google.ads.googleads.v15.enums.types.keyword_plan_network import (
    KeywordPlanNetworkEnum,
)

from seo_keyword_planner.database import session
from seo_keyword_planner.env import parse_env, Environment
from seo_keyword_planner.geo_target import find_geo_target
from seo_keyword_planner.models.keyword_idea import KeywordIdea
from seo_keyword_planner.oauth import (
    load_client_or_prompt_login,
    logout,
    ClientWithCustomerId,
)
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    command_subparsers = parser.add_subparsers(dest="command")
    fetch_parser = command_subparsers.add_parser("fetch")
    fetch_parser.add_argument(
        "--keywords",
        help="A Keyword or phrase to generate ideas from. For example: startup law.",
    )
    fetch_parser.add_argument(
        "--url",
        help="A specific url to generate ideas from. For example: www.example.com/cars.",
    )
    fetch_parser.add_argument(
        "--location",
        help="The name of a geographical location. For example: US, Seattle, Washington.",
        default="United States",
    )
    command_subparsers.add_parser("logout")

    return parser.parse_args()


def calc_change_percent(current: float, previous: float) -> float:
    return round((current - previous) / previous * 100, 2)


def enhance_keyword_idea(
    keyword: GenerateKeywordIdeaResult, keywords: Optional[str], url: Optional[str]
) -> KeywordIdea:
    monthly_searches = [
        month.monthly_searches
        for month in keyword.keyword_idea_metrics.monthly_search_volumes
        if month.monthly_searches
    ]
    avg_monthly_searches = (
        round(sum(monthly_searches) / len(monthly_searches), 2)
        if len(monthly_searches) >= 1
        else None
    )
    three_month_change_percent = (
        calc_change_percent(monthly_searches[-1], monthly_searches[-3])
        if len(monthly_searches) >= 3
        else None
    )
    year_change_percent = (
        calc_change_percent(monthly_searches[-1], monthly_searches[-12])
        if len(monthly_searches) >= 12
        else None
    )
    return KeywordIdea(
        # Storing all possible information
        keyword=keyword.text,
        original_keywords=keywords,
        original_url=url,
        competition=keyword.keyword_idea_metrics.competition.name,
        competition_index=keyword.keyword_idea_metrics.competition_index,
        low_top_of_page_bid_micros=keyword.keyword_idea_metrics.low_top_of_page_bid_micros,
        high_top_of_page_bid_micros=keyword.keyword_idea_metrics.high_top_of_page_bid_micros,
        average_cpc_micros=keyword.keyword_idea_metrics.average_cpc_micros,
        close_variants=", ".join(keyword.close_variants),
        concepts=", ".join(
            (
                f"{concept.concept_group}/{concept.name}"
                for concept in keyword.keyword_annotations.concepts
            )
        ),
        avg_monthly_searches=avg_monthly_searches,
        three_month_change_percent=three_month_change_percent,
        year_change_percent=year_change_percent,
    )


def fetch_keyword_ideas(
    client: ClientWithCustomerId,
    keywords: Optional[str],
    url: Optional[str],
    location: Optional[str],
) -> list[GenerateKeywordIdeaResult]:
    service: KeywordPlanIdeaServiceClient = client.client.get_service(
        "KeywordPlanIdeaService"
    )
    request: GenerateKeywordIdeasRequest = client.client.get_type(
        "GenerateKeywordIdeasRequest"
    )
    request.customer_id = client.customer_id
    # https://developers.google.com/google-ads/api/data/codes-formats#languages
    request.language = "languageConstants/1000"
    request.include_adult_keywords = False
    request.geo_target_constants = [find_geo_target(client, location).resource_name]
    request.keyword_plan_network = (
        KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
    )
    request.historical_metrics_options.include_average_cpc = True

    # Copied from https://developers.google.com/google-ads/api/docs/keyword-planning/generate-keyword-ideas#python
    # To generate keyword ideas with only a page_url and no keywords we need
    # to initialize a UrlSeed object with the page_url as the "url" field.
    if not keywords and url:
        request.url_seed.url = url

    # To generate keyword ideas with only a list of keywords and no page_url
    # we need to initialize a KeywordSeed object and set the "keywords" field
    # to be a list of StringValue objects.
    if keywords and not url:
        request.keyword_seed.keywords.extend(keywords.split(" "))

    # To generate keyword ideas using both a list of keywords and a page_url we
    # need to initialize a KeywordAndUrlSeed object, setting both the "url" and
    # "keywords" fields.
    if keywords and url:
        request.keyword_and_url_seed.url = url
        request.keyword_and_url_seed.keywords.extend(keywords)

    print("Fetching Keyword Ideas...")
    return list(service.generate_keyword_ideas(request))


def generate_and_insert_keyword_ideas(env: Environment, args):
    client = load_client_or_prompt_login(env)
    print(f"Logged in as {client.customer_id}")

    keyword_ideas = fetch_keyword_ideas(
        client, keywords=args.keywords, url=args.url, location=args.location
    )
    ideas = [
        enhance_keyword_idea(idea, keywords=args.keywords, url=args.url)
        for idea in keyword_ideas
    ]
    session.add_all(ideas)
    session.commit()
    print(f"Stored {len(ideas)} ideas")


def main():
    env = parse_env()
    args = parse_args()

    if args.command == "logout":
        logout(env)
        print("Logged out")
    else:
        generate_and_insert_keyword_ideas(env, args)


if __name__ == "__main__":
    main()
