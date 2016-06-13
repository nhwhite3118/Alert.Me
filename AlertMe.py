import config
from urllib.request import urlopen
import json
import pymysql
import time
import smtplib

conn = pymysql.connect(host="127.0.0.1", user=config.DB_USER, passwd=config.DB_PASSWORD, db="alertme")


def sendAlerts():
    print("time - " + time.ctime())
    cur = conn.cursor()
    cur.execute("SELECT * FROM user")

    for user in cur:
        number = user[0]
        portal = user[1]
        match = user[2]
        site = user[3]
        fSite=site
        if(not "www." in site):
            fSite = "www."+site
        if(not "http://" in fSite):
            fSite = "http://"+fSite
        notSpam = fSite.replace("http://","").replace("https://","").replace("www.","")
        print(site)
        if checkSite(match,fSite):
            sql = "DELETE FROM user WHERE number=%s AND portal =%s AND matchstr=%s AND site=%s;"
            v = (number,portal,match,site)
            cur.execute(sql,v)
            conn.commit()
            #sendEmailSms(number + "@" + portal, "Your AlertMe alert for "+match+" at " + str(notSpam)+ " has gone off!")
            sendEmailSms(number + "@" + portal, "Your AlertMe alert for "+match+" has gone off!")


def checkSite(match,site):
    f = urlopen(site)
    siteString = f.read().decode('utf-8')
    f.close()
    return match in siteString

#TODO: make alertme email
def sendEmailSms(recipient, body):
    gmailUser = 'thunderbuddyproject@gmail.com'
    gmailPassword = config.EMAIL_PASSWORD
    to = recipient if type(recipient) is list else [recipient]

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmailUser, gmailPassword)
        server.sendmail(gmailUser, to, body)
        server.close()
        print("successfully sent email to - " + str(to))
    except:
        print("failed to send email to - " + str(to))


sendAlerts()
