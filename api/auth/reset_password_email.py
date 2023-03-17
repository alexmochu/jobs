from flask_mail import Message

msg = Message('Subject', recipients=['recipient@example.com'])
msg.body = 'Body'
mail.send(msg)