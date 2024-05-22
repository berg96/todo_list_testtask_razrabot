import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify, flash
from flask_restful import fields, marshal_with

from models import Task, db

load_dotenv()
DB_NAME = os.getenv('MYSQL_DATABASE')
DB_USER = os.getenv('MYSQL_USER')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD')
DB_HOST = os.getenv('MYSQL_HOST')
DB_CONTAINER_NAME = 'mysql_db'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql://{DB_USER}:{DB_PASSWORD}@{DB_CONTAINER_NAME}:{DB_HOST}/{DB_NAME}'
)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
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
    flash('Задача создана!', 'success')
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
    flash('Задача обновлена!', 'success')
    return task


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    db.session.delete(Task.query.get_or_404(task_id))
    db.session.commit()
    flash('Задача удалена!', 'success')
    return jsonify({'detail': 'Задача успешно удалена'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
