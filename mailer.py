from flask import current_app, url_for, copy_current_request_context
from flask_mail import Mail, Message
import threading 

mail = Mail(current_app)

def send_async(message):

    @copy_current_request_context
    def send_message(message):
        mail.send(message)

    sender = threading.Thread(name='mail_sender', target=send_message, args=(message,))
    sender.start()

def sendActivationMail(sender, token) :
    msg = Message(   
            "NANCY - ACCOUNT ACTIVATION",
            sender="nancy@hexoid.com",
            recipients=[sender],
            body = f"""
            Hi there,
                This is Nancy, Hope youre having a great day. It is a plesure to welocme you into our team.
                Please activate your account using the link provided below : 
                {current_app.config['BASE_URL'] +  url_for('auth.activate', token=token)}
            """
    )
    send_async(msg)


def sendPasswordResetMail(sender, token) :
    msg = Message(   
            "NANCY - ACCOUNT ACTIVATION",
            sender="nancy@hexoid.com",
            recipients=[sender],
            body = f"""
            Hi there,
                This is Nancy, 
                We heard you hve forgotten your password, to forget is only human but transceding beyond Human is being Nancy.
                Anyways here is the link to reset your password : 
                {current_app.config['BASE_URL'] +  url_for('auth.resetPassword', token=token)}
            """
        )
    send_async(msg)


