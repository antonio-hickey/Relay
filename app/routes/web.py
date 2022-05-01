from flask import Blueprint, render_template

blueprint = Blueprint("web", __name__)


@blueprint.route("/web-app/sign-up", methods=["GET"])
def sign_up_page():
    """
    This endpoint will respond with rendering the
    html from the sign-up page.
    """
    return render_template('pages/sign-up.html')


@blueprint.route("/web-app/sign-in", methods=["GET"])
def sign_in_page():
    """
    This endpoint will respond with rendering the
    html from the sign-in page.
    """
    return render_template('pages/sign-in.html')
