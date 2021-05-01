from flask import Flask, render_template, request, redirect, url_for, session
import requests
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_mail import Mail, Message
import smtplib, ssl
from email.mime.text import MIMEText
import schedule
import time
app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3308
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'harsh'
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['email'] = account['email']
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
#    msg = Message('Hello', sender = 'rameshsuresh4819@gmail.com', recipients = [session['email']])
#    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#    cursor.execute('SELECT * FROM medica WHERE user = %s', (session['id'],))
#    med = cursor.fetchall()
#    st=""
#    for m in med:
#        if int(m["consquantity"])>0:
#             st+=m['name']+"\t"+m["consquantity"]+"\t"+m["unit"]+"\n"
#             cons=int(m["quantity"])-1
#             cursor.execute('Update medica set quantity=%s  WHERE name = %s', (str(cons),m['name'],))
#             mysql.connection.commit()
#        else:
#            st+=m['name']+"\t"+"is not available.Please buy it."


#    msg.body = "Hello "+session['username']+" this message is sent from Travel-Guide.\nPlease take following dose : \n"+st
#    mail.send(msg)
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        session['lat'] =request.args.get('Latitude',None)
        session['long'] =request.args.get('Longitude',None)
        latiname = str(request.args.get('Latitude',None))
        longiname = str(request.args.get('Longitude',None))
        if latiname == 'None' or longiname == 'None':
            return render_template('home.html',context = {'weatherdesc':[]})
        context = {
            "weatherdesc": weatherf(latiname,longiname)
        }
        return render_template('home.html',context = context)


    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
def weatherf(latiname,longiname):
    import socket
    import requests
    try:
        send =[]
        socket.create_connection( ("www.google.com",80) )
        if(latiname == 'None' and longiname == 'None' ):
            pass
        else:
            a1 = "http://api.openweathermap.org/data/2.5/forecast?"
            a2 = "lat=" + latiname + "&lon=" + longiname
            a3 = "&appid=c6e315d09197cec231495138183954bd"
            api_address = a1 + a2 + a3
            res1=requests.get(api_address)
            data = res1.json()
            list1 = data['list']
            res = [sub['main'] for sub in list1] 
            temp = [t['temp'] for t in res]
            hum = [t['humidity'] for t in res]
            mini = [t['temp_min'] for t in res]
            maxim = [t['temp_max'] for t in res]
            time = [sub['dt_txt'] for sub in list1]  
            degree_sign = u"\N{DEGREE SIGN}" + "C"
            weather = [sub['weather'] for sub in list1] 
            wind = [sub['wind']for sub in list1]
            windspeed = [sub['speed']for sub in wind]
            weatherm,weatherd,icon = [],[],[]
            for i in range(len(temp)):
                for sub in weather[i]:
                    weatherm.append(sub['main'])
                    weatherd.append(sub['description'])
            #for i in range(len(temp)):
            a11 = "http://api.openweathermap.org/data/2.5/air_pollution/forecast?"
            a22 = "lat=" + latiname + "&lon=" + longiname
            a33 = "&appid=c6e315d09197cec231495138183954bd"
            api_address1 = a11 + a22 + a33
            res=requests.get(api_address1)
            data1 = res.json()
            list2 = data1['list']
            res2 = [sub1['main'] for sub1 in list2]
            aqi = [a['aqi'] for a in res2]
            send.append([time,temp,mini,maxim,hum,weatherm,weatherd,windspeed,aqi])
            temperature_in_fahrenheit = temp[0]
            humidity_in_rh = hum[0]
            seeds(temperature_in_fahrenheit,humidity_in_rh)

        # for i in range(len(temp)):
        #     print("time = ",time[i],"temp = ", temp[i], degree_sign,"humidity = ",hum[i],"%", "min = ", mini[i], degree_sign, "max = ",maxim[i], degree_sign, "weather = ",weatherm[i],"desc = ",weatherd[i], "image= ",icon[i])
    except KeyError as k:
        print("City Not Found")
    except OSError as e:
        print("check network ",e)
    return send

mail_sent=0
def sendmail(temp_str,hum_str):
        message = 'TEMPERATURE HAS REACHED: '+ temp_str +'F' + '\n HUMIDITY HAS REACHED: ' + hum_str +'rh'
        to ="harshk9800@gmail.com"   
        subject="WEATHER ALERT"     
        text = message
        sender = 'manasi.jadhav@spit.ac.in'
        password = '2018140025'
        message='Subject: {}\n\n{}'.format(subject,text)
        server = smtplib.SMTP_SSL('smtp.gmail.com',465)
        server.ehlo()
        server.login(sender,password)
        print('logged in')
        try:
                server.sendmail(sender,to,message)
                print('email sent')
                mail_sent=1
        except:
                print('error sending mail')
        server.quit

def seeds(temperature_in_fahrenheit,humidity_in_rh):
        global mail_sent
        if temperature_in_fahrenheit > 90 or temperature_in_fahrenheit < 50:
                if mail_sent == 0:
                        temp_str = str(temperature_in_fahrenheit)
                        hum_str = str(humidity_in_rh)
                        sendmail(temp_str,hum_str)
                        return
                return

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM medica WHERE user = %s', (session['id'],))
        med = cursor.fetchall()
        # Show the profile page with account info
        return render_template('profile.html', account=account,med=med)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
@app.route('/medic', methods=['GET', 'POST'])
def medic():
     # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'mdname' in request.form and 'mdquantity' in request.form and 'mdunits' in request.form and 'mdfrequency' in request.form and 'mdconsquantity' in request.form:
        # Create variables for easy access
        name = request.form['mdname']
        quan = request.form['mdquantity']
        unit = request.form['mdunits']
        freq = request.form['mdfrequency']
        cons = request.form['mdconsquantity']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM medica WHERE name = %s', (name,))
        account = cursor.fetchone()
        print(name)
        # If account exists show error and validation checks
        if account:
            msg = 'Medication already exists!'
        elif not name or not quan or not unit or not freq:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO medica VALUES (NULL, %s, %s,%s, %s,%s,%s)', (name, quan, cons,unit,freq,session['id'],))
            mysql.connection.commit()
            msg = 'Medication added successfully!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    return render_template('medicineForm.html',msg=msg)
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        name=request.form["mdname"]
        cursor.execute('Delete from medica where name=%s', (name,))
        mysql.connection.commit()
        cursor.execute('SELECT * FROM medica WHERE user = %s', (session['id'],))
        med = cursor.fetchall()

    return render_template('profile.html', account=account,med=med)

@app.route('/ambulance')
def ambulance():
    URL = "https://discover.search.hereapi.com/v1/discover"
    latitude = session['lat']
    longitude = session['long']
    print(latitude,longitude)
    api_key = 'QnBBA1vjPqJTkYI7CqWB-b9oA25zZf5jfCandU7ZVn4' # Acquire from developer.here.com
    query = 'hospitals'
    limit = 5

    PARAMS = {
                'apikey':api_key,
                'q':query,
                'limit': limit,
                'at':'{},{}'.format(latitude,longitude)
            } 

    # sending get request and saving the response as response object 
    r = requests.get(url = URL, params = PARAMS) 
    data = r.json()


    hospitalOne = data['items'][0]['title']
    hospitalOne_address =  data['items'][0]['address']['label']
    hospitalOne_latitude = data['items'][0]['position']['lat']
    hospitalOne_longitude = data['items'][0]['position']['lng']


    hospitalTwo = data['items'][1]['title']
    hospitalTwo_address =  data['items'][1]['address']['label']
    hospitalTwo_latitude = data['items'][1]['position']['lat']
    hospitalTwo_longitude = data['items'][1]['position']['lng']

    hospitalThree = data['items'][2]['title']
    hospitalThree_address =  data['items'][2]['address']['label']
    hospitalThree_latitude = data['items'][2]['position']['lat']
    hospitalThree_longitude = data['items'][2]['position']['lng']


    hospitalFour = data['items'][3]['title']
    hospitalFour_address =  data['items'][3]['address']['label']
    hospitalFour_latitude = data['items'][3]['position']['lat']
    hospitalFour_longitude = data['items'][3]['position']['lng']

    hospitalFive = data['items'][4]['title']
    hospitalFive_address =  data['items'][4]['address']['label']
    hospitalFive_latitude = data['items'][4]['position']['lat']
    hospitalFive_longitude = data['items'][4]['position']['lng']
    return render_template('map.html',latitude=latitude,longitude=longitude,apikey=api_key,oneName=hospitalOne,OneAddress=hospitalOne_address,oneLatitude=hospitalOne_latitude,oneLongitude=hospitalOne_longitude,twoName=hospitalTwo,twoAddress=hospitalTwo_address,twoLatitude=hospitalTwo_latitude,twoLongitude=hospitalTwo_longitude,threeName=hospitalThree,threeAddress=hospitalThree_address,threeLatitude=hospitalThree_latitude,threeLongitude=hospitalThree_longitude,fourName=hospitalFour,fourAddress=hospitalFour_address,fourLatitude=hospitalFour_latitude,fourLongitude=hospitalFour_longitude,fiveName=hospitalFive,fiveAddress=hospitalFive_address,fiveLatitude=hospitalFive_latitude,fiveLongitude=hospitalFive_longitude)

if __name__ == '__main__':
    app.run(debug=True)
