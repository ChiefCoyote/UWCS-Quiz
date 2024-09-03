from flask_mail import Mail, Message

mail = Mail()

def sendEmail(subject, sender, recipient, html):
    msg = Message(subject, sender=sender, recipients=[recipient])
    msg.html = html
    mail.send(msg)