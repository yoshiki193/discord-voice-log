from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bot.db")
engine = create_engine(DATABASE_URL)

Base = declarative_base()

SessionClass = sessionmaker(engine)