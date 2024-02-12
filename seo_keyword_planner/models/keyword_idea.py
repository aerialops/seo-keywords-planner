from typing import Optional
from sqlalchemy import DateTime, func
from sqlalchemy.orm import mapped_column, Mapped
from seo_keyword_planner.models.base import BaseDbModel


class KeywordIdea(BaseDbModel):
    __tablename__ = "idea"

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

    def __repr__(self):
        return (
            f"KeywordIdea(id={self.id}, "
            f"keyword={self.keyword}, "
            f"original_keywords={self.original_keywords}, "
            f"original_url={self.original_url}, "
            f"query_time={self.query_time}, "
            f"competition={self.competition}, "
            f"competition_index={self.competition_index}, "
            f"avg_monthly_searches={self.avg_monthly_searches}, "
            f"low_top_of_page_bid_micros={self.low_top_of_page_bid_micros}, "
            f"high_top_of_page_bid_micros={self.high_top_of_page_bid_micros}, "
            f"average_cpc_micros={self.average_cpc_micros}, "
            f"close_variants={self.close_variants}, "
            f"concepts={self.concepts})"
        )
