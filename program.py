import requests, re
from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def index():
    r = s.get("http://es.investing.com/currencies/")
    valor = str(re.findall("pid-1-last..(\d,\d{4})", r.text))[2:-2]
    print(str(r.text))
    return render_template('index.html', value=valor)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
