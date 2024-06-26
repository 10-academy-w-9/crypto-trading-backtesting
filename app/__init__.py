from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
import threading
from flask_cors import CORS  
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()

from app.services.backtest_service import run_backtest_by_id
from app.services.kafka_service import kafka_service

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate = Migrate(app, db)

    CORS(app)

    with app.app_context():
        from app.routes import auth, backtest, index, data
        app.register_blueprint(auth.bp)
        app.register_blueprint(backtest.bp)
        app.register_blueprint(index.bp)
        app.register_blueprint(data.bp)
        db.create_all()

    return app

def consume_backtest_scenes(app):
    def callback(message):
        with app.app_context():
            backtest_id = message.get('backtest_id')
            run_backtest_by_id(backtest_id)

    kafka_service.consume('backtest_scenes', callback)

# Start consuming Kafka messages in a separate thread
def start_consumer_thread(app):
    consumer_thread = threading.Thread(target=consume_backtest_scenes, args=(app,))
    consumer_thread.daemon = True  # Allow the thread to be killed when the main program exits
    consumer_thread.start()

app = create_app()
start_consumer_thread(app)
