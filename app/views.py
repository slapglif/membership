
from app.models import User
from flask_openid import OpenID
import re, requests, time, MySQLdb, random, paramiko, os
from app import app
from app import engine
from app import db_session
from flask import url_for, render_template, flash, g, session, \
        redirect
from flask import request
from .forms import xForm
from .forms import fdlform
from mandril import drill
from subprocess import (PIPE, Popen)
import datetime
from mandril import drill
import json, ast
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import stripe
from stripe import Customer, Charge
from .forms import stripeform


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator



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



@app.route('/servers', methods=['GET'])
def servers():
    sstats = json.loads(request.args.get('json'))

    output = render_template('servers.html',
                             server=sstats)
    return output


@app.route('/graphs', methods=['GET'])
def graphs():
    # print "hello"
    sstats = json.loads(request.args.get('json'))
    stats = apireq("http://freebieservers.com/api/SeekStats?user=testest&pass=testest")
    #print test

    pct_hdd = 0
    pct_ram = 0
    pct_cpu = 0
    xx = 0
    for x in sstats:
        print x
        pct_hdd += float(x["result"]["used_pct"])
        pct_ram += float(x["result"]["free_ram"])
        pct_cpu += float(x["result"]["used_cpu"])

        xx += 1

    total_hddpct = pct_hdd / xx
    total_rampct = pct_ram / xx
    total_cpupct = pct_cpu / xx


    output = render_template('graphs.html',
                             growth=stats['user_data'],
                             utoday=stats['users_today'],
                             ptoday=stats['purchases_today'],
                             server=sstats,
                             revenue=stats['payments_data'],
                             total=stats['purchases_usd'],
                             total_cpu=total_cpupct,
                             total_hdd=total_hddpct,
                             total_ram=total_rampct)
    return output




@app.route("/api/ServStats")
@crossdomain(origin='*')
def servstats():
    db = MySQLdb.connect("db.freebieservers.com","root","Fuc5M4n15!","gcp2")
    cursor = db.cursor()
    fetch = "SELECT * FROM fbs_servers WHERE windows = '0'"
    cursor.execute(fetch)
    list = cursor.fetchall()

    list_res = []
    for row in list:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(row[2],username='root',password='jajbsdddsd32555339f99cgggvcdad1f')
        x = True
        if x == (False): # the ip check
            cmd1 = "df -hl | grep \"/home$\""
        else:
            cmd1 = "df -hl | grep \"/$\"" # just let it  always pull this one for now, my mic is muted atm but i can hear u

        stdin,stdout,stderr = ssh.exec_command(cmd1)

        data0 = str(stdout.readlines()).split(' ')
        while '' in data0:
            data0.remove('')

        if re.match("^[A-Za-z0-9/]*$", data0[0]):
            data0.remove(data0[0])

        spaceFree = data0[len(data0)-3] # continue...
        usedPct = data0[len(data0)-2]
        stdin2,stdout2,stderr2 = ssh.exec_command("free | awk 'FNR == 3 {print $3/($3+$4)*100}'")

        freeRam = stdout2.readlines()
        stdin3,stdout3,stderr3 = ssh.exec_command("top -d 0.1 -b -n2 -p 1 | fgrep \"Cpu(s)\" | tail -1 | awk -F'id,' -v prefix=\"$prefix\" '{ split($1, vs, \",\"); v=vs[length(vs)]; sub(\"%\", \"\", v); printf \"%s%.1f%%\", prefix, 100 - v }'")
        cpu = stdout3.readlines()
        ssh.close()

        free_space = spaceFree
        used_pct = usedPct.strip('%')
        free_ram = freeRam[0].strip('\n')
        used_cpu = cpu[0].strip('%')

        list_res.append({
            # we can just omit data and error for now i think
            'data':
            {
                "id": row[0],
                "name": row[1],
                "ipaddress": row[2],
                "flags": row[3],
                "windows": row[4],
                "is_default": row[5]
            },
            'result':
             {
                'online': True,
                'free_space': free_space,
                "used_pct": used_pct,
                "free_ram": free_ram,
                "used_cpu": used_cpu
            }
        })

    return json.dumps(list_res)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    # choice = 1
    # form = xForm()
    # admin = None
    stats = apireq("http://freebieservers.com/api/SeekStats?user=testest&pass=testest")
    #sstats = apireq("http://freebieservers.com/api/SeekServers?user=testest&pass=testest")
    # xx = 0
    # pct_hdd = 0
    # pct_ram = 0
    # pct_cpu = 0
    # for x in sstats:
    #      pct_hdd += float(x["result"]["used_pct"])
    #      pct_ram += float(x["result"]["free_ram"])
    #      pct_cpu += float(x["result"]["used_cpu"])
    #
    #      xx += 1
    #
    # total_hddpct = pct_hdd / xx
    # total_rampct = pct_ram / xx
    # total_cpupct = pct_cpu / xx


    # if 'user_id' in session:
    #     g.user = User.query.get(session['user_id'])
    #     #admin = g.user.admin

    output = render_template('index.html',growth=stats['user_data'],utoday=stats['users_today'],ptoday=stats['purchases_today'],revenue=stats['payments_data'],total=stats['purchases_usd'])
    flash("errors")
    return output


def apireq(url):
    x = requests.get(url).json()
    return x



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

    if sz == "1":
        for server in sstats:
            if server['data']['id'] == 1:
                sload = server["result"]["used_cpu"]
                sram = server["result"]["free_ram"]
                shdd = server["result"]["used_pct"]
                shddf = server["result"]["free_space"]

    if sz:
        if sz == "2":
            for server in sstats:
                if server['data']['id'] == 2:
                    sload = server["result"]["used_cpu"]
                    sram = server["result"]["free_ram"]
                    shdd = server["result"]["used_pct"]
                    shddf = server["result"]["free_space"]
    if sz:
        if sz == "4":
            for server in sstats:

                if int(server['data']['id']) == 4:
                    sload = server["result"]["used_cpu"]
                    sram = server["result"]["free_ram"]
                    shdd = server["result"]["used_pct"]
                    shddf = server["result"]["free_space"]

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin
    output = render_template('index.html',form=form,growth=stats['user_data'],utoday=stats['users_today'],ptoday=stats['purchases_today'],servers=sstats,total=stats['purchases_usd'],load=sload,ram=sram,hdd=shdd,free=shddf)

    flash("errors")
    return output




@app.route('/hdd', methods=['GET', 'POST'])
def hdd():
    choice = 2
    form = xForm()
    admin = None
    #sl = requests.get("http://127.0.0.1:5000/api/ServStats")
    #sstats = sl.json()

    output = render_template('hdd.html')


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
    if srv == "1":
        r = requests.get('http://freebieservers.com/api/SeekChangeDefault?user=testest&pass=testest&idserv=1')
        print r
    if srv == "2":
        r = requests.get('http://freebieservers.com/api/SeekChangeDefault?user=testest&pass=testest&idserv=2')
        print r
    if srv == "4":
        r = requests.get('http://freebieservers.com/api/SeekChangeDefault?user=testest&pass=testest&idserv=4')
        print r
    if srv == "3":
        r = requests.get('http://freebieservers.com/api/SeekChangeDefault?user=testest&pass=testest&idserv=%s'%randomize())
        print r

    output = render_template('hdd.html',username=g.user,form=form,admin=admin,page=choice,servers=sstats)

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin
        output = render_template('hdd.html',username=g.user,form=form,admin=admin,page=choice,servers=sstats)

    flash("errors")
    return output

def randomize():
    x = random.randint(0,4)
    if x == 3:
        randomize()
    else:
        return x



@app.route('/hdd/seeker/go', methods=['GET', 'POST'])
def hddseeker():
    form = xForm()
    admin = None
    choice = 2
    sl = requests.get("http://freebieservers.com/api/SeekServers?user=testest&pass=testest")
    sstats = sl.json()

    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
    r = requests.get("http://freebieservers.com:62992/api/SeekUsers?user=testest&pass=testest")
    results = r.json()
    output = render_template('hdd.html',form=form,page=2,servers=sstats)

    flash("errors")
    return output

@app.route('/email', methods=['GET', 'POST'])
def email():
    choice = 3
    form = xForm()
    admin = None

    #sr = requests.get("http://freebieservers.com/api/SeekStats?user=testest&pass=testest")
    #stats = sr.json()
    #sl = requests.get("http://freebieservers.com/api/SeekServers?user=testest&pass=testest")
    #sstats = sl.json()

    output = render_template('email.html',emailsent=False,form=form)

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





@app.route("/fdl")
def fdl():
    choice = 5
    form = fdlform()
    admin = None
    output = render_template('fdl.html',username=g.user,form=form,admin=admin,page=choice,ret=None)


    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        #admin = g.user.admin
        output = render_template('fdl.html',username=g.user,form=form,admin=admin,page=choice,ret=None)

    flash("errors")
    return output

@app.route("/fdl/go", methods=['GET', 'POST'])
def fdlgo():
    form = fdlform()
    pw = None
    cid = None
    output = render_template('fdl.html',form=form,ret=None)
    if form.clientname.data:
        if "client" in form.clientname.data:
            cid = form.clientname.data
            db = MySQLdb.connect("db.freebieservers.com","root","Fuc5M4n15!","gamecp")
            db2 = MySQLdb.connect("db.freebieservers.com","root","Fuc5M4n15!","gcp2")
            cursor = db.cursor()
            fetch = "SELECT * FROM users WHERE username = '%s'"%cid
            cursor.execute(fetch)
            list = cursor.fetchall()
            for row in list:
                email = row[2]
                cursor2 = db2.cursor()
                fetch2 = "SELECT * FROM fbs_users WHERE email = '%s'"%email
                cursor2.execute(fetch2)
                user = cursor2.fetchall()
                pw = user[0][13]

            ssh('useradd -m -d /home/html/%s-fdl -s /sbin/nologin -U %s-fdl'%(cid,cid))
            ssh('echo "%s-fdl:%s" | /usr/sbin/chpasswd'%(cid,pw))
            ssh('mkdir /home/html/%s-fdl'%cid)
            ssh('chown -R %s-fdl:%s-fdl /home/html/%s-fdl'%(cid,cid,cid))
            ssh('chmod 777 -R /home/html/%s-fdl'%(cid))

            print('FDL Generated, Username: %s-fdl'%(cid))
            ret = ["FDL Generated:","Username: %s-fdl\n"%(cid),"Password: %s\n"%pw,"URL: http://kc1.freebieservers.com/%s-fdl/\n"%(cid)]
            output = render_template('fdl.html',form=form,ret=ret)


    return output


@app.route("/mods")
def mods():
    db = MySQLdb.connect("db.freebieservers.com","root","Fuc5M4n15!","gamecp")
    cursor = db.cursor()
    fetch = "SELECT * FROM servers WHERE ip != '0'"
    cursor.execute(fetch)
    list = cursor.fetchall()
    for table in list:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(table[2],username='root',password='jajbsdddsd32555339f99cgggvcdad1f')
        fetch2 = "SELECT * FROM usergames WHERE id != '0'"
        fetch3 = "SELECT * FROM game WHERE id != '0'"
        cursor.execute(fetch2)
        listu = cursor.fetchall()
        cursor.execute(fetch3)
        listg = cursor.fetchall()
        for x in listu:
            if str(x[24]) != "garrysmod" and x[24] != "minecraft" and x[24] != "spaceengi" and x[24] != "bukkit" and x[24] != "forge" and x[24] != "KFmod" and x[24] != "modernwarfare" and x[24] != "fof" and x[24] != "unturned" and x[24] != "Rust":
                for y in listg:
                    if x[24] == y[2]:
                        gt = y[6]
                ssh.exec_command("rm -rf /home/client" + str(x[1]) + "/service" + str(x[0]) + "/" + str(gt) + "/" + str(x[24]) + "/addons/sourcemod/plugins/motdgd_adverts.smx")
                ssh.exec_command("cp -R /home/gcp/installs/csgo/csgo/addons/sourcemod/plugins/motdgd_adverts.smx /home/client" + str(x[1]) + "/service" + str(x[0]) + "/" + str(gt) + "/" + str(x[24]) + "/addons/sourcemod/plugins/")
                print("rm -rf /home/client" + str(x[1]) + "/service" + str(x[0]) + "/" + str(gt) + "/" + str(x[24]) + "/addons/sourcemod/plugins/motdgd_adverts.smx")
                print("cp -R /home/gcp/installs/csgo/csgo/addons/sourcemod/plugins/motdgd_adverts.smx /home/client" + str(x[1]) + "/service" + str(x[0]) + "/" + str(gt) + "/" + str(x[24]) + "/addons/sourcemod/plugins/")
    return "Executed"


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


def ssh(command):
    db = MySQLdb.connect("db.freebieservers.com","root","Fuc5M4n15!","gamecp")
    cursor = db.cursor()
    fetch = "SELECT * FROM servers WHERE ip != '0'"
    cursor.execute(fetch)
    list = cursor.fetchall()
    for table in list:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(table[2],username='root',password='jajbsdddsd32555339f99cgggvcdad1f')
        ssh.exec_command(command)





stripe_keys = {
        'secret_key': "sk_live_GFHD3hslyrBiTy9I2HCEIP7y",
        'publishable_key': "pk_live_MjOyhptp99TO2UUMypnJwckz"
    }




@app.route("/stripe", methods=['GET', 'POST'])
def stripe():
    print '--- got stripe request ---'
    stripe.api_key = stripe_keys['secret_key']
    form = stripeform()
    output = render_template('stripe.html', key=stripe_keys['publishable_key'], form=form)
    if form.amount.data:
        drill("xTcR Donation","Thanks for donating to xTcR!",request.form["stripeEmail"])
        #stripe.api_key = "sk_test_KBnACrVyXtFPcHyGTd5cot9D"

        customer = Customer.create(
            email= request.form["stripeEmail"],
            card=request.form['stripeToken']
        )

        charge = Charge.create(
            customer=customer.id,
            amount=form.amount.data * 100,
            currency='usd',
            description='xTcR Donation'
        )


        custom = '0'
        if request.form.has_key('custom'):
            custom = str(request.form['custom'])

        cb_data = {
             #'app': 'donate',
             #'do': 'payment',
             #'gateway': '1',
             'mc_gross': float(charge['amount']) / 100,
             'mc_currency': charge['currency'],
             'custom': custom,
             'payment_status': 'Completed' if charge['status'] == 'succeeded' else charge['status'],
             'business': charge['receipt_email'],
             'option_selection1': '',
             'option_selection2': '',
             'txn_id': charge['id'],
             'memo': 'stripe',
             'fees': (float(charge['amount']) / 100) * 0.029 + 0.30,
             'item_name': str(request.form['item_name']),
             'item_number': str(request.form['item_number'])
        }

        r = requests.post("http://192.210.138.77/index.php?app=donate&do=payment&gateway=1", data=cb_data)

        print ' ----- '
        cmd("echo '%s' >> stripe.log"%r.text)

        output = redirect("http://xtcr.net/success.html")


    return output


@app.route('/gcp')
def gcp():
    output = "fuck GCP"

    return output


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
