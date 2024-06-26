import threading
from flask import Blueprint, request, jsonify, current_app
from app.models.backtest import Backtest, Result
from app import db
from flask_jwt_extended import jwt_required
from app.services.backtest_service import run_backtest_by_id, run_and_evaluate_backtest
from app.services.kafka_service import kafka_service
from flask_cors import CORS, cross_origin

bp = Blueprint('backtest', __name__)
CORS(bp)

@bp.route('/backtests', methods=['POST'])
@jwt_required()
@cross_origin(origin='*')
def run_backtest():
    data = request.get_json()
    name = data.get('name')
    symbol = data.get('coin')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    inital_cash = data.get('inital_cash')
    fee = data.get('fee')

    # Check if backtest with same parameters exists
    existing_backtest = Backtest.query.filter_by(name=name, symbol=symbol, start_date=start_date, end_date=end_date).first()
    if existing_backtest:
        return jsonify(
            {"msg": "Backtest with same parameters already exists", "backtest_id": existing_backtest.id}), 200

    # Create new backtest
    new_backtest = Backtest(name=name, symbol=symbol, start_date=start_date, end_date=end_date, inital_cash=inital_cash, fee = fee)
    db.session.add(new_backtest)
    db.session.commit()


    # # Publish backtest to Kafka for processing
    # kafka_service.produce('backtest_scenes', {
    #     "backtest_id": new_backtest.id
    # })
    run_and_evaluate_backtest(backtest_id=new_backtest.id, symbol=symbol, initial_cash= inital_cash, fee=fee, start_date=start_date,end_date= end_date)

    return jsonify({"msg": "Backtest created and published to Kafka", "backtest_id": new_backtest.id}), 201


@bp.route('/backtests', methods=['GET'])
@jwt_required()
@cross_origin(origin='*')
def get_backtests():
    backtests = Backtest.query.all()
    backtest_list = []
    for backtest in backtests:
        backtest_list.append({
            'id': backtest.id,
            'name': backtest.name,
            'symbol': backtest.symbol,
            'start_date': backtest.start_date.strftime('%Y-%m-%d'),
            'end_date': backtest.end_date.strftime('%Y-%m-%d'),
            'inital_cash': backtest.inital_cash,
            'fee': backtest.fee,
            'created_at': backtest.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({'backtests': backtest_list}), 200

@bp.route('/backtests/<int:backtest_id>/results', methods=['GET'])
@jwt_required()
@cross_origin(origins='*')
def get_backtest_results(backtest_id):
    results = Result.query.filter_by(backtest_id=backtest_id).all()
    if not results:
        return jsonify({'msg': 'No results found for this backtest'}), 404
    
    result_list = []
    for result in results:
        result_list.append({
            'id': result.id,
            'strategy': result.strategy,
            'total_return': float(result.total_return),
            'number_of_trades': result.number_of_trades,
            'winning_trades': result.winning_trades,
            'losing_trades': result.losing_trades,
            'max_drawdown': float(result.max_drawdown),
            'sharpe_ratio': float(result.sharpe_ratio),
            'is_best': result.is_best
        })
    
    return jsonify({'results': result_list}), 200
