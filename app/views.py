
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
        g.user.status = "Pending"
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


        if g.user.div == 'Counter-Strike':
            xy = cs
        if g.user.div == 'Insurgency':
            xy = ins
        if g.user.div == 'Team Fortress 2':
            xy = tf2
        if g.user.div == 'Gmod':
            xy = gmod
        if g.user.div == 'Minecraft':
            xy = mc
        if g.user.div == 'Space Engineers':
            xy = se
        if g.user.div == 'Public Relations':
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
    g.user.flag = 1
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
    cnt = 0

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        admin = g.user.admin
        for us in usl:
            cnt += 1
        output = render_template('apps.html',username=g.user,form=form,uslz=reversed(usl),admin=admin,count=cnt)

    else:
        output = render_template('apps.html',username=g.user,form=form,uslz=reversed(usl),admin=False,count=0)

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


@app.route("/apps/<ap>", methods=['GET', 'POST'])
def ap(ap):
    gogo = None
    form = xForm()
    userlist = []
    userlist2 = []
    userlist3 = []
    admin = None
    usl = None
    mod = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        if g.user:
            admin = g.user.admin
            mod = g.user.flag
    pplz = User.query.filter_by(steam_id=ap)
    for user in pplz:
        gogo = user

    output = render_template('app.html',username=g.user,form=form,gogo=gogo,admin=admin,mod=mod)


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
        output = render_template('apps.html',username=g.user,form=form,uslz=usl,mod=mod)

    if request.form.get("datebtn"):

        xf = request.form.get("datebtn")
        userlist = []
        userlist2 = []
        userlist3 = []
        for user2 in User.query.filter(User.email.isnot(None)):
            userlist2 += [user2]
        for user1 in User.query.filter_by(admin=None):
            if [user1][0].date == xf:
                userlist += [user1]

        for user3 in userlist:
            if user3 in userlist2:
                userlist3 += [user3]

            usl = userlist3
        output = render_template('apps.html',username=g.user,form=form,uslz=usl,mod=mod)


    if request.form.get("divbtn"):
        xf = request.form.get("divbtn")
        userlist = []
        userlist2 = []
        userlist3 = []
        for user2 in User.query.filter(User.email.isnot(None)):
            userlist2 += [user2]
        for user1 in User.query.filter_by(admin=None):
            if [user1][0].div == xf:
                userlist += [user1]

        for user3 in userlist:
            if user3 in userlist2:
                userlist3 += [user3]

            usl = userlist3

        output = render_template('apps.html',username=g.user,form=form,uslz=usl,mod=mod)


    if request.form.get("statbtn"):
        sbt = request.form.get("statbtn")

        userlist = []
        userlist2 = []
        userlist3 = []
        for user2 in User.query.filter(User.email.isnot(None)):
            userlist2 += [user2]
        for user1 in User.query.filter_by(admin=None):
            if [user1][0].status == sbt:
                userlist += [user1]

        for user3 in userlist:
            if user3 in userlist2:
                userlist3 += [user3]

            usl = userlist3

        output = render_template('apps.html',username=g.user,form=form,uslz=usl,mod=mod)



    if request.form.get('datesort'):
        ds = request.form.get('datesort')
        ulsz = ulist()
        output = render_template('apps.html',username=g.user,form=form,uslz=ulsz,mod=mod)


    if request.form.get('revbtn'):
        x = request.form.get('revbtn')
        for user1 in User.query.filter_by(steam_id=x):
            [user1][0].status = "Under Review"
            db_session.commit()
            ulsz = ulist()
            output = render_template('app.html',username=g.user,form=form,uslz=ulsz,gogo=gogo,admin=admin,mod=mod)
    if request.form.get('aprbtn'):
        x = request.form.get('aprbtn')
        for user1 in User.query.filter_by(steam_id=x):
            [user1][0].status = "Approved"
            db_session.commit()
            ulsz = ulist()
            output = render_template('app.html',username=g.user,form=form,uslz=ulsz,gogo=gogo,admin=admin,mod=mod)
    if request.form.get('dnybtn'):
        x = request.form.get('dnybtn')
        for user1 in User.query.filter_by(steam_id=x):
            [user1][0].status = "Denied"
            db_session.commit()
            ulsz = ulist()
            output = render_template('app.html',username=g.user,form=form,uslz=ulsz,gogo=gogo,admin=admin,mod=mod)




    return output



def admusl():
    userlist = []
    userlist2 = []
    userlist3 = []
    for user2 in User.query.filter(User.steam_id.isnot(None)):
        userlist2 += [user2]


    return userlist2

@app.route('/users', methods=['GET', 'POST'])
@app.route('/users/search', methods=['GET', 'POST'])
def users():
    form = xForm
    g.user = None
    usl = admusl()

    admin = None

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        admin = g.user.admin
        output = render_template('users.html',username=g.user,form=form,uslz=reversed(usl),admin=admin)

    else:
        output = render_template('users.html',username=g.user,form=form,uslz=reversed(usl),admin=False)



    if request.form.get('modbtn'):
        x = request.form.get('modbtn')
        for user1 in User.query.filter_by(steam_id=x):
            [user1][0].flag = 2
            db_session.commit()

            output = render_template('users.html',username=g.user,form=form,uslz=reversed(usl),admin=admin)
    if request.form.get('rmmbtn'):
        x = request.form.get('rmmbtn')
        for user1 in User.query.filter_by(steam_id=x):
            [user1][0].flag = 1
            db_session.commit()

            output = render_template('users.html',username=g.user,form=form,uslz=reversed(usl),admin=admin)
    if request.form.get('adadm'):
        x = request.form.get('adadm')
        for user1 in User.query.filter_by(steam_id=x):
            [user1][0].admin = 1
            db_session.commit()

            output = render_template('users.html',username=g.user,form=form,uslz=reversed(usl),admin=admin)
    if request.form.get('rmadm'):
        x = request.form.get('rmadm')
        for user1 in User.query.filter_by(steam_id=x):
            [user1][0].admin = 0
            db_session.commit()

            output = render_template('users.html',username=g.user,form=form,uslz=reversed(usl),admin=admin)

    if request.form.get("divbtn"):
        xf = request.form.get("divbtn")
        userlist = []
        userlist2 = []
        userlist3 = []
        for user2 in User.query.filter(User.email.isnot(None)):
            if [user2][0].div == xf:
                userlist2 += [user2]

            usl = userlist2

        output = render_template('users.html',username=g.user,form=form,uslz=usl,admin=admin)


    if request.form.get('search'):
        userlist = []
        userlist2 = []
        userlist3 = []
        xxd = []
        x = request.form.get('search')

        for user2 in User.query.filter(User.steam_id.isnot(None)):
            if str(x) in str([user2][0].nickname.encode('ascii', 'ignore').lower()):
                userlist2 += [user2]



        usl = userlist2
        output = render_template('users.html',username=g.user,form=form,uslz=usl,admin=admin)


    return output



@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
