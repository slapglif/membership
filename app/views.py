
from app.models import User
from flask_openid import OpenID
import re, requests, time, MySQLdb
from app import app
from app import engine
from app import db_session
from flask import url_for, render_template, flash, g, session, \
        redirect
from flask import request
from .forms import xForm
from mandril import drill
from subprocess import (PIPE, Popen)
import datetime
from mandril import drill

def tnow():
    tlist = []
    today = datetime.date.today()
    tlist.append(today)

def cmd(command):
  return Popen(command, shell=True, stdout=PIPE)

con = engine.connect()
app.secret_key = 'super secret key'
STEAM_API_KEY = "1A15D2C82402F944CF5625FC011EF14C"
open_id = OpenID(app)
_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')





@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = xForm()
    admin = None
    sr = requests.get("http://freebieservers.com/api/SeekStats?user=testest&pass=testest")
    stats = sr.json()
    sl = requests.get("http://freebieservers.com/api/SeekServers?user=testest&pass=testest")
    sstats = sl.json()

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin

    output = render_template('index.html',form=form,growth=stats['user_data'],utoday=stats['users_today'],ptoday=stats['purchases_today'],servers=sstats)

    flash("errors")
    return output



@app.route('/hdd', methods=['GET', 'POST'])
def hdd():
    form = xForm()
    admin = None
    output = render_template('hdd.html',username=g.user,form=form,admin=admin)


    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin
        output = render_template('hdd.html',username=g.user,form=form,admin=admin)

    flash("errors")
    return output



@app.route('/email', methods=['GET', 'POST'])
def email():
    form = xForm()
    admin = None
    output = render_template('email.html',username=g.user,form=form,admin=admin)


    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin

    output = render_template('email.html',username=g.user,form=form,admin=admin,emailsent=False)

    if form.subject.data != None and form.body.data != None:
        s = form.subject.data
        b = form.body.data
        db = MySQLdb.connect("db.freebieservers.com","root","Fuc5M4n15!","gamecp")
        cursor = db.cursor()
        sql = "SELECT * FROM users WHERE active != '3'"
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            email = row[2]
            drill(s,b,email)
        output = render_template('email.html',username=g.user,form=form,admin=admin,emailsent=True)

    flash("errors")
    return output


@app.route('/hdd/seeker', methods=['GET', 'POST'])
def hddseeker():
    form = xForm()
    admin = None
    output = render_template('hdd.html',username=g.user,form=form,admin=admin)

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin
        #r = requests.get("http://freebieservers.com:62992/api/SeekUsers?user=testest&pass=testest")
        #results = r.json()
        output = render_template('hdd.html',username=g.user,form=form,admin=admin)

    flash("errors")
    return output




def get_steam_userinfo(steam_id):
    options = {
        'key': STEAM_API_KEY,
        'steamids': steam_id
    }
    url = 'http://api.steampowered.com/ISteamUser/' \
          'GetPlayerSummaries/v0001'

    r = requests.get(url, params=options)
    rv = r.json()
    return rv['response']['players']['player'][0] or {}

@app.route('/login')
@open_id.loginhandler
def login():
    if g.user is not None:
        flash("You already have a team!")
        return redirect(open_id.get_next_url())

    return open_id.try_login('http://steamcommunity.com/openid')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('admin', None)
    return redirect(open_id.get_next_url())


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@open_id.after_login
def create_or_login(response):
    form = xForm()
    match = _steam_id_re.search(response.identity_url)
    g.user = User.get_or_create(match.group(1))
    steamdata = get_steam_userinfo(g.user.steam_id)
    g.user.nickname = steamdata['personaname']
    g.user.flag = 1
    db_session.commit()
    session['user_id'] = g.user.user_id
    output = redirect(open_id.get_next_url())
    return output


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
