from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse, Message
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]

db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Text)
    body = db.Column(db.Text)
    media_url = db.Column(db.Text)

    def __init__(self, sender, body, media_url):
        self.sender = sender
        self.body = body
        self.media_url = media_url

    # def __repr__(self):
    #     return '<User %r>' % self.username


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Respond to incoming calls with a simple text message."""
    sender = request.values.get('From', None)
    body = request.values.get('Body', None)
    num_media = int(request.values.get('NumMedia', 0))
    msg = Message().body(body)
    resp = MessagingResponse()

    if num_media == 1:
        media_url_0 = request.values.get('MediaUrl0', None)

        db.session.add(Post(sender, body, media_url_0))
        db.session.commit()

        msg = msg.media(media_url_0)
    elif num_media > 1:
        msg = Message().body('Please only include one image.')
    else:
        msg = Message().body('Please include an image.')

    resp.append(msg)

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    app.run(debug=True, host='0.0.0.0', port=port)
