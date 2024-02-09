from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from seo_keyword_planner.models.base import BaseModel

engine = create_engine('sqlite:///database.sqlite', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

BaseModel.metadata.create_all(engine)

