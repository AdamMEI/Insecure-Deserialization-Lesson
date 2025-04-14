import pickle
import cookie_manager
import base64

class Comment:
    def __init__(self, text, username):
        self.text = text
        self.username = username
    def to_dict(self):
        return {"text": self.text, "username": self.username}
    @staticmethod
    def from_dict(data):
        return Comment(data["text"], data["username"])

# Save comments (serialize)
def save_comments(comments):
    # converts list of Comment objects to a list of dicts
    comment_dicts = [comment.to_dict() for comment in comments]
    json_string = json.dumps(comment_dicts)
    cookie_manager.save_cookie("comments", json_string)

# Load comments (deserialize)
def load_comments():
    cookie = cookie_manager.get_cookie("comments")
    if cookie:
        try:
            comment_dicts = json.loads(cookie)
            # converts list of dicts to a list of Comments
            return [Comment.from_dict(d) for d in comment_dicts]
        except json.JSONDecodeError:
            return []
    return []
