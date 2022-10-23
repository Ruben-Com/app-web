import requests, re, pymongo, time, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template
app = Flask(__name__)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["servidor"]
mycol = mydb["euro"]

valor = 0.0

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
    return render_template('index.html', value=valor)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
