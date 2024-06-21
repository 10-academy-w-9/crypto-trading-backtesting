from flask import Blueprint, request, jsonify
from app.models.backtest import Backtest, Parameter, Result
from app import db
from flask_jwt_extended import jwt_required
from app.services.backtest_service import run_backtest_by_id
from app.services.kafka_service import kafka_service

bp = Blueprint('backtest', __name__)


@bp.route('/backtest', methods=['POST'])
@jwt_required()
def run_backtest():
    data = request.get_json()
    name = data.get('name')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    parameters = data.get('parameters')

    # Check if backtest with same parameters exists
    existing_backtest = Backtest.query.filter_by(name=name, start_date=start_date, end_date=end_date).first()
    if existing_backtest:
        return jsonify(
            {"msg": "Backtest with same parameters already exists", "backtest_id": existing_backtest.id}), 200

    # Create new backtest
    new_backtest = Backtest(name=name, start_date=start_date, end_date=end_date, status="pending")
    db.session.add(new_backtest)
    db.session.commit()

    # Add parameters
    for param in parameters:
        new_param = Parameter(backtest_id=new_backtest.id, indicator_id=param['indicator_id'], value=param['value'])
        db.session.add(new_param)

    db.session.commit()

    # Publish backtest to Kafka for processing
    kafka_service.produce('backtest_scenes', {
        "backtest_id": new_backtest.id,
        "parameters": parameters
    })

    return jsonify({"msg": "Backtest created and published to Kafka", "backtest_id": new_backtest.id}), 201


def consume_backtest_scenes():
    def callback(message):
        backtest_id = message.get('backtest_id')
        run_backtest_by_id(backtest_id)

    kafka_service.consume('backtest_scenes', callback)


consume_backtest_scenes()  # Start consuming Kafka messages in a separate thread
