from flask import Blueprint, request, jsonify
from app.models.backtest import Backtest, Parameter, Result
from app import db
from flask_jwt_extended import jwt_required

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

    # Run the backtest (dummy processing here)
    result = run_backtest_logic(new_backtest.id)

    return jsonify(result), 201


def run_backtest_logic(backtest_id):
    # Dummy backtest logic
    result = Result(
        backtest_id=backtest_id,
        total_return=10.5,
        number_of_trades=20,
        winning_trades=15,
        losing_trades=5,
        max_drawdown=3.5,
        sharpe_ratio=1.8
    )
    db.session.add(result)
    db.session.commit()

    return {"msg": "Backtest completed", "backtest_id": backtest_id, "result": result.id}
