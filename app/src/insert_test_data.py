import sys
from datetime import datetime, time, timedelta
from random import randrange, randint, choice

from sqlalchemy.exc import InternalError
from sqlalchemy.orm import (
    Session
)

from models import engine, Clients, Restaurants, Tables, Reservations
from entries import RESTAURANTS, CLIENTS


def rand_datetime(start: datetime, end: datetime) -> datetime:
    """Returns a random datetime between start and end."""

    return datetime.fromtimestamp(randrange(
        round(start.timestamp()), round(end.timestamp())
    ))

def rand_time(start: time, end: time) -> time:
    """Returns a random time between start and end."""
    time_start = rand_datetime(
        datetime.combine(dt0 := datetime.fromtimestamp(0), start),
        datetime.combine(
            dt0 if start < end else dt0 + timedelta(hours=1),
            end
        )
    )
    time_end = time_start + timedelta(hours=1)
    return time_start.time(), time_end.time()
        
class FillDB:
    def __init__(self, engine, entries, num_reservations):
        self.engine = engine
        self.num_reservations = int(num_reservations)
        for i in entries:
            self._insert_objects(i[0], i[1])
        self._add_tables()
        self._add_reservations()
        
    def _insert_objects(self, entries: list, model):
        for entry in entries:
            new_obj = model()
            for key, value in entry.items():
                setattr(new_obj, key, value)
            with Session(self.engine) as session:
                session.add(new_obj)
                session.flush()
                entry['id'] = new_obj.id
                session.commit()
                
    def _add_tables(self):
        with Session(self.engine) as session:
            restaurants = session.query(Restaurants).all()
            for rest in restaurants:
                for i in range(1, 10):
                    table = Tables(internal_id=i, restaurant_id=rest.id, capacity = randint(1,8))
                    session.add(table)
            session.commit()
   
   
    def _add_reservations(self):
        with Session(engine) as session:
            rests = session.query(Restaurants).all()
            tables = []
            for rest in rests:
                tables.append(session.query(Tables).filter(Tables.restaurant_id==rest.id).all())
            clients = session.query(Clients).all()
            count = 0
            
            while count < self.num_reservations:
                table = choice(choice(tables))
                try:
                    start_time, end_time = rand_time(table.restaurant.time_open, table.restaurant.time_closed)
                    date = rand_datetime(datetime.today(), datetime.today()+timedelta(days=15)).date(),
                except ValueError:
                    continue
                reservation = Reservations(
                client = choice(clients),
                table = table,
                date = date,
                start_time = start_time,
                end_time = end_time
                )
                try:
                    session.add(reservation)
                    session.commit()
                    count += 1
                except InternalError as e:
                    session.rollback()


                
                
if __name__ == '__main__':
    entries = [(RESTAURANTS, Restaurants), (CLIENTS, Clients)]
    num_reservations = sys.argv[1] if sys.argv[1] else 15
    FillDB(engine, entries, num_reservations)
    