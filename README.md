# flask_classfield_site
"Telecom Now" it's a classfield site used for selling telecomunication equipments, it's developed using Flask micro-framework, and SQLite database engine. 


Run the application using following commands:

export FLASK_APP=flaskr
export FLASK_ENV=development
flask init-db
flask run

Application structure.
├── flaskr
│   ├── auth.py
│   ├── db.py
│   ├── __init__.py
│   ├── __init__.pyc
│   ├── __pycache__
│   │   ├── auth.cpython-35.pyc
│   │   ├── auth.cpython-36.pyc
│   │   ├── blog.cpython-35.pyc
│   │   ├── blog.cpython-36.pyc
│   │   ├── db.cpython-35.pyc
│   │   ├── db.cpython-36.pyc
│   │   ├── __init__.cpython-35.pyc
│   │   ├── __init__.cpython-36.pyc
│   │   ├── __init__.cpython-37.pyc
│   │   ├── web.cpython-35.pyc
│   │   └── web.cpython-36.pyc
│   ├── schema.sql
│   ├── static
│   │   ├── logo_vodafone.jpeg
│   │   ├── profile_pics
│   │   │   ├── cisco1800.jpg
│   │   │   ├── cisco_1900.jpg
│   │   │   ├── default.jpg
│   │   │   ├── logo_vodafone.jpeg
│   │   │   ├── picturemessage_r0gxtd03.vox.png
│   │   │   ├── rslogo.png
│   │   │   ├── switch.jpg
│   │   │   └── Vodafone_logo.png
│   │   └── style.css
│   ├── templates
│   │   ├── auth
│   │   │   ├── account.html
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── base.html
│   │   └── web
│   │       ├── create.html
│   │       ├── index.html
│   │       ├── post.html
│   │       ├── profile.html
│   │       └── update.html
│   └── web.py
├── instance
│   └── flaskr.sqlite
└── run.py
