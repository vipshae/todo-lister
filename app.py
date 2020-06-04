import sys
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Refer to .env.example to set up the .env local env file correctly
from dotenv import load_dotenv
load_dotenv(verbose=True)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://" + os.getenv('POSTGRES_USER') + "@localhost:" \
                                        + os.getenv('POSTGRES_PORT') + "/" + os.getenv('POSTGRES_DB')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class ToDo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Todo {self.id}, Description: {self.description}>'


# Not needed since updates to the db model maintained by flask migrate
#db.create_all()


@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo = ToDo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route('/')
def index():
    return render_template('index.html', data=ToDo.query.all())
