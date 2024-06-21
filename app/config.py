class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://test_user:password@localhost/test_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_secret_key'
