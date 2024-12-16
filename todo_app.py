from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import subprocess
import sys
from flask_cors import CORS 


try:
    import flask_pymongo
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask-pymongo'])

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}})
app.config['MONGO_URI'] = 'mongodb+srv://troygons246:thisismynewpassword#2024@cluster0.oxyqd.mongodb.net/todo_db?retryWrites=true&w=majority&appName=Cluster0'
mongo = PyMongo(app)

todo_collection = mongo.db.todos


# Root Route
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the To-Do API!  Open index.html using liveserver'}), 200


# Routes and APIs
@app.route('/todo', methods=['POST'])
def add_task():
    data = request.json
    title = data.get('title')
    description = data.get('description')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    task = {
        "title": title,
        "description": description,
        "is_completed": False
    }
    result = todo_collection.insert_one(task)
    task["_id"] = str(result.inserted_id)

    return jsonify(task), 201

@app.route('/todo', methods=['GET'])
def get_tasks():
    tasks = list(todo_collection.find())
    for task in tasks:
        task["_id"] = str(task["_id"])
    return jsonify(tasks), 200

@app.route('/todo/<string:task_id>', methods=['PUT'])
def edit_task(task_id):
    data = request.json
    update_data = {}

    if "title" in data:
        update_data["title"] = data["title"]
    if "description" in data:
        update_data["description"] = data["description"]
    if "is_completed" in data:
        update_data["is_completed"] = data["is_completed"]

    try:
        result = todo_collection.update_one({"_id": ObjectId(task_id)}, {"$set": update_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if result.matched_count == 0:
        return jsonify({'error': 'Task not found'}), 404

    updated_task = todo_collection.find_one({"_id": ObjectId(task_id)})
    updated_task["_id"] = str(updated_task["_id"])
    return jsonify(updated_task), 200

@app.route('/todo/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        result = todo_collection.delete_one({"_id": ObjectId(task_id)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if result.deleted_count == 0:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify({'message': 'Task deleted successfully'}), 200

@app.route('/todo', methods=['DELETE'])
def delete_all_tasks():
    todo_collection.delete_many({})
    return jsonify({'message': 'All tasks deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
