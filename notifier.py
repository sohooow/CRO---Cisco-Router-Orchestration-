from config import Configuration
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Notifier():

    def __init__(self):
        self.config = Configuration()
        self.server = SMTP(
            self.config['SMTP_SERVER'], self.config['SMTP_PORT'], timeout=10)

    def send(self,recipients,subject,body):
        for people in recipients:
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['To'] = people
            msg.attach(MIMEText(body, 'plain'))
            self.server.sendmail(
                self.config['NoReplyEmail'], people, msg.as_string())
