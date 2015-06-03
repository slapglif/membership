
from app.models import User
from flask_openid import OpenID
import re, requests, time, MySQLdb, paramiko
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
    choice = 1
    form = xForm()
    admin = None
    sr = requests.get("http://freebieservers.com/api/SeekStats?user=testest&pass=testest")
    stats = sr.json()
    sl = requests.get("http://freebieservers.com/api/SeekServers?user=testest&pass=testest")
    sstats = sl.json()

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin

    output = render_template('index.html',form=form,growth=stats['user_data'],utoday=stats['users_today'],ptoday=stats['purchases_today'],servers=sstats,revenue=stats['payments_data'],total=stats['purchases_usd'])

    flash("errors")
    return output


@app.route('/<sz>', methods=['GET', 'POST'])
@app.route('/index/<sz>', methods=['GET', 'POST'])
def isz(sz):
    choice = 1
    form = xForm()
    admin = None
    sr = requests.get("http://freebieservers.com/api/SeekStats?user=testest&pass=testest")
    stats = sr.json()
    sl = requests.get("http://freebieservers.com/api/SeekServers?user=testest&pass=testest")
    sstats = sl.json()

    sload = None
    sram = None
    shdd = None
    shddf = None

    if sz:
        if sz == "1":
            db = MySQLdb.connect("db.freebieservers.com","root","Fuc5M4n15!","gamecp")
            cursor = db.cursor()

            ###build server box list###
            fetch = "SELECT * FROM servers WHERE id = '13'"
            cursor.execute(fetch)
            list = cursor.fetchall()
            for table in list:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(table[2],username='root',password='jajbsdddsd32555339f99cgggvcdad1f')
                x = """top -b -n2 -p 1 | fgrep "Cpu(s)" | tail -1 | awk -F'id,' -v prefix="$prefix" '{ split($1, vs, ","); v=vs[length(vs)]; sub("%", "", v); printf "%s%.1f%%", prefix, 100 - v }'"""
                y = "free | awk 'FNR == 3 {print $3/($3+$4)*100}'"
                z = """df -hl | awk '{print $5}' | head -n 3 | grep "[0-9]" """
                xx = """df -hl | awk '{print $4}' | head -n 3 | grep "[0-9]" """

                stdin1,stdout1,stderr1 = ssh.exec_command(x)
                stdin2,stdout2,stderr2 = ssh.exec_command(y)
                stdin3,stdout3,stderr3 = ssh.exec_command(z)
                stdin4,stdout4,stderr4 = ssh.exec_command(xx)
                sload = stdout1.readlines()
                sram = stdout2.readlines()
                shdd = stdout3.readlines()
                shddf = stdout4.readlines()
                ssh.close()
            db.close()

    if sz:
        if sz == "2":
            db = MySQLdb.connect("db.freebieservers.com","root","Fuc5M4n15!","gamecp")
            cursor = db.cursor()
            ###build server box list###
            fetch = "SELECT * FROM servers WHERE id = '14'"
            cursor.execute(fetch)
            list = cursor.fetchall()
            for table in list:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(table[2],username='root',password='jajbsdddsd32555339f99cgggvcdad1f')
                x = """top -b -n2 -p 1 | fgrep "Cpu(s)" | tail -1 | awk -F'id,' -v prefix="$prefix" '{ split($1, vs, ","); v=vs[length(vs)]; sub("%", "", v); printf "%s%.1f%%", prefix, 100 - v }'"""
                y = "free | awk 'FNR == 3 {print $3/($3+$4)*100}'"
                z = """df -hl | awk '{print $5}' | head -n 3 | grep "[0-9]" """
                xx = """df -hl | awk '{print $4}' | head -n 3 | grep "[0-9]" """

                stdin1,stdout1,stderr1 = ssh.exec_command(x)
                stdin2,stdout2,stderr2 = ssh.exec_command(y)
                stdin3,stdout3,stderr3 = ssh.exec_command(z)
                stdin4,stdout4,stderr4 = ssh.exec_command(xx)
                sload = stdout1.readlines()
                sram = stdout2.readlines()
                shdd = stdout3.readlines()
                shddf = stdout4.readlines()
                ssh.close()
            db.close()
    if sz:
        if sz == "4":
            ###build server box list###
            db = MySQLdb.connect("db.freebieservers.com","root","Fuc5M4n15!","gamecp")
            cursor = db.cursor()
            fetch = "SELECT * FROM servers WHERE id = '16'"
            cursor.execute(fetch)
            list = cursor.fetchall()
            for table in list:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(table[2],username='root',password='jajbsdddsd32555339f99cgggvcdad1f')
                x = """top -b -n2 -p 1 | fgrep "Cpu(s)" | tail -1 | awk -F'id,' -v prefix="$prefix" '{ split($1, vs, ","); v=vs[length(vs)]; sub("%", "", v); printf "%s%.1f%%", prefix, 100 - v }'"""
                y = "free | awk 'FNR == 3 {print $3/($3+$4)*100}'"
                z = """df -hl | awk '{print $5}' | head -n 3 | grep "[0-9]" """
                xx = """df -hl | awk '{print $4}' | head -n 3 | grep "[0-9]" """

                stdin1,stdout1,stderr1 = ssh.exec_command(x)
                stdin2,stdout2,stderr2 = ssh.exec_command(y)
                stdin3,stdout3,stderr3 = ssh.exec_command(z)
                stdin4,stdout4,stderr4 = ssh.exec_command(xx)
                sload = stdout1.readlines()
                sram = stdout2.readlines()
                shdd = stdout3.readlines()
                shddf = stdout4.readlines()
                ssh.close()
            db.close()

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin
    output = render_template('index.html',form=form,growth=stats['user_data'],utoday=stats['users_today'],ptoday=stats['purchases_today'],servers=sstats,revenue=stats['payments_data'],total=stats['purchases_usd'],load=sload[0].strip('%'),ram=sram[0],hdd=shdd,free=shddf)

    flash("errors")
    return output

@app.context_processor
def page_proc():
    def change_page(page):
        return page
    return dict(change_page=change_page)



@app.route('/hdd', methods=['GET', 'POST'])
def hdd():
    choice = 2
    form = xForm()
    admin = None
    sr = requests.get("http://freebieservers.com/api/SeekStats?user=testest&pass=testest")
    stats = sr.json()
    sl = requests.get("http://freebieservers.com/api/SeekServers?user=testest&pass=testest")
    sstats = sl.json()

    output = render_template('hdd.html',username=g.user,form=form,admin=admin,page=choice,servers=sstats)


    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin
        output = render_template('hdd.html',username=g.user,form=form,admin=admin,page=choice,servers=sstats)

    flash("errors")
    return output

@app.route('/hdd/<srv>', methods=['GET', 'POST'])
def hddgo(srv):
    choice = 2
    form = xForm()
    admin = None
    sr = requests.get("http://freebieservers.com/api/SeekStats?user=testest&pass=testest")
    stats = sr.json()
    sl = requests.get("http://freebieservers.com/api/SeekServers?user=testest&pass=testest")
    sstats = sl.json()

    output = render_template('hdd.html',username=g.user,form=form,admin=admin,page=choice,servers=sstats)


    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin
        output = render_template('hdd.html',username=g.user,form=form,admin=admin,page=choice,servers=sstats)

    flash("errors")
    return output

@app.route('/hdd/seeker/go', methods=['GET', 'POST'])
def hddseeker():
    form = xForm()
    admin = None
    choice = 2
    output = render_template('hdd.html',form=form)

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        r = requests.get("http://freebieservers.com:62992/api/SeekUsers?user=testest&pass=testest")
        results = r.json()
        output = render_template('hdd.html',form=form,page=2)

    flash("errors")
    return output

@app.route('/email', methods=['GET', 'POST'])
def email():
    choice = 3
    form = xForm()
    admin = None

    sr = requests.get("http://freebieservers.com/api/SeekStats?user=testest&pass=testest")
    stats = sr.json()
    sl = requests.get("http://freebieservers.com/api/SeekServers?user=testest&pass=testest")
    sstats = sl.json()

    output = render_template('email.html',form=form,servers=sstats,emailsent=False,sselect=None,page=choice)

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin

    flash("errors")
    return output


@app.route('/email/<srv>', methods=['GET', 'POST'])
def emails(srv):
    form = xForm()
    admin = None
    choice = 3
    sr = requests.get("http://freebieservers.com/api/SeekStats?user=testest&pass=testest")
    stats = sr.json()
    sl = requests.get("http://freebieservers.com/api/SeekServers?user=testest&pass=testest")
    sstats = sl.json()

    output = render_template('email.html',form=form,servers=sstats,emailsent=False,sselect=srv,page=choice)

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin

    if form.subject.data != None and form.body.data != None:
        s = form.subject.data
        b = form.body.data
        db = MySQLdb.connect("db.freebieservers.com","root","Fuc5M4n15!","gamecp")
        cursor = db.cursor()
        if srv == all:
            sql = "SELECT * FROM users WHERE active != '3'"
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                email = row[2]
                drill(s,b,email)
            output = render_template('email.html',username=g.user,form=form,admin=admin,emailsent=True,servers=sstats,sselect=srv,page=choice)
        else:
            output = render_template('email.html',username=g.user,form=form,admin=admin,emailsent=False,servers=sstats,sselect=srv,page=choice)

    flash("errors")
    return output



@app.route('/update', methods=['GET', 'POST'])
def update():
    choice = 4
    form = xForm()
    admin = None
    output = render_template('update.html',username=g.user,form=form,admin=admin,page=choice)


    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin
        output = render_template('update.html',username=g.user,form=form,admin=admin,page=choice)

    flash("errors")
    return output


@app.route('/update/run', methods=['GET', 'POST'])
def updaterun():
    choice = 4
    form = xForm()
    admin = None
    output = redirect("/")

    db = MySQLdb.connect("db.freebieservers.com","root","Fuc5M4n15!","gamecp")
    cursor = db.cursor()
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin
        output = redirect("/")
    ###build server box list###

    fetch = "SELECT * FROM servers WHERE ip != '0'"
    cursor.execute(fetch)
    list = cursor.fetchall()
    for table in list:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(table[2],username='root',password='jajbsdddsd32555339f99cgggvcdad1f')
        ssh.exec_command("screen -dmS updatecss ./steamcmd.sh +login anonymous +force_install_dir /home/gcp/installs/css +app_update 232330 validate +exit")
        ssh.exec_command("screen -dmS updatecsgo ./steamcmd.sh +login anonymous +force_install_dir /home/gcp/installs/csgo +app_update 740 validate +exit")
        ssh.exec_command("screen -dmS updatetf2 ./steamcmd.sh +login anonymous +force_install_dir /home/gcp/installs/tf2 +app_update 232250 validate +exit")
        ssh.exec_command("screen -dmS updategmod ./steamcmd.sh +login anonymous +force_install_dir /home/gcp/installs/gmod +app_update 4020 validate +exit")
        ssh.exec_command("screen -dmS updatedods ./steamcmd.sh +login anonymous +force_install_dir /home/gcp/installs/dods +app_update 232290 validate +exit")
        ssh.exec_command("screen -dmS updatehl2dm ./steamcmd.sh +login anonymous +force_install_dir /home/gcp/installs/hl2dm +app_update 232370 validate +exit")
        ssh.exec_command("screen -dmS updatel4d2 ./steamcmd.sh +login anonymous +force_install_dir /home/gcp/installs/l4d2 +app_update 222860 validate +exit")
        ssh.exec_command("screen -dmS updateins ./steamcmd.sh +login anonymous +force_install_dir /home/gcp/installs/ins +app_update 237410 validate +exit")
    db.close()
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
