# run.py

import os

from api import create_app
# from flask_caching import Cache
# from werkzeug.contrib.cache import SimpleCache

config_name = os.getenv('APP_SETTINGS')
app = create_app(config_name)
# cache = SimpleCache(app)
# cache = Cache(app)
# cache.init_app(app)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run('', port=port)