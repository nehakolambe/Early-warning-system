import smtplib, ssl
from email.mime.text import MIMEText
import mysql.connector
import schedule
import time

sender_email = 'rameshsuresh4819@gmail.com'
password = "Mayur@21"

db = mysql.connector.connect(
    host='localhost',
    port=3308,
    user='root',
    password='harsh',
    database='pythonlogin'
)
cursor = db.cursor()

def critical_stock_warning(recipientsEmail, recipientsName, mName, mQuantity):
    msg = MIMEText(f"Hello {recipientsName[0]}, your supply for {mName[0]} is critically low.\nQuantity = {mQuantity[0]}/-")
    msg['Subject'] = f"Critical Stock Warning!"
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipientsEmail)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipientsEmail, msg.as_string())

def no_stock_warning(recipientsEmail, recipientsName, mName):
    msg = MIMEText(f"Hello {recipientsName[0]}, your supply for {mName[0]} is over.")
    msg['Subject'] = f"No supply for {mName[0]}!"
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipientsEmail)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipientsEmail, msg.as_string())


def send_email(recipientsEmail, recipientsName, mName, consQuantity, mQuantity):

    if(int(mQuantity[0]) < int(consQuantity[0])):
        # Stock Over
        no_stock_warning(recipientsEmail, recipientsName, mName)
        return

    elif(int(mQuantity[0]) - int(consQuantity[0]) == 0 or int(mQuantity[0]) - int(consQuantity[0]) < int(consQuantity[0])):
        # critical stock warning
        critical_stock_warning(recipientsEmail, recipientsName, mName, mQuantity)
        
    newQuantity = int(mQuantity[0]) - int(consQuantity[0])
    cursor.execute(f'Update medica set quantity={str(newQuantity)}  WHERE name = "{mName[0]}" ')
    db.commit()

    msg = MIMEText(f"Hello {recipientsName[0]}, take your {mName[0]} Quantity = {consQuantity[0]}/-")
    msg['Subject'] = f"Medication Reminder"
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipientsEmail)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipientsEmail, msg.as_string())


def daily_notif():
    recipientsEmail = []
    recipientsName = []
    mName = []
    mQuantity = []
    consQuantity = []
    # fetch email info 
    cursor.execute('select email from accounts where id in (select user from medica where frequency="Daily")')
    for x in cursor:
        recipientsEmail.append(x)
    
    # fetch email info 
    cursor.execute('select username from accounts where id in (select user from medica where frequency="Daily")')
    for x in cursor:
        recipientsName.append(x)

    # fetch medication name
    cursor.execute('select name from medica where frequency="Daily"')
    for x in cursor:
        mName.append(x)

    # fetch medication quantity
    cursor.execute('select quantity from medica where frequency="Daily"')
    for x in cursor:
        mQuantity.append(x)
    
    # fetch consumption medication quantity
    cursor.execute('select consquantity from medica where frequency="Daily"')
    for x in cursor:
        consQuantity.append(x)

    for i in range(len(recipientsEmail)):
        send_email(recipientsEmail[i], recipientsName[i], mName[i], consQuantity[i], mQuantity[i])
    
def once_every_2_days_notif():
    recipientsEmail = []
    recipientsName = []
    mName = []
    mQuantity = []
    consQuantity = []
    # fetch email info 
    cursor.execute('select email from accounts where id in (select user from medica where frequency="Once, every 2 days")')
    for x in cursor:
        recipientsEmail.append(x)
    
    # fetch email info 
    cursor.execute('select username from accounts where id in (select user from medica where frequency="Once, every 2 days")')
    for x in cursor:
        recipientsName.append(x)

    # fetch medication name
    cursor.execute('select name from medica where frequency="Once, every 2 days"')
    for x in cursor:
        mName.append(x)

    # fetch medication quantity
    cursor.execute('select quantity from medica where frequency="Once, every 2 days"')
    for x in cursor:
        mQuantity.append(x)
    
    # fetch consumption medication quantity
    cursor.execute('select consquantity from medica where frequency="Once, every 2 days"')
    for x in cursor:
        consQuantity.append(x)

    for i in range(len(recipientsEmail)):
        send_email(recipientsEmail[i], recipientsName[i], mName[i], consQuantity[i], mQuantity[i])

def weekely_notif():
    recipientsEmail = []
    recipientsName = []
    mName = []
    mQuantity = []
    consQuantity = []
    # fetch email info 
    cursor.execute('select email from accounts where id in (select user from medica where frequency="Weekly")')
    for x in cursor:
        recipientsEmail.append(x)
    
    # fetch email info 
    cursor.execute('select username from accounts where id in (select user from medica where frequency="Weekly")')
    for x in cursor:
        recipientsName.append(x)

    # fetch medication name
    cursor.execute('select name from medica where frequency="Weekly"')
    for x in cursor:
        mName.append(x)

    # fetch medication quantity
    cursor.execute('select quantity from medica where frequency="Weekly"')
    for x in cursor:
        mQuantity.append(x)
    
    # fetch consumption medication quantity
    cursor.execute('select consquantity from medica where frequency="Weekly"')
    for x in cursor:
        consQuantity.append(x)

    for i in range(len(recipientsEmail)):
        send_email(recipientsEmail[i], recipientsName[i], mName[i], consQuantity[i], mQuantity[i])
    

schedule.every(1).minutes.do(daily_notif)

schedule.every().day.at("09:00").do(daily_notif)
schedule.every(2).days.at("09:00").do(once_every_2_days_notif) 
schedule.every().monday.at("09:00").do(weekely_notif)

if __name__ == '__main__':

    while True:
        schedule.run_pending()
        time.sleep(1)
