
import base64
from helpers import random_generator as random_generator_function
import helpers.textconsole as report
from helpers import logger_settings
import os
import sys

from helpers.Error import ExceptionType
from helpers.Error import UATError

from helpers.hpcapi_verbs import admin

from tests.AUTHENTICATION.login_test import LoginTest


class InitDataTest(object):
    def __init__(self, parser, GROUP_name, endpoint_name, method_name):
        # parse data
        try:
            self.GROUP_name = GROUP_name
            self.endpoint_name = endpoint_name
            self.method_name = method_name

            self.parser = parser
            self.suite_name = []
            self.suite_name.append(endpoint_name)
            self.test_name = []
            self.result = []
            # if there is no env var for HPC_APIURL, use the one from config.ini
            self.url = os.environ.get('HPC_APIURL', parser.config_params('hpcapi')['url'])

            # Login/users data
            self.login =  LoginTest(parser, 'user_a')
            self.user_a, self.user_b, self.user_c =  self.login.getUsers()
            self.ticket, self.user = self.login.getTicketUser()


            self.accesible_folder = parser.config_params('users_paths')['accesible_folder']
            # if there is no env var SSH_PATH, use the one from config.ini
            # SSH_PATH is the location on storage where file are located and they are different from server to server
            # print "the path ", self.ssh_path
            self.ssh_path = os.environ.get('SSH_PATH', parser.config_params('users_paths')['ssh_path'])



            self.success = parser.config_params('results')['success']
            self.failure = parser.config_params('results')['failure']
            self.host_domain = parser.config_params('host')['host_domain']

            # if there is no env var for SSH_SERVER, use the onfe from config.ini
            # SSH_SERVER is the machine were we connect to execute tests
            self.remotehost = os.environ.get('SSH_SERVER', parser.config_params('sshserver')['hostname'])
            self.random_dir = random_generator_function.generator_instance.random_volume()
            self.blob_dir = parser.config_params('blob')['location']

            print
            logger_settings.logger.info(
                '[TEST] = {0}/{1} : {2}'.format(self.GROUP_name, self.endpoint_name, self.method_name))
            print

        except UATError as e:
            logger_settings.logger.info('Test failed (Likely the credentials are wrong): {0}'.format(e.emsg()))
        except BaseException as e:
            logger_settings.logger.info('There is some general problem parsening data from config.ini {0} '.format(e))


    def _close(self):
        report.report_testcase(self.suite_name, zip(self.test_name, self.result))
        report.report_testcasehtml(self.suite_name, zip(self.test_name, self.result))
        print
        logger_settings.logger.info('[CLOSING TEST] = {0}/{1}'.format(self.GROUP_name, self.endpoint_name))
        print
