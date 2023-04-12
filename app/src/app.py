from flask import Flask, request, jsonify
from flask_pydantic import validate

from sqlalchemy.orm import Session
from sqlalchemy.exc import InternalError, IntegrityError

from models import Reservations, Restaurants, Clients, Tables, engine
from models_schema import ReservationSchema, ReservationOptionsSchema

app = Flask(__name__)

@app.route('/reservation', methods=['GET'])
def get_reservations():
    restaurant_id = request.args.get('restaurant_id', default=None, type=int)
    date = request.args.get('date', default=None, type=str)
    result = {}
    with Session(engine) as session:
        reservations = session.query(Restaurants, Tables, Reservations).filter(Restaurants.id==Tables.restaurant_id).filter(Tables.id==Reservations.table_id)
        if restaurant_id:
            reservations=reservations.filter(Restaurants.id==restaurant_id)
        if date:
            reservations=reservations.filter(Reservations.date==date)
        reservations = reservations.all()
        for reservation in reservations:
            restaurant, table, res = reservation
            if not result.get(restaurant.id):
                result[restaurant.id]={}
            if not result[restaurant.id].get(table.internal_id):
                 result[restaurant.id][table.internal_id]={}
            if not result[restaurant.id][table.internal_id].get(str(res.date)):
                result[restaurant.id][table.internal_id][str(res.date)]=[]
            result[restaurant.id][table.internal_id][str(res.date)].append({
                'id': res.id,
                'start_time': str(res.start_time),
                'end_time': str(res.end_time),
                'clients_name': res.client.name,
                'clients_phone': res.client.phone
            })
    return jsonify(result), 200

@app.route('/reservation', methods=['POST'])
@validate(body=ReservationSchema)
def make_reservation():
    body = request.get_json()
    reservation = Reservations()
    for key, value in body.items():
        setattr(reservation, key, value)
    with Session(engine) as session:
        session.add(reservation)
        try:
            session.commit()
        except InternalError as e:
            session.rollback()
            resp = str(e.orig).split('\n')[0]
            return jsonify(resp), e.code
        except IntegrityError as e:
            session.rollback()
            resp = str(e.orig).split('\n')[0].split(' ')[-1]
            return jsonify(resp), e.code
        resp = f'Столик {reservation.table_id} забронирован с {reservation.start_time} до {reservation.end_time} {reservation.date} для клиента {reservation.client.name}!'
    return jsonify(resp), 201
    

@app.route('/reservation/<int:reservation_id>', methods=["PUT", "DELETE"])
@validate(body=ReservationOptionsSchema)
def change_reservation(reservation_id):
    body = request.get_json()
    if request.method == "PUT":
        with Session(engine) as session:
            reservation = session.query(Reservations).filter(Reservations.id == reservation_id).first()
            if not reservation:
                raise NotFoundException(
                    f'Бронирование с id {reservation_id} не найдено в базе.')
            msg = 'Изменено '
            for key, value in body.items():
                setattr(reservation, key, value)
                msg += f'{key}: {value}, '
            try:
                session.commit()
            except InternalError as e:
                session.rollback()
                resp = str(e.orig).split('\n')[0]
                return jsonify(resp), e.code
            except IntegrityError as e:
                session.rollback()
                resp = str(e.orig).split('\n')[0].split(' ')[-1]
                return jsonify(resp), e.code
         
    elif request.method == "DELETE":
        with Session(engine) as session:
            deleted = session.query(Reservations).filter(
                Reservations.id == reservation_id).delete()
            if deleted == 0:
                ex = NotFoundException(
                    f'Бронирование с id {reservation_id} не найдено в базе.')
                return jsonify(str(ex)), ex.code
            session.commit()
        msg = 'deleted'

    return jsonify({
        'success': True,
        'msg': msg
    }), 200
    
class NotFoundException(Exception):
    code = 400
    description = "Not Found"
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
