from flask import Flask

from app.routes import user

application = Flask(__name__)
app = application

app.register_blueprint(user.blueprint)


@app.route("/")
def healthcheck():
    return "ok"
