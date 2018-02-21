from flask import (
	render_template,
	request,
	redirect,
	session,
	url_for,
	Blueprint,
	make_response,
	send_from_directory,
    abort,
)

from routes import *
from utils import log
import os
from config import user_file_director
import uuid

main = Blueprint('index', __name__)

"""
用户路由 在这里可以
    访问首页 index
    注册 register
    登录 login
    退出 logout
    个人主页 profile
    用户头像 uploads
    用户资料 setting
用户登录后, 会写入 session, 并且定向到 /topic
带有session的用户打开登录页面,会定向到/topic
将用户操作信息写入log

"""


@main.route('/', methods=[ 'GET' ])
def index():
	u = current_user()
	login = request.args.get('msg', None)
	if u is not None:
		return redirect(url_for('topic.index'))
	elif login == 'False':
		msg = '登录失败,请检查用户名或密码!'
		return render_template('user/login.html', msg=msg)
	else:
		return render_template('user/login.html')


# register注册页面
@main.route('/register', methods=[ 'GET' ])
def registered():
	return render_template('user/register.html')


# 注册
@main.route('/register', methods=[ 'POST' ])
def register():
	form = request.form
	# 用类函数来判断
	u = User.register(form)
	if u is None:
		msg = '注册失败,请检查 !'
		log(request.remote_addr, form[ 'username' ], '注册失败')
		return render_template('user/register.html', msg=msg)
	elif u == 'repeat':
		msg = '用户名已存在 !'
		log(request.remote_addr, form[ 'username' ], '用户名已存在')
		return render_template('user/register.html', msg=msg)
	else:
		msg = '注册成功 !'
		log(request.remote_addr, u.username, '注册成功')
		return render_template('user/register.html', user=u, msg=msg)


@main.route('/login', methods=[ 'POST' ])
def login():
	form = request.form
	u = User.validate_login(form)
	if u is None:
		# 登录失败!
		msg = 'False'
		log(request.remote_addr, form[ 'username' ], '登录失败')
		return redirect(url_for('.index', msg=msg))
	else:
		# session 中写入 user_id
		session[ 'user_id' ] = u.id
		# 设置 cookie 有效期为 永久
		session.permanent = True
		log(request.remote_addr, u.id, '登录成功')
		return redirect(url_for('topic.index'))


@main.route('/logout')
def logout():
	# 清除session用户信息
	session[ 'user_id' ] = None
	return redirect(url_for('index.index'))

@main.route('/user/<username>')
def user(username):
	u = current_user()
	user = User.find_by(username=username)
	if user is not None:
		if u is None:
			login = False
			return render_template('user/users.html', user=user, login=login)
		login = True
		return render_template('user/users.html', user=user, login=login)
	else:
		abort(404)


@main.route('/setting',  methods=[ 'POST' ])
def setting():
	u = current_user()
	if u is None:
		return redirect(url_for('index.index'))
	form = request.form
	for k, v in form.items():
		setattr(u,k,v)
		u.save()
	return redirect(url_for('index.user'))



def allow_file(filename):
	suffix = filename.split('.')[ -1 ]
	return suffix


@main.route('/addimg', methods=[ 'POST' ])
def add_img():
	u = current_user()
	if u is None:
		return redirect(url_for('index.index'))
	if 'file' not in request.files:
		return redirect(request.url)
	file = request.files[ 'file' ]
	if file.filename == '':
		return redirect(request.url)
	suffix = allow_file(file.filename)

	from config import accept_user_file_type

	if suffix in accept_user_file_type:
		filename = str(uuid.uuid4()) + '.' + suffix
		file.save(os.path.join(user_file_director, filename))
		u.user_image = filename
		u.save()
	log(u.id, '用户已上传头像')
	return redirect(url_for('.user',username=u.username))


@main.route('/uploads/<int:user_id>')
def uploads(user_id):
	u = User.get(id=user_id)
	filename =u.user_image
	return send_from_directory(user_file_director, filename)



