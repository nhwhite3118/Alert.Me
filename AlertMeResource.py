import config
from flask import Flask
import flask
import pymysql
from twilio.rest.lookups import TwilioLookupsClient
from datetime import datetime
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

app = Flask(__name__)

carrierPortalLookup = {
    "Verizon Wireless": "vtext.com",
    "Sprint Spectrum, L.P.": "messaging.sprintpcs.com",
    "AT&T Wireless": "txt.att.net",
}

# twilio
client = TwilioLookupsClient()
client = TwilioLookupsClient()

# database
#conn = pymysql.connect(host='127.0.0.1', user=config.DB_USER, passwd=config.DB_PASSWORD, db='alertme')
#cur = conn.cursor()


# subscribes a user by inserting their number into the database
@app.route("/api/subscribe/number/<number>/match/<match>/site/<site>", methods=["POST"])
def subscribe(number, match, site):
    conn = pymysql.connect(host='127.0.0.1', user=config.DB_USER, passwd=config.DB_PASSWORD, db='alertme')
    cur = conn.cursor()
    try:
        if len(str(int(number))) > 15:
            cur.close()
            conn.close()
            return "Please input a valid number"
    except:
        cur.close()
        conn.close()
        return "Please input a valid number"

    numberInfo = client.phone_numbers.get(number, include_carrier_info=True)
    carrier = numberInfo.carrier['name']
    # Convert carrier to portal
    portal = ""
    if carrier in carrierPortalLookup:
        portal = carrierPortalLookup[carrier]
    else:
        cur.close()
        conn.close()
        return "We are sorry, but AlertMe does not support your carrier"

    sql = "INSERT INTO user(number,portal,matchstr,site) VALUES(%s,%s,%s,%s)"
    v = (str(number), portal, match, site)
    print(str(datetime.now()) + " Adding user - " + carrier + " " + str(v))
    cur.execute(sql, v)
    conn.commit()

    resp = flask.Response("Subscribed " + str(number), status=200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    cur.close()
    conn.close()
    return resp,


# unsubscribes a user by removing their number from the database
@app.route("/api/unsubscribe/number/<number>", methods=["POST"])
def unsubscribe(number):
    conn = pymysql.connect(host='127.0.0.1', user=config.DB_USER, passwd=config.DB_PASSWORD, db='alertme')
    cur = conn.cursor()
    try:
        if len(str(int(number))) > 15:
            return "Please input a valid number"
    except:
        return "Please input a valid number"

    print(str(datetime.now()) + " Removing user - " + number)
    cur.execute("DELETE FROM user WHERE number=" + number)
    conn.commit()

    resp = flask.Response("Unsubscribed " + str(number), status=200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    cur.close()
    conn.close()
    return resp


# debugging helpers
@app.route("/")
def hello():
    resp = flask.Response("Woo Alerts", status=200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

# consider taking out during release for privacy
@app.route("/users")
def users():
    conn = pymysql.connect(host='127.0.0.1', user=config.DB_USER, passwd=config.DB_PASSWORD, db='alertme')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user")
    users = ""
    for r in cur:
        users += str(r)
    resp = flask.Response(users, status=200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    cur.close()
    conn.close()
    return resp


if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(8000)
    print(str(datetime.now()) + " Flask started...")
    IOLoop.instance().start()

cur.close()
conn.close()

cur.close()
conn.close()
