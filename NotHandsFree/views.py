from NotHandsFree import app, backend, sockets, redis, db
from NotHandsFree.models import Speeddial

from flask import render_template, jsonify, request, url_for
from twilio import twiml
from twilio.rest import TwilioRestClient

import gevent

import logging
from logging import StreamHandler
file_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)  # set the desired logging level here
app.logger.addHandler(file_handler)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/train", methods=['GET', 'POST'])
def train():
    if request.method == "POST":
        # We're creating a new speeddial
        newdial = Speeddial(
            gesture=request.form['gesture'],
            number=request.form['number']
        )

        db.session.add(newdial)
        db.session.commit()
    return render_template("train.html")

@app.route("/speed")
def get_all_speeddial():
    dials = []
    for assoc in Speeddial.query.all():
        dials.append({'gesture': assoc.gesture, 'number': assoc.number})
    return jsonify(speeddial=dials)

@app.route("/call", methods=['POST'])
def create_call():
    to_call = request.form['gesture']
    association = Speeddial.query.filter_by(gesture=to_call).first_or_404()
    number = association.number

    try:
        tclient = TwilioRestClient(app.config['TWILIO_ACCOUNT_SID'],
                                   app.config['TWILIO_AUTH_TOKEN'])

    except Exception as e:
        msg = 'Missing configuration variable: {0}'.format(e)
        return jsonify({'error': msg})

    # try:
    outbound = url_for('outbound', _external=True)
    app.logger.info(outbound)
    app.logger.info("%s %s" % (app.config['TWILIO_CALLER_ID'], number))
    tclient.calls.create(to=number,
                         from_=app.config['TWILIO_CALLER_ID'],
                         url=outbound)
    # except Exception as e:
    #     app.logger.error(e)
    #     return jsonify({'error': str(e)})
    return jsonify({'message': 'Call incoming!'})

@app.route('/outbound', methods=['POST'])
def outbound():
    response = twiml.Response()

    response.say("Thank you for calling. You will be connected shortly.",
                 voice='alice')

    with response.dial() as dial:
        dial.number("+447415722341")
    return str(response)

@app.route("/input", methods=['POST'])
def recv_input():
    json = request.get_json(force=True)
    for key in json:
        val = json[key]
        del json[key]
        json[str(key)] = str(val)
    redis.publish(app.config['REDIS_CHAN'], json)
    return jsonify(status="OK")

@sockets.route('/ws')
def ws_receive(ws):
    backend.register(ws)
    while not ws.closed:
        gevent.sleep()