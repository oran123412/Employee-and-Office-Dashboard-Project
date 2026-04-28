from flask import Flask
from controllers.api import api_bp
from controllers.web import web_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(port=5000, debug=True)
