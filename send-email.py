import os
import string
import json
import smtplib
from email.mime.text import MIMEText


sender = "rykahsay@gwu.edu"
receivers = ["rykahsay@gmail.com"]

msg = MIMEText("Hi there!")
msg['Subject'] = "test email"
msg['From'] = sender
msg['To'] = receivers[0]

try:
    s = smtplib.SMTP('localhost')
    s.sendmail(sender, receivers, msg.as_string())
    s.quit()
except Exception as e:
    print ({"error_list":[{"error_code":str(e)}]})


