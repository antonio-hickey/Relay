from flask import Flask

from app.routes import conversation, user, web

application = Flask(__name__,
                    static_folder='static',
                    template_folder='templates')
app = application

app.register_blueprint(user.blueprint)
app.register_blueprint(conversation.blueprint)
app.register_blueprint(web.blueprint)


@app.route("/")
def healthcheck():
    return "ok"
