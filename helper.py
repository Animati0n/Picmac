import smtplib,ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv() 

def sndmail(uname,msg,subject):
    port = 465  # For SSL
    #password = input("Type your password and press enter: ")

    # Create a secure SSL context
    context = ssl.create_default_context()
    msg2 = EmailMessage()
    msg2.set_content(msg)

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(os.getenv('SERVER_LOGIN_EMIL'), os.getenv('SERVER_LOGIN_PASSWORD'))
        message = msg
        msg2['Subject'] = subject
        msg2['From'] = os.getenv('FROM_EMAIL')
        msg2['To'] = uname
        server.send_message(msg2)
    print("workinggg....")


