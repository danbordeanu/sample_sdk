import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import Encoders
import helpers.config_parser as parser
from helpers import logger_settings


def send_mail(send_from, send_to, subject, text, files=(), server=parser.config_params('smtp')['server']):
    '''
    This function will send emails with the results of the test
    :param send_from:
    :param send_to:
    :param subject:
    :param text:
    :param files:
    :param server:
    :return:
    '''
    if type(send_to) != list:
        raise Exception('send_to must be of type list')
    if type(files) != list and type(files) != tuple:
        raise Exception('files must be of type list')

    if len(send_to) == 0:
        logger_settings.logger.info('Empty list of recipients. Aborting the send_mail().')
        return

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename=\'%s\'' % (os.path.basename(f)))
        msg.attach(part)

    try:
        smtp = smtplib.SMTP(server)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
    except smtplib.SMTPSenderRefused, e:
        logger_settings.logger.error('The email was refused:{0}'.format(str(e)))
    except Exception, e:
        logger_settings.logger.error('The email couldn\'t be sent:{0}'.format(str(e)))
