
from app.models import User
from flask_openid import OpenID
import re, requests, time
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
mylist = []
today = datetime.date.today()
mylist.append(today)

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
    g.user = None
    output = render_template('index.html',username=g.user,form=form)

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        output = render_template('req.html',username=g.user,form=form)

    flash("errors")
    return output

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    form = xForm()
    g.user = None
    email = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        if g.user is not None:
            email = g.user.email
        output = render_template('index.html',username=g.user,form=form,email=email)
    else:
        output = render_template('index.html',username=g.user,form=form,email=email)

    if form.ign.data != None:
        g.user.ign = form.ign.data
        g.user.email = form.email.data
        g.user.community = form.community.data
        g.user.age = form.age.data
        g.user.div = request.form.get('div')
        g.user.time = request.form.get('time')
        g.user.skills = request.form.get('skills')
        g.user.bio = request.form.get('bio')
        g.user.stuff = request.form.get('industries')
        g.user.disciplines = request.form.get('disciplines')
        now = mylist[0]
        g.user.date = str(now)


        cs = '10'
        tf2 = '12'
        ins = '86'
        gmod = '59'
        se = '82'
        mc = '71'
        pr = '101'
        xy = None

        drill(g.user.nickname,g.user.email)
        db_session.commit()


        if g.user.div == 'cs':
            xy = cs
        if g.user.div == 'ins':
            xy = ins
        if g.user.div == 'tf2':
            xy = tf2
        if g.user.div == 'gmod':
            xy = gmod
        if g.user.div == 'mc':
            xy = mc
        if g.user.div == 'se':
            xy = se
        if g.user.div == 'pr':
            xy = pr


        r = requests.get("http://108.61.149.51/1/info.php?div=%s&name=%s&steam_id=%s"%(xy,g.user.ign,g.user.steam_id))
        print r
        print r.url
        output = render_template('success.html',username=g.user,form=form)

    return output


@app.route('/req', methods=['GET', 'POST'])
def req():
    form = xForm()
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

    output = render_template('req.html',username=g.user,form=form)

    return output



@app.route('/select', methods=['GET', 'POST'])
def select():
    g.user = None
    form = xForm()
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        redirect(url_for("success"))

    if 'player' in request.form:
        g.user.ptype = True
        db_session.commit()
        return redirect(url_for("signup"))

    if 'team' in request.form:
        g.user.ptype = False
        db_session.commit()
        return redirect(url_for("signup"))

    output = render_template('select.html',username=g.user,form=form)
    return output


@app.route('/success', methods=['GET', 'POST'])
def success():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])




    output = render_template('success.html',username=g.user)

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
    db_session.commit()

    session['user_id'] = g.user.user_id
    session['admin'] = False
    output = redirect(open_id.get_next_url())
    return output


@app.route('/apps')
def apps():
    form = xForm
    g.user = None
    usl = ulist()
    num = count([])
    cnt = 0
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        admin = g.user.admin
        for us in usl:
            cnt += 1
        output = render_template('apps.html',username=g.user,form=form,uslz=reversed(usl),num=num,admin=admin,count=cnt)

    else:
        output = render_template('apps.html',username=g.user,form=form,uslz=reversed(usl),num=num,admin=False,count=0)



    return output


def ulist():
    userlist = []
    userlist2 = []
    userlist3 = []
    for user2 in User.query.filter(User.email.isnot(None)):
        userlist2 += [user2]
    for user1 in User.query.filter_by(admin=None):
        userlist += [user1]

    for user3 in userlist:
        if user3 in userlist2:
            userlist3 += [user3]

    return userlist3

def count(list):
    numz = []
    for user in User.query.filter():
        if not user in list:
            numz += [1]
    return numz



@app.route("/apps/<ap>", methods=['GET', 'POST'])
def ap(ap):
    gogo = None
    form = xForm()
    userlist = []
    userlist2 = []
    userlist3 = []
    usl = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
    pplz = User.query.filter_by(steam_id=ap)
    for user in pplz:
        gogo = user

    output = render_template('app.html',username=g.user,form=form,gogo=gogo)



    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


    if form.search.data:
        x = form.search.data



        for user2 in User.query.filter(User.email.isnot(None)):
            userlist2 += [user2]
        for user1 in User.query.filter_by(admin=None):
            if str(x) in str([user1][0].nickname.encode('ascii', 'ignore').lower()):
                userlist += [user1]
                print "stuff is %s"%x
                print [user1][0].nickname
            else:
                print "%s not in %s"%(x,[user1][0].nickname)

        for user3 in userlist:
            if user3 in userlist2:
                userlist3 += [user3]


        usl = userlist3
        cnt = 0
        output = render_template('apps.html',username=g.user,form=form,uslz=usl)

    if request.form.get("datebtn"):

        xf = request.form.get("datebtn")
        userlist = []
        userlist2 = []
        userlist3 = []
        userlist4 = []
        for user2 in User.query.filter(User.email.isnot(None)):
            userlist2 += [user2]
        for user1 in User.query.filter_by(admin=None):
            if [user1][0].date == xf:
                userlist += [user1]

        for user3 in userlist:
            if user3 in userlist2:
                userlist3 += [user3]

            usl = userlist3
        output = render_template('apps.html',username=g.user,form=form,uslz=usl)


    if request.form.get("divbtn"):
        xf = request.form.get("divbtn")
        userlist = []
        userlist2 = []
        userlist3 = []
        userlist4 = []
        for user2 in User.query.filter(User.email.isnot(None)):
            userlist2 += [user2]
        for user1 in User.query.filter_by(admin=None):
            if [user1][0].div == xf:
                userlist += [user1]

        for user3 in userlist:
            if user3 in userlist2:
                userlist3 += [user3]

            usl = userlist3

        output = render_template('apps.html',username=g.user,form=form,uslz=usl)


    if request.form.get('datesort'):
        ds = request.form.get('datesort')
        ulsz = ulist()
        output = render_template('apps.html',username=g.user,form=form,uslz=ulsz)



    return output

