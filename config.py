# config.py
import os

class Config(object):
    """
    Common configurations
    """
    # Put any configurations here that are common across all environments
    SQLALCHEMY_DATABASE_URI =  'postgresql+psycopg2://dolf:wawu@localhost:5432/jobs'
    SECRET_KEY = 'ofdhrjrbrneirgeojgoegekgneogre'
    DEBUG = True

class DevelopmentConfig(Config):
    """
    Development configurations
    """

    SQLALCHEMY_DATABASE_URI =  'postgresql+psycopg2://dolf:wawu@localhost:5432/jobs'
    SECRET_KEY = 'ofdhrjrbrneirgeojgoegekgneogre'
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False

class TestingConfig(Config):
    """ Configurations for Testing, with a separate test database."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://obadolf:@localhost:5432/weConnect_db_test'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SECRET_KEY = 'ofdhrjrbrneirgeojgoegekgneogre'

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}