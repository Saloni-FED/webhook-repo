from flask import Flask

from app.webhook.routes import webhook
from flask_cors import CORS

# Creating our flask app
def create_app():

    app = Flask(__name__)
    CORS(app)
    
    # registering all the blueprints
    app.register_blueprint(webhook)
    
    return app
