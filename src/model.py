from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
from db import Base

class Dvl(Base):
    __tablename__ = 'dvl'

    ch_id = Column(Integer, primary_key=True)
    message_id = Column(Integer)
    start_time = Column(Integer)
    total_time = Column(Integer)