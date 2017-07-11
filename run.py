from flask import Flask, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from jinja2 import Environment, FileSystemLoader
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse, Message

import arrow
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]

db = SQLAlchemy(app)

client = Client(os.environ["ACCOUNT_SID"], os.environ["AUTH_TOKEN"])


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)


class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    mobile_number = db.Column(db.Text)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Text, db.ForeignKey('team_member.mobile_number'))
    body = db.Column(db.Text)
    media_url = db.Column(db.Text)
    posted_on = db.Column(db.TIMESTAMP)
    teams = db.relationship('Team', secondary='team_member')

    def __init__(self, sender, body, media_url):
        self.sender = sender
        self.body = body
        self.media_url = media_url
        self.posted_on = arrow.utcnow().datetime


@app.route('/')
def index():
    jinja = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))), trim_blocks=True)

    posts = Post.query.order_by(Post.posted_on.desc()).all()

    for post in posts:
        post.posted_on = arrow.get(post.posted_on).to('America/New_York')

    return jinja.get_template('blog.html.j2').render(posts=posts)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    sender = request.values.get('From', None)
    body = request.values.get('Body', '')
    num_media = int(request.values.get('NumMedia', 0))
    msg = Message().body(body)
    resp = MessagingResponse()

    if not TeamMember.query.filter(TeamMember.mobile_number == sender).first():
        abort(403)

    if body == '' or num_media != 1:
        msg = Message().body('Please include a single image with a caption.')
    elif num_media == 1:
        media_url_0 = request.values.get('MediaUrl0', None)
        db.session.add(Post(sender, body, media_url_0))
        db.session.commit()
        msg = Message().body('Patio posted! {}'.format(os.environ["APP_URL"]))

        posting_team = Team.query.filter(Team.id == TeamMember.query.filter(TeamMember.mobile_number == sender).first().team_id).first()
        other_team_members = TeamMember.query.filter(TeamMember.team_id != posting_team.id).all()

        for member in other_team_members:
            client.api.account.messages.create(to=member.mobile_number, from_=os.environ["TWILIO_NUMBER"], body='{} just posted a patio! {}'.format(posting_team.name, os.environ["APP_URL"]))

    resp.append(msg)

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    app.run(debug=True, host='0.0.0.0', port=port)
