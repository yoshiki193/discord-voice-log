from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///opt/data')

Base = declarative_base()

SessionClass = sessionmaker(engine)