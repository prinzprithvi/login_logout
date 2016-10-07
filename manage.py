__author__ = 'prathvi'
# Set the path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from flask.ext.script import Manager, Server
from app  import ecom_app

from app.views import app_views
ecom_app.register_blueprint(app_views)

from console_ui.views import console_views
ecom_app.register_blueprint(console_views)

from flask_sauth.views import auth_views
ecom_app.register_blueprint(auth_views)

manager = Manager(ecom_app)
# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger=False,
    use_reloader=False,
    host='0.0.0.0',port=8080)
)

# from GunicornServer import GunicornServer
# manager.add_command("rungunicorn", GunicornServer())

# import flask_sauth.commands
# flask_sauth.commands.add_commands(manager)

if __name__ == "__main__":
    manager.run()

