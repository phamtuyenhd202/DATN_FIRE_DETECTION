
# -*- coding: utf-8 -*-
"""
Email to SMS Gateway - send SMS
@author: adam getbags
"""


import smtplib
from email.message import EmailMessage

from flask import Blueprint

from emailToSMSConfig import senderEmail, gatewayAddress, appKey


# def sendEmail(Notimessage, notiType):
#     msg = EmailMessage()
#
#
#     msg['From'] = senderEmail  # 'email@address.com'
#     msg['To'] = gatewayAddress  # '1112223333@vmobl.com'
#     # msg['Subject'] = 'CẢNH BÁO'
#     msg['Subject'] = notiType
#
#     #for HTML
#     msg.add_alternative(f"""\
#     <!DOCTYPE html>
#     <html lang="en">
#         <body>
#            <h1>{Notimessage} </h1>
#            <img src="https://bienbaodaian.com/upload/images/Bien-canh-bao/nguy-hiem-chay-no/bien-bao-nguy-hiem-de-chay%20(1).jpg">
#         </body>
#     </html>
#
#
#     """.format(**locals()), subtype= 'html')
#
#
#     with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
#         smtp.login(senderEmail, appKey)
#         smtp.send_message(msg)
#         print("email sucessfully")
#         smtp.quit()

# gửi nhiều email
# import smtplib
# from email.message import EmailMessage
# from emailToSMSConfig import senderEmail, appKey

from app import DAO



def sendEmail(Notimessage, notiType, recipients):
    print(recipients)
    for recipient in recipients:
        msg = EmailMessage()

        msg['From'] = senderEmail
        msg['To'] = recipient['noti_email']
        msg['Subject'] = notiType

        msg.add_alternative(f"""\
            <!DOCTYPE html>
            <html lang="en">
                <body>
                   <h1>{Notimessage}</h1>
                   <img src="https://bienbaodaian.com/upload/images/Bien-canh-bao/nguy-hiem-chay-no/bien-bao-nguy-hiem-de-chay%20(1).jpg">
                </body>
            </html>
            """, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(senderEmail, appKey)
            smtp.send_message(msg)
            print("Email sent successfully")
            smtp.quit()


