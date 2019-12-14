import os


# uncomment the line below for postgres database url from environment variable
postgres_base = 'postgres://ptgqegjffgjalr:e7cef014443aa2dc5231e5dab3ac83519f998d4503001c730d5bda79a30427c1@ec2-107-21-235-87.compute-1.amazonaws.com:5432/d76sshgg8gvarr'

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')
    SECURITY_PASSWORD_SALT = 'my_secret_password'

    DEBUG = False
    FLASK_ADMIN_SWATCH = 'cerulean'
    REDIS_HOST = '0.0.0.0'
    REDIS_PORT = 6379
    BROKER_URL = os.environ.get('REDIS_URL', 'redis://{host}:{port}/0'.format(
        host=REDIS_HOST, port=str(REDIS_PORT)))
    CELERY_RESULT_BACKEND = BROKER_URL
    LANGUAGES = {
        'en_EN': 'English',
        'uk_UA': 'Ukrainian',
        'de': 'Deutsch'
    }

    MAIL_SERVER ='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'system.spero@gmail.com'
    MAIL_PASSWORD = '343dfb3e'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    STRIPE_KEY = 'sk_test_KkGEJemEelBHxdDIVLKkpfgo00OELhzQhM'
    STRIPE_PLANS = {
        'ADVANCED': 'plan_G8q6hcSY0O28k1',
        'MAX': 'plan_G8q5R7P8EzA3Wh'
    }

    CLOUD_NAME = 'dvm82rgep'
    KEY = '998544382314233'
    SECRET = 'jZR0l8VCm4q0MavVVwI7Gdr7ZVo'


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = postgres_base
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'flask_boilerplate_test.db')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    SQLALCHEMY_DATABASE_URI = postgres_base


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY
