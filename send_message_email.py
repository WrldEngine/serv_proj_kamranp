import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#igry5302@gmail.com
def send_to_email(main_content, toEmail, subject):
    acc_EMAIL = 'medianait.academy.uz@gmail.com'
    acc_PASSWORD = 'tcmlqznbpafrzjam'

    blank = MIMEMultipart()
    blank['Subject'] = subject
    blank.attach(MIMEText(main_content, 'plain'))

    text = blank.as_string()

    Service = smtplib.SMTP('smtp.gmail.com', 587)
    Service.starttls()

    Service.login(acc_EMAIL, acc_PASSWORD)
    Service.sendmail(acc_EMAIL, toEmail, text)

    Service.quit()
    return "Status: ok"