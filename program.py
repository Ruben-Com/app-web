import requests, re, pymongo, time, datetime, hashlib, http.client, random, urllib.parse, json
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "ayush"  
api_key = "19b609d0-19c2-3844-b7c7-f88cee74648d"
api_key_dash = "695ae44b-9cd8-3cde-8d19-fc2cb2937a5c"
component_id = "eur-usd"
base_url = '/api/feed?'
conn = http.client.HTTPConnection('www.grovestreams.com')

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["servidor"]
mycol_val = mydb["euro"]
mycol_usr = mydb["users"]

def recoger_valor():
    r = requests.get("http://es.investing.com/currencies/")
    valor = float((str(re.findall("pid-1-last..(\d,\d{4})", r.text))[2:-2]).replace(",", "."))
    mydict = {"value": valor, "time": datetime.datetime.now()}
    x = mycol_val.insert_one(mydict)

    now = datetime.datetime.now()
    sample_time = int(time.mktime(now.timetuple()))*1000
    url = base_url + urllib.parse.urlencode({'compId': 'eur-usd', 'value': valor, 'time': sample_time})
    headers = {"Connection": "close", "Content-type": "application/json", "Cookie":"api_key="+api_key}
    conn.request("PUT", url, "", headers)
    response = conn.getresponse()
    conn.close()
    
sched = BackgroundScheduler(daemon=True)
sched.add_job(recoger_valor, 'interval', minutes=2)
sched.start()

@app.route("/")
def index():
    r = requests.get("http://es.investing.com/currencies/")
    valor = float((str(re.findall("pid-1-last..(\d,\d{4})", r.text))[2:-2]).replace(",", "."))
    if 'username' in session and 'email' in session:  
        return render_template('index_log.html', value=valor, usuario=("Sesión con el usuario: "+session['username']))
    else:
        return render_template('index_not_log.html', value=valor)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    if request.method == "POST":
        email = request.form.get('email')
        if len(list(mycol_usr.find({"email": email}))) == 0:
            session['email']=email  
            name = request.form.get('name')
            session['username']=name  
            password = hashlib.sha256(request.form.get('pass').encode()).hexdigest()
            mydict = {"email": email, "username": name, "password": password, "local_mean": 0, "remote_mean": 0}
            x = mycol_usr.insert_one(mydict)
            usuario="Sesión con el usuario: "+name
            r = requests.get("http://es.investing.com/currencies/")
            valor = float((str(re.findall("pid-1-last..(\d,\d{4})", r.text))[2:-2]).replace(",", "."))
            mydict = {"value": valor, "time": datetime.datetime.now()}
            x = mycol_val.insert_one(mydict)
            return render_template('index_log.html', value=valor, usuario=usuario)
        else:
            mensaje="Ya existe un usuario con el email utilizado"
            return render_template('register.html', mensaje=mensaje)

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'username' in session and 'email' in session:  
        r = requests.get("http://es.investing.com/currencies/")
        valor = float((str(re.findall("pid-1-last..(\d,\d{4})", r.text))[2:-2]).replace(",", "."))
        mydict = {"value": valor, "time": datetime.datetime.now()}
        x = mycol_val.insert_one(mydict)
        return render_template('index_log.html', value=valor, usuario="")
    else:
        if request.method == "GET":
            return render_template('login.html', mensaje="")
        if request.method == "POST":
            email = request.form.get('email')
            session['email']=email  
            password = hashlib.sha256(request.form.get('pass').encode()).hexdigest()
            if len(list(mycol_usr.find({"email": email, "password": password}))) == 0:
                mensaje="El usuario especificado no existe, pruebe con otro"
                return render_template('login.html', mensaje=mensaje)
            else:
                for x in mycol_usr.find({"email": email, "password": password}):
                    name = x["username"]
                session['username']=name  
                return render_template('success.html', usuario=name)

@app.route("/logout")
def logout():
    if 'username' in session and 'email' in session:  
        session.pop('username',None)  
        session.pop('email',None)  
        return render_template('logout.html', sesion="Sesión cerrada correctamente")
    else:  
        return render_template('logout.html', sesion="No había sesión iniciada")

@app.route("/profile")
def profile():
    for x in mycol_usr.find({"email": session['email'], "username": session['username']}):
        local = x["local_mean"]
        remote = x["remote_mean"]
    return render_template('profile.html', email=session['email'], local_mean=local, remote_mean=remote)

@app.route("/success", methods=['GET', 'POST'])
def success():
    return render_template('success.html')

@app.route("/media", methods=['POST'])
def media():
    base = request.form.get('base')
    if base=="local":
        for x in mycol_usr.find({"email": session['email'], "username": session['username']}):
            num = x["local_mean"]
        num=num+1
        mycol_usr.update_one({"email": session['email'], "username": session['username']},{"$set":{"local_mean": num}})
        suma=0
        cuenta=0
        for valores in mycol_val.find({},{"_id": 0, "time": 0}):
            suma=suma+float(valores["value"])
            cuenta=cuenta+1
    if base=='remota':
        for x in mycol_usr.find({"email": session['email'], "username": session['username']}):
            num = x["remote_mean"]
        num=num+1
        mycol_usr.update_one({"email": session['email'], "username": session['username']},{"$set":{"remote_mean": num}})
        url = "/api/comp/eur-usd/feed?"
        headers = {"Connection": "close", "Content-type": "application/json", "Cookie":"api_key="+api_key}
        conn.request("GET", url, "", headers)
        response = conn.getresponse()
        conn.close()
        suma=0
        cuenta=0
        for valores in json.loads(str(response.read().decode(encoding='UTF-8'))):
            suma=suma+float(valores["data"])
            cuenta=cuenta+1
    return render_template('media.html', base=base, media=round((suma/cuenta), 4) )

@app.route("/graphic")
def graphic():
    return render_template('graphic.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
