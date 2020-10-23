import os
from flask import (
    Blueprint, flash, Flask,g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from flaskr.auth import login_required
from flaskr.db import get_db
from PIL import Image


bp = Blueprint('web', __name__)

#UPLOAD_FOLDER = '/home/oancea/Desktop/flask-tutorial/flaskr/static/profile_pics'
UPLOAD_FOLDER = '/home/oancea/Desktop/dizertatie/flask-tutorial/flaskr/static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/', methods=('GET', 'POST'))
@bp.route('/index', methods=('GET', 'POST'))
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, description, created, author_id, username, image_file, price,condition,category'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    pt = {'latest_post': 'Latest Posts',
        'lower_price': 'Lower Price',
        'higher_price': 'Higher Price'}

    if request.method == 'POST':
        select = str(request.form['test'])
        categ = str(request.form['cates'])
        print(categ)
        page_title = pt[select]
        #order by last items
        if select == 'latest_post':
            if categ =='0':
                posts = db.execute(
                    'SELECT p.id, title, description, created, author_id, username, image_file, price,condition,category'
                    ' FROM post p JOIN user u ON p.author_id = u.id'
                    ' ORDER BY created DESC'
                ).fetchall()
            else:
                posts = db.execute(
                    'SELECT p.id, title, description, created, author_id, username, image_file, price,condition,category'
                    ' FROM post p JOIN user u ON p.author_id = u.id'
                    '  WHERE category=? ORDER BY created DESC', (categ,)
                ).fetchall()

        #order by lower price items
        if select == 'lower_price':
            if categ =='0':
                posts = db.execute(
                    'SELECT p.id, title, description, created, author_id, username, image_file, price,condition,category'
                    ' FROM post p JOIN user u ON p.author_id = u.id'
                    ' ORDER BY price ASC'
                ).fetchall()
            else:
                posts = db.execute(
                    'SELECT p.id, title, description, created, author_id, username, image_file, price,condition,category'
                    ' FROM post p JOIN user u ON p.author_id = u.id'
                    ' WHERE category=? ORDER BY price ASC', (categ,)
                ).fetchall()
        #order by higher price items
        
        if select == 'higher_price':
            if categ =='0':
                posts = db.execute(
                    'SELECT p.id, title, description, created, author_id, username, image_file, price,condition,category'
                    ' FROM post p JOIN user u ON p.author_id = u.id'
                    ' ORDER BY price DESC'
                ).fetchall()
            else:
                posts = db.execute(
                    'SELECT p.id, title, description, created, author_id, username, image_file, price,condition,category'
                    ' FROM post p JOIN user u ON p.author_id = u.id'
                    ' WHERE category=? ORDER BY price DESC', (categ,)
                ).fetchall()

        return render_template('web/index.html', posts=posts, page_title = page_title)

    page_title = 'Latest Posts'
    return render_template('web/index.html', posts=posts, page_title = page_title)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        description = request.form['description']
        condition = request.form['condition']
        price = request.form['price']

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            output_size = (225,225)
            full_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_name)
            i = Image.open(full_name)
            i.thumbnail(output_size)
            i.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            error = None
            if not title:
                error = 'Title is required.'


            print(error)
            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'INSERT INTO post (title, category,description, author_id,price,condition,image_file)'
                    ' VALUES (?, ?, ?,?,?,?,?)',
                    (title, category,description, g.user['id'],price,condition,filename)
                )
                db.commit()
                return render_template('web/create.html', data=['Routers', 'Switches', 'Servers'], condition_options=['New','Used','Refurbished'] ,photo = filename)
                #return redirect(url_for('web.index'))


    return render_template('web/create.html', data=['Routers', 'Switches', 'Servers'],condition_options=['New','Used','Refurbished'] ,photo = 'empty.jpg')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title,description, created,price,author_id, username,image_file'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/post', methods=('GET', 'POST'))
def post(id):
    post = get_db().execute(
        'SELECT p.id, title,description, created, price,author_id, condition,username,image_file'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    account = get_db().execute(
        'SELECT username,company_name,contact,contact_phone,contact_email,address,logo FROM user WHERE id = ?',(post['author_id'],)
        ).fetchone()

    print(account)

    return render_template('web/post.html', post=post, account=account)



@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        error = None
        condition = request.form['condition']
        file = request.files['file']

        filename = post['image_file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            output_size = (225,225)
            full_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_name)
            i = Image.open(full_name)
            i.thumbnail(output_size)
            i.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, description = ?, image_file = ?, price = ?,condition = ?'
                ' WHERE id = ?',
                (title, description,filename,price,condition,id)
            )
            db.commit()
            return redirect(url_for('web.index'))

    return render_template('web/update.html', post=post, data=['Routers', 'Switches', 'Servers'],  condition_options=['New','Used','Refurbished'])

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('web.index'))


@bp.route('/<int:id>/profile', methods=('GET', 'POST'))
def profile(id):
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, description, created, author_id, username, image_file'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('web/profile.html', posts=posts)
