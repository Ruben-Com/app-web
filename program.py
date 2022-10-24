import requests, re, pymongo, time, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request
from beebotte import *
app = Flask(__name__)
#bclient = BBT("API_KEY", "SECRET_KEY")

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["servidor"]
mycol = mydb["euro"]

correo = ""

def recoger_valor():
    r = requests.get("http://es.investing.com/currencies/")
    valor = float((str(re.findall("pid-1-last..(\d,\d{4})", r.text))[2:-2]).replace(",", "."))
    mydict = {"value": valor, "time": datetime.datetime.now()}
    x = mycol.insert_one(mydict)
    
sched = BackgroundScheduler(daemon=True)
sched.add_job(recoger_valor, 'interval', minutes=2)
sched.start()

@app.route("/")
def index():
    r = requests.get("http://es.investing.com/currencies/")
    valor = float((str(re.findall("pid-1-last..(\d,\d{4})", r.text))[2:-2]).replace(",", "."))
    mydict = {"value": valor, "time": datetime.datetime.now()}
    x = mycol.insert_one(mydict)
    return render_template('index.html', value=valor)

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/logout")
def logout():
    return render_template('logout.html')

@app.route("/profile")
def profile():
    return render_template('profile.html')

@app.route("/success", methods=['GET', 'POST'])
def success():
    return render_template('success3.html')

@app.route("/media", methods=['POST'])
def media():
    base = request.form.get('base')
    if base=="local":
        suma=0
        cuenta=0
        for valores in mycol.find({},{"_id": 0, "time": 0}):
            suma=suma+float(valores["value"])
            cuenta=cuenta+1
    return render_template('media.html', base=base, media=round((suma/cuenta), 4) )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
