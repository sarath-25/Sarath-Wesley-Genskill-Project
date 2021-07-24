from flask import Flask, render_template

def create_app():
    app = Flask("TODO List Manager")
    app.config.from_mapping(DATABASE="Manager")
    
    
    from . import TODO
    app.register_blueprint(TODO.bp)
    
    from . import db
    db.init_app(app)
    
    return app
