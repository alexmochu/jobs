# config.py
import os

class Config(object):
    """
    Common configurations
    """
    # Put any configurations here that are common across all environments
    SQLALCHEMY_DATABASE_URI =  os.getenv('DATABASE_URL')
    SECRET_KEY = 'ofdhrjrbrneirgeojgoegekgneogre'
    DEBUG = True
    CACHE_TYPE= os.getenv('CACHE_TYPE')  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT= os.getenv("CACHE_DEFAULT_TIMEOUT")

class DevelopmentConfig(Config):
    """
    Development configurations
    """
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    DEBUG = True
    SQLALCHEMY_ECHO = True
    CACHE_TYPE= os.getenv('CACHE_TYPE')  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT= os.getenv("CACHE_DEFAULT_TIMEOUT")

class ProductionConfig(Config):
    """
    Production configurations
    """
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    DEBUG = False
    CACHE_TYPE= os.getenv('CACHE_TYPE')  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT= os.getenv("CACHE_DEFAULT_TIMEOUT")

class TestingConfig(Config):
    """ Configurations for Testing, with a separate test database."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SECRET_KEY = 'ofdhrjrbrneirgeojgoegekgneogre'

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}