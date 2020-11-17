"""Initialize Flask app."""
from flask import Flask
from functools import wraps
from flask_mail import Mail


def create_app():
    """Create Flask application."""
    app = Flask(__name__, instance_relative_config=False)

    with app.app_context():
        #Import config
        from nancy.config import Config
        # Import parts of our application
        from nancy.auth import auth
        from nancy.shop import shop
        from nancy.seller import seller
        from nancy.user import user
        from nancy.media_server import media

        # Register Blueprints
        app.register_blueprint(auth.auth_bp, url_prefix= "/auth")
        app.register_blueprint(shop.shop_bp, url_prefix= "/shop")
        app.register_blueprint(seller.seller_bp, url_prefix= "/seller")
        app.register_blueprint(user.user_bp, url_prefix="/user")
        app.register_blueprint(media.media_bp, url_prefix="/media")

        #Add Configuration from Config Object
        app.config.from_object(Config)

        mail = Mail(app)


        app.debug = True

        return app
