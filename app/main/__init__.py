from flask import Blueprint, current_app

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission


@main.app_context_processor
def title_processor():
    return dict(WEB_TITLE=current_app.config['WEB_TITLE'])


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

