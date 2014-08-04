import os
from flask import Flask

app = Flask(__name__)
app.config.from_object('config.Default')
app.config.from_object(os.environ.get('APP_CONFIG'))

from . import views
from . import filters
