from flask import Flask
from flask_mail import Mail, Message
import schedule
import time

app = Flask(__name__)
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'rameshsuresh4819@gmail.com'
app.config['MAIL_PASSWORD'] = 'Mayur@21'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def send_email():
    msg = Message('Sup', sender = 'rameshsuresh4819@gmail.com', recipients = ['nemanog483@donmah.com'])
    msg.body = "Hello Flask message sent from Flask-Mail"
    mail.send(msg)
    return "Sent"
    
# 2 time a day
schedule.every().day.at("10:30").do(send_email)
schedule.every().day.at("16:30").do(send_email)
# every 2 days 
schedule.every(2).days.do(send_email)
# every day
schedule.every().day.at("10:30").do(send_email)
# schedule.every(60).seconds.do(send_email)


@app.route("/")
def index():
    while True:
        schedule.run_pending()
        time.sleep(1)