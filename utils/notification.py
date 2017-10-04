import os
import sendgrid
from sendgrid.helpers.mail import *
from twilio.rest import Client

class notification():
    sendgrid_key = os.environ.get('sendgrid_apikey') or "none"
    twillio_account_sid = os.environ.get('twillio_account_sid') or "none"
    twillio_auth_token  = os.environ.get('twillio_auth_token') or "none"
    twillio_number = os.environ.get('twillio_number') or "none"
    
    @staticmethod   
    def sendMail(fromEmail, toEmail, subject, contentType, content):
        sg = sendgrid.SendGridAPIClient(apikey=notification.sendgrid_key)

        from_email = Email(fromEmail)
        to_email = Email(toEmail)
        content = Content(contentType, content)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        return response

    @staticmethod
    def sendText(toNumber, content):
        twillio_client = Client(notification.twillio_account_sid, notification.twillio_auth_token)

        message = twillio_client.messages.create(
        to="+1"+toNumber, 
        from_=notification.twillio_number,
        body=content)
        return message