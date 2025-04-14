from flask import Flask, render_template, request, make_response
from flask_cors import CORS
import docker_management
import uuid
import json
import redis

app = Flask(__name__)
CORS(app, supports_credentials=True)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sandbox")
def sandbox():
    return render_template("sandbox.html")

@app.route("/load-comments", methods=["GET"])
def load_comments():
    session_id = request.cookies.get("session_id")
    if not session_id:
        return {"error": "no session"}, 403
    code = r.get(session_id)
    if not code:
        print("haven't set user code")
        return {"error": "haven't set user code"}, 400
    comments_string = docker_management.load_comments(request.cookies, code)
    try:
        comments = json.loads(comments_string)
        return comments
    except json.JSONDecodeError:
        return {"error": f"json decode failed, input is: {comments_string}"}, 400

@app.route("/save-comments", methods=["POST"])
def save_comments():
    session_id = request.cookies.get("session_id")
    if not session_id:
        return {"error": "no session"}, 403
    code = r.get(session_id)
    if not code:
        print("haven't set user code")
        return {"error": "haven't set user code"}, 400
    comments = request.get_json()
    if comments == None:
        return {"error": "no comments"}, 400
    response = make_response("Saved comments")
    docker_management.save_comments(response, code, comments)
    return response

@app.route("/set-user-code", methods=["POST"])
def set_user_code():
    session_id = request.cookies.get("session_id")
    if not session_id:
        return {"error": "no session"}, 403
    code = request.get_json().get("user-code")
    if not code:
        return {"error": "no user code"}, 400
    r.set(session_id, code)
    return {"status": "ok"}

@app.route("/set-session-id", methods=["GET"])
def set_session_id():
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response = make_response("Logged in!")
        response.set_cookie("session_id", session_id, httponly=True, samesite='Lax')
        return response
    return {"session_id": session_id}

if __name__ == "__main__":
    app.run(debug=True)
