import os
from sqlalchemy import create_engine, Column, Integer, String, Time, ForeignKey, Date, Identity, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship, backref


POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_PORT = os.environ['POSTGRES_PORT']
POSTGRES_SUB_DB = os.environ['POSTGRES_DB']

postgres_url =  f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_SUB_DB}'

engine = create_engine(postgres_url)

Base = declarative_base()


class Clients(Base):
    __tablename__ = 'clients'
    
    id = Column(Integer, Identity(), primary_key=True, nullable=False)
    name = Column(String(50), nullable=False) 
    phone = Column(String(15), nullable=False)
    email = Column(String(50), nullable=False)

class Restaurants(Base):
    __tablename__ = 'restaurants'
    
    id = Column(Integer, Identity(), primary_key=True, nullable=False)
    address = Column(String(50), nullable=False) 
    phone = Column(String(30), nullable=False)
    email = Column(String(50), nullable=False)
    time_open = Column(Time, nullable=False)
    time_closed = Column(Time, nullable=False)
    
    __table_args__ = (CheckConstraint(time_open < time_closed, name='time_closed_greater_than_time_open'),)

class Tables(Base):
    __tablename__ = 'tables'
    
    id = Column(Integer, Identity(), primary_key=True, nullable=False)
    internal_id = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id', ondelete='CASCADE')) 
    restaurant = relationship("Restaurants", backref=backref("tables", cascade="all,delete"))

class Reservations(Base):
    __tablename__ = 'reservations'
    
    id = Column(Integer, Identity(), primary_key=True, nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'))
    client = relationship("Clients", backref=backref("reservations", cascade="all,delete"))
    table_id = Column(Integer, ForeignKey("tables.id", ondelete='CASCADE'))
    table = relationship("Tables", backref=backref("reservations", cascade="all,delete"))
    
    __table_args__ = (CheckConstraint(start_time < end_time, name='end_time_greater_than_start_time'), )

    
Base.metadata.create_all(engine)