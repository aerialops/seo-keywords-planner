from typing import Optional
from sqlalchemy import DateTime, func
from sqlalchemy.orm import mapped_column, Mapped
from seo_keyword_planner.models.base import BaseDbModel


class KeywordIdea(BaseDbModel):
    __tablename__ = "keyword_idea"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str]

    original_keywords: Mapped[Optional[str]]
    original_url: Mapped[Optional[str]]
    query_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    competition: Mapped[Optional[int]]
    competition_index: Mapped[Optional[int]]
    avg_monthly_searches: Mapped[Optional[int]]

    low_top_of_page_bid_micros: Mapped[Optional[int]]
    high_top_of_page_bid_micros: Mapped[Optional[int]]
    average_cpc_micros: Mapped[Optional[int]]

    close_variants: Mapped[Optional[str]]
    concepts: Mapped[Optional[str]]
    is_brand: Mapped[Optional[bool]]

    three_month_change_percent: Mapped[Optional[float]]
    year_change_percent: Mapped[Optional[float]]
