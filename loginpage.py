from flask import Flask, render_template, redirect, request, url_for, session
app = Flask(__name__)  
app.secret_key = "ayush"  
@app.route('/')  
def home():   
  return render_template("homepage2.html")  
@app.route('/login')  
def login():  
  return render_template("loginpage3.html")  
@app.route('/success',methods = ["POST"])   
def success(): 
  if request.method == "POST":  
   session['email']=request.form['email']  
   return render_template('success3.html')  
@app.route('/logout')  
def logout(): 
  if 'email' in session:  
    session.pop('email',None)  
    return render_template('logoutpage2.html');  
  else:  
    return '<p>user already logged out</p>'   
@app.route('/profile')  
def profile():  
   if 'email' in session:  
      email = session['email']  
      return              render_template('profile.html',name=email)   
   else:  
    return '<p>Please login first</p>'  
if __name__ == "__main__":
    #app.run()
    app.run(host='0.0.0.0', port=5000, debug=True)
