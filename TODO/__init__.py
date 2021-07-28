from flask import Flask, render_template, url_for, g
import os

def create_app():
    app = Flask("TODO")
    app.config.from_mapping(DATABASE="Manager")
    app.secret_key = os.urandom(24)

    
    from . import todo
    app.register_blueprint(todo.bp)
    
    from . import db
    db.init_app(app)
    
    
    
    
    @app.route("/")
    def index():
        return render_template('index.html')
    
    
    return app
    
