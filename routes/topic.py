from flask import (
	render_template,
	request,
	redirect,
	url_for,
	Blueprint,
	abort,
)

from routes import *
from utils import log
from models.topic import Topic
from models.board import Board

main = Blueprint('topic', __name__)

'''
topic路由 在这里可以
   主题 index
   详情 detail
   发布话题 new[GET]
   增加内容 add
   删除话题 delete 
每一个路由会先检查session,查不到用户就会定向到登录页面   
'''
import uuid

csrf_tokens = dict()


@main.route('/')
def index():
	u = current_user()
	board_id = int(request.args.get('board_id', -1))
	bs = Board.all()
	if board_id == -1:
		ms = Topic.all()
	else:
		ms = Topic.find_all(board_id=board_id)
	if u is None:
		login = False
		return render_template('topic/index.html', ms=ms, bs=bs, login=login)
	login = True
	token = uuid.uuid4()
	csrf_tokens[ str(token) ] = u.id
	return render_template('topic/index.html', ms=ms, bs=bs, token=token, user=u, login=login)


@main.route('/<int:id>')
def detail(id):
	u = current_user()
	t = Topic.get(id)
	# 传递 topic 的所有 reply 到 页面中
	user = User.get(id=t.user_id)
	board = Board.get(id=t.board_id)
	if u is None:
		login = False
		return render_template('topic/detail.html', topic=t, user=user, board=board, login=login)
	login = True
	return render_template('topic/detail.html', topic=t, user=user, board=board, login=login, my=u)


@main.route('/new', methods=[ "GET" ])
def new():
	u = current_user()
	if u is None:
		return redirect(url_for('index.index'))
	bs = Board.all()
	return render_template('topic/new.html', bs=bs)


@main.route('/add', methods=[ "POST" ])
def add():
	u = current_user()
	if u is None:
		return redirect(url_for('index.index'))
	form = request.form
	m = Topic.new(form, user_id=u.id)
	return redirect(url_for('.detail', id=m.id))


@main.route('/delete')
def delete():
	u = current_user()
	if u is None:
		return redirect(url_for('index.index'))
	id = int(request.args.get('id', -1))
	token = request.args.get('token')
	if token in csrf_tokens and csrf_tokens[ token ] == u.id:
		csrf_tokens.pop(token)
		if u.admin == True:
			log('topic id 为:', id, '被id为:', u.id, '的用户删除!')
			Topic.delete(id)
			return redirect(url_for('.index'))
		else:
			return redirect(url_for('.index'))
	else:
		abort(403)
