from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import os


app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""

    # resp = MessagingResponse().message("Hello, Mobile Monkey")

    resp = MessagingResponse()
    msg = Message().body("Hello, Mobile Monkey").media("https://demo.twilio.com/owl.png")
    resp.append(msg)

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
