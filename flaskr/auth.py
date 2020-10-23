import functools
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from PIL import Image
from flaskr.db import get_db
from werkzeug.utils import secure_filename
from flask import Flask

bp = Blueprint('auth', __name__, url_prefix='/auth')

#UPLOAD_FOLDER = '/home/oancea/Desktop/flask-tutorial/flaskr/static/profile_pics'
UPLOAD_FOLDER = '/home/oancea/Desktop/dizertatie/flask-tutorial/flaskr/static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        company_name = request.form['company_name']
        contact = request.form['contact']
        contact_phone = request.form['contact_phone']
        contact_email = request.form['contact_email']
        address = request.form['address']
        password = request.form['password']



        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        elif not company_name:
            error = 'Company name is required.'
        elif not contact:
            error = 'Contact is required.'
        elif not contact_phone:
            error = 'Contact phone is required.'
        elif not contact_email:
            error = 'Contact email is required.'
        elif not password:
            error = 'Password is required.'
        elif not address:
            error = 'Address is required'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'Username {} is already registered.'.format(username)
        elif db.execute(
            'SELECT id FROM user WHERE contact = ?', (contact,)
        ).fetchone() is not None:
            error = 'Contact {} is already registered.'.format(contact)
        elif db.execute(
            'SELECT id FROM user WHERE contact_phone = ?', (contact_phone,)
        ).fetchone() is not None:
            error = 'Contact with phone number {} is already registered.'.format(contact_phone)
        elif db.execute(
            'SELECT id FROM user WHERE contact_email = ?', (contact_email,)
        ).fetchone() is not None:
            error = 'Contact with email address {} is already registered.'.format(contact_email)
        elif db.execute(
            'SELECT id FROM user WHERE address = ?', (address,)
        ).fetchone() is not None:
            error = 'Contact with address {} is already registered'.format(address)

        if error is None:
            db.execute(
                'INSERT INTO user (username,company_name,contact,contact_phone,contact_email,address,password) VALUES (?,?,?,?,?,?,?)',
                (username,company_name,contact,contact_phone,contact_email,address,generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')



@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def get_account(id):
    account = get_db().execute(
        'SELECT username,company_name,contact,contact_phone,contact_email,address,logo FROM user WHERE id = ?',(id,)
        ).fetchone()

    return account

@bp.route("/<int:id>/account",  methods=['GET', 'POST'])
@login_required
def account(id):
    filename = None
    account = get_account(id)

    if request.method == 'POST':
        username = request.form['username']
        company_name = request.form['company_name']
        contact = request.form['contact']
        contact_phone = request.form['contact_phone']
        contact_email = request.form['contact_email']
        address = request.form['address']

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        #if file.filename == '':
        #    flash('No selected file')
        #   return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            output_size = (125,125)
            full_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_name)
            i = Image.open(full_name)
            i.thumbnail(output_size)
            i.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))



        error = None

        if not username:
            error = 'Username is required'
        elif not company_name:
            error = 'Company name is required.'
        elif not contact:
            error = 'Contact is required.'
        elif not contact_phone:
            error = 'Contact phone is required.'
        elif not contact_email:
            error = 'Contact email is required.'
        elif not address:
            error = 'Address is required.'

        
        
        if error is None:
            print('**********')
            db = get_db()
            if filename:
                db.execute(
                        'UPDATE user SET username = ?, company_name = ?, contact = ?, contact_phone = ?, contact_email = ?, logo = ?, address = ?'
                    ' WHERE id = ?',
                    (username, company_name,contact,contact_phone,contact_email,filename,address,id)
                    )
                db.commit()
                return render_template('auth/account.html', account = account , image = filename)
            else:
                db.execute(
                        'UPDATE user SET username = ?, company_name = ?, contact = ?, contact_phone = ?, contact_email = ?, address = ?'
                    ' WHERE id = ?',
                    (username, company_name,contact,contact_phone,contact_email,address,id)
                        )
                db.commit()
                return render_template('auth/account.html', account = account , image = account['logo'])

        flash(error)

    if account['logo']:
        return render_template('auth/account.html', account = account,
            image = account['logo'])
    else: 
        return render_template('auth/account.html', account = account,
            image = 'default.jpg') 