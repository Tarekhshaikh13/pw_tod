from flask import Flask, request, jsonify

app = Flask(__name__)

todos = []

@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(todos)

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    todo = data.get('todo')
    if todo:
        todos.append(todo)
        return jsonify({"message": "Todo added"}), 201
    return jsonify({"error": "Todo is required"}), 400

@app.route('/todos/<int:index>', methods=['DELETE'])
def delete_todo(index):
    try:
        todos.pop(index)
        return jsonify({"message": "Todo deleted"})
    except IndexError:
        return jsonify({"error": "Todo not found"}), 404

@app.route('/todos/<int:index>', methods=['PUT'])
def update_todo(index):
    try:
        data = request.get_json()
        todo = data.get('todo')
        if todo:
            todos[index] = todo
            return jsonify({"message": "Todo updated"})
        return jsonify({"error": "Todo is required"}), 400
    except IndexError:
        return jsonify({"error": "Todo not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
