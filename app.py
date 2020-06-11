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


# Parent class
class ToDoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todos = db.relationship('ToDo', backref='list', passive_deletes=True, lazy=True)

    def __repr__(self):
        return f'<TodoList {self.id}, Name: {self.name}>'

# child class
class ToDo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id', ondelete='CASCADE'), nullable=False)

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
        active_list_id = request.get_json()['active_list_id']
        activelist = ToDoList.query.get(active_list_id)
        todo.list = activelist
        print('Creating', description)
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


@app.route('/todos/set-completed/<todo_id>', methods=['POST'])
def set_completed_todo(todo_id):
    error = False
    try:
        completed = request.get_json()['completed']
        print('Completed Todo:', todo_id)
        todo = ToDo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if error:
        abort(400)
    return jsonify({ 'success': True })


@app.route('/todos/delete-completed/<todo_id>', methods=['DELETE'])
def delete_completed_todo(todo_id):
    error = False
    try:
        print('Deleting todo:', todo_id)
        ToDo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    return jsonify({ 'success': True })    


@app.route('/lists/<list_id>', methods=['GET'])
def get_list_todos(list_id):
    return render_template('index.html', 
      lists=ToDoList.query.all(),
      active_list=ToDoList.query.get(list_id),
      todos=ToDo.query.filter_by(list_id=list_id).order_by('id').all())


@app.route('/lists/create', methods=['POST'])
def create_list():
    error = False
    body = {}
    try:        
        newlist = ToDoList(name=request.get_json()['name'])
        print('Creating list:', newlist.name)
        db.session.add(newlist)
        db.session.commit()
        body['name'] = newlist.name
        body['listid'] = newlist.id
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


@app.route('/lists/set-completed/<list_id>', methods=['POST'])
def set_completed_list(list_id):
    error = False
    try:
        completed = request.get_json()['completed']
        print('Completed list', list_id)
        listObj = ToDoList.query.get(list_id)
        listObj.completed = completed
        ToDo.query.filter_by(list_id=list_id).update({ToDo.completed: completed})
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if error:
        abort(400)
    return jsonify({ 'success': True })


@app.route('/lists/delete-completed/<list_id>', methods=['DELETE'])
def delete_completed_list(list_id):
    error = False
    try:
        print('Deleting list:', list_id)
        ToDoList.query.filter_by(id=list_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    return jsonify({ 'success': True })  


@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))
