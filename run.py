from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse, Message
from jinja2 import Environment, FileSystemLoader
from arrow import now
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]

db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Text)
    body = db.Column(db.Text)
    media_url = db.Column(db.Text)
    posted_on = db.Column(db.TIMESTAMP)

    def __init__(self, sender, body, media_url):
        self.sender = sender
        self.body = body
        self.media_url = media_url

        ny_time = timezone('America/New_York')
        self.posted_on = ny_tz.localize(now().datetime)


@app.route('/')
def index():
    jinja = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))), trim_blocks=True)

    posts = Post.query.order_by(Post.posted_on.desc()).all()

    return jinja.get_template('blog.html.j2').render(posts=posts)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    sender = request.values.get('From', None)
    body = request.values.get('Body', '')
    num_media = int(request.values.get('NumMedia', 0))
    msg = Message().body(body)
    resp = MessagingResponse()

    if body == '':
        msg = Message().body('Please include a message.')
    elif num_media > 1:
        msg = Message().body('Please only include one image.')
    elif num_media == 0:
        msg = Message().body('Please include an image.')
    elif num_media == 1:
        media_url_0 = request.values.get('MediaUrl0', None)
        db.session.add(Post(sender, body, media_url_0))
        db.session.commit()
        msg = Message().body('Patio posted! http://bit.ly/2rIKhJa')

    resp.append(msg)

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    app.run(debug=True, host='0.0.0.0', port=port)
