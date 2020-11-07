import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendVerificationEmail(email_address,vcode):
	print("Sending Email...")
	subject = "FinancePeer Assignment Verification Code"
	html = """\
	<html>
	  <body>
	    <p><strong>Dear User,</strong></p>
	    <p style="color: red;">Please enter this code.</p>
	    <div style="background-color: grey:">
	    <h1><strong>{}</strong></h1>
	    </div>
	    <p><strong>Thank You<br>Sukhmanjit Singh Mann<br>180050106<br>CSE Department, IIT Bombay</strong></p>
	  </body>
	</html>
	""".format(vcode)
	sender_email = "financepeerfullstacktask@gmail.com"
	receiver_email = email_address
	password = "financePeerFullStack"

	# Create a multipart message and set headers
	message = MIMEMultipart()
	message["From"] = sender_email
	message["To"] = receiver_email
	message["Subject"] = subject
	# message["Cc"] = receiver_email  # Recommended for mass emails

	# Add body to email
	message.attach(MIMEText(html, "html"))
	text = message.as_string()

	# Log in to server using secure context and send email
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
	    server.login(sender_email, password)
	    server.sendmail(sender_email, receiver_email, text)
	print("Email sent...")