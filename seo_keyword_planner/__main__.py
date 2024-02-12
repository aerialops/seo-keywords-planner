from google.ads.googleads.v15.services.services.keyword_plan_idea_service import (
    KeywordPlanIdeaServiceClient,
)
from google.ads.googleads.v15.services.types.keyword_plan_idea_service import (
    GenerateKeywordIdeasRequest,
)
from google.ads.googleads.v15.enums.types.keyword_plan_network import (
    KeywordPlanNetworkEnum,
)

from seo_keyword_planner.database import session
from seo_keyword_planner.env import parse_env
from seo_keyword_planner.models.keyword_idea import KeywordIdea
from seo_keyword_planner.oauth import load_client_or_prompt_login
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--keywords",
        help="A Keyword or phrase to generate ideas from. For example: startup law.",
    )
    parser.add_argument(
        "--url",
        help="A specific url to generate ideas from. For example: www.example.com/cars.",
    )

    return parser.parse_args()


def main():
    env = parse_env()
    args = parse_args()

    client = load_client_or_prompt_login(env)
    print(f"Logged in as {client.customer_id}")

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
    # TODO: select geographic target (defaults to US)
    request.keyword_plan_network = (
        KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
    )

    # Copied from https://developers.google.com/google-ads/api/docs/keyword-planning/generate-keyword-ideas#python
    # To generate keyword ideas with only a page_url and no keywords we need
    # to initialize a UrlSeed object with the page_url as the "url" field.
    if not args.keywords and args.url:
        request.url_seed.url = args.url

    # To generate keyword ideas with only a list of keywords and no page_url
    # we need to initialize a KeywordSeed object and set the "keywords" field
    # to be a list of StringValue objects.
    if args.keywords and not args.url:
        request.keyword_seed.keywords.extend(args.keywords.split(" "))

    # To generate keyword ideas using both a list of keywords and a page_url we
    # need to initialize a KeywordAndUrlSeed object, setting both the "url" and
    # "keywords" fields.
    if args.keywords and args.url:
        request.keyword_and_url_seed.url = args.url
        request.keyword_and_url_seed.keywords.extend(args.keywords)

    print("Fetching Keyword Ideas...")

    response = service.generate_keyword_ideas(request)
    ideas = [
        KeywordIdea(
            # Storing all possible information
            keyword=idea.text,
            original_keywords=args.keywords,
            original_url=args.url,
            competition=idea.keyword_idea_metrics.competition.name,
            competition_index=idea.keyword_idea_metrics.competition_index,
            low_top_of_page_bid_micros=idea.keyword_idea_metrics.low_top_of_page_bid_micros,
            high_top_of_page_bid_micros=idea.keyword_idea_metrics.high_top_of_page_bid_micros,
            average_cpc_micros=idea.keyword_idea_metrics.average_cpc_micros,
            close_variants=", ".join(idea.close_variants),
            concepts=", ".join(
                (
                    f"{concept.concept_group}/{concept.name}"
                    for concept in idea.keyword_annotations.concepts
                )
            ),
        )
        for idea in response
    ]
    session.add_all(ideas)
    session.commit()
    print(f"Stored {len(ideas)} ideas")


if __name__ == "__main__":
    main()
