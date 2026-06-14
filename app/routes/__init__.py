from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("index.html")

from app.routes.analysis import analysis_bp

__all__ = ["main_bp", "analysis_bp"]



