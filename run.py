from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse, Message
import os


app = Flask(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Respond to incoming calls with a simple text message."""

    # resp = MessagingResponse().message("Hello, Mobile Monkey")


    resp = MessagingResponse()

    body = request.values.get('Body', None)

    msg = Message().body(body)

    num_media = request.values.get('NumMedia', 0)

    if num_media > 0:
        media_url_0 = request.values.get('MediaUrl0', None)
        msg.media(media_url_0)

    # msg = Message().body("Hello, Mobile Monkey").media("https://demo.twilio.com/owl.png")

    resp.append(msg)

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
