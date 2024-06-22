# Import necessary modules
import threading
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app import db
from app.models.backtest import Indicator, Coin
from app.services.backtest_service import run_backtest_by_id
from app.services.kafka_service import kafka_service

# Define Blueprint
bp = Blueprint('data', __name__)

# Endpoint for fetching coins
@bp.route('/coins', methods=['GET'])
@jwt_required()
def fetch_coins():
    # Assuming you have a model named Coin
    coins = Coin.query.all()
    coin_list = [{'id': coin.id, 'name': coin.name, 'symbol': coin.symbol} for coin in coins]
    
    return jsonify({'coins': coin_list}), 200

# Endpoint for fetching indicators
@bp.route('/indicators', methods=['GET'])
@jwt_required()
def fetch_indicators():
    # Assuming you have a model named Indicator
    indicators = Indicator.query.all()
    indicator_list = [{'id': indicator.id, 'name': indicator.name, 'description': indicator.description} for indicator in indicators]
    print(indicator_list)
    return jsonify({'indicators': indicator_list}), 200
