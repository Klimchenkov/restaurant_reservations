from datetime import date, time

from pydantic import BaseModel
from typing import Optional

class ReservationSchema(BaseModel):
    date: date 
    start_time: time 
    end_time: time
    client_id: int
    table_id: int
    
    
class ReservationOptionsSchema(BaseModel):
    start_time: Optional[time] = None 
    end_time: Optional[time] = None 
    client_id: Optional[int] = None 
    table_id: Optional[int] = None 

    