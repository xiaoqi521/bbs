from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.board import Board


main = Blueprint('board', __name__)

@main.route('/admin')
def index():
	u = current_user()
	if u is not None and u.admin == True:
		return render_template('board/admin_index.html')
	else:
		return redirect(url_for('index.index'))

@main.route('/add',  methods=["POST"])
def add():
	u = current_user()
	if u is not None and u.admin == True:
		form = request.form
		m = Board.new(form)
		return redirect(url_for('topic.index'))
	else:
		return redirect(url_for('index.index'))
