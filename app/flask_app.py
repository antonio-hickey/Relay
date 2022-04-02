from flask import Flask

from app.routes import conversation, user

application = Flask(__name__)
app = application

app.register_blueprint(user.blueprint)
app.register_blueprint(conversation.blueprint)


@app.route("/")
def healthcheck():
    return "ok"
