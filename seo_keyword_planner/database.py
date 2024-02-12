from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from seo_keyword_planner.models.base import BaseDbModel

engine = create_engine("sqlite:///database.sqlite", echo=False)

Session = sessionmaker(bind=engine)
session = Session()

BaseDbModel.metadata.create_all(engine)
