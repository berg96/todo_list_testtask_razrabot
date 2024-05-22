from datetime import datetime

from flask import Flask, request, abort, jsonify
from flask_restful import fields, marshal_with

from models import Task, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_list.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db.init_app(app)

task_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}


@app.route('/tasks', methods=['GET'])
@marshal_with(task_fields)
def get_tasks():
    return Task.query.all()


@app.route('/tasks', methods=['POST'])
@marshal_with(task_fields)
def create_task():
    if not request.json or 'title' not in request.json:
        abort(400)
    task = Task(
        title=request.json['title'],
        description=request.json.get('description'),
    )
    db.session.add(task)
    db.session.commit()
    return task, 201


@app.route('/tasks/<int:task_id>', methods=['GET'])
@marshal_with(task_fields)
def get_task(task_id):
    return Task.query.get_or_404(task_id)


@app.route('/tasks/<int:task_id>', methods=['PUT'])
@marshal_with(task_fields)
def update_task(task_id):
    if not request.json:
        abort(400)
    task = Task.query.get_or_404(task_id)
    task.title = request.json.get('title', task.title)
    task.description = request.json.get('description', task.description)
    task.updated_at = datetime.now()
    db.session.commit()
    return task


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    db.session.delete(Task.query.get_or_404(task_id))
    db.session.commit()
    return {'detail': 'Задача успешно удалена'}, 204


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
