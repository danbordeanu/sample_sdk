import base64
import helpers.textconsole as report
import os
import sys
import ast

from helpers import logger_settings

# Secret Labs' Regular Expression Engine
import re

from helpers.colors import bcolors
from helpers.hpcapi_verbs.admin import login

# error
from helpers.Error import UATError
from helpers.Error import ExceptionType


class LoginTest(object):
    def __init__(self, parser, user=None):
        # parse data
        try:
            self.myboolean = True
            self.suite_name = 'Login'
            self.result = []
            self.test_name = []
            self.GROUP_name = 'AUTHENTICATION'
            self.endpoint_name = 'Login'
            self.method_name = 'post'
            self.parser = parser
            # if there is no env var for HPC_APIURL, use the one from config.ini
            self.url = os.environ.get('HPC_APIURL', parser.config_params('hpcapi')['url'])

            if os.environ.get('HPC_UAT_USERS') is not None:
                # check if there are the env vars for user/password
                # export HPC_UAT_USERS="{'user_a':'user_1', 'password_a':'password_1', 'user_b':'user_2',
                # 'password_b':'password_2', 'user_c':'user_3', 'password_c':'password_3'}"
                my_user_env_dict = ast.literal_eval(os.environ.get('HPC_UAT_USERS'))
                self.user_a = my_user_env_dict['user_a']
                self.password_a = base64.b64decode(my_user_env_dict['password_a'])

                self.user_b = my_user_env_dict['user_b']
                self.password_b = base64.b64decode(my_user_env_dict['password_b'])

                self.user_c = my_user_env_dict['user_c']
                self.password_c = base64.b64decode(my_user_env_dict['password_c'])

            else:
                # use the config ini stored variables
                self.user_a = parser.config_params('users')['user_a']
                self.password_a = base64.b64decode(parser.config_params('users')['password_a'])

                self.user_b = parser.config_params('users')['user_b']
                self.password_b = base64.b64decode(parser.config_params('users')['password_b'])

                self.user_c = parser.config_params('users')['user_c']
                self.password_c = base64.b64decode(parser.config_params('users')['password_c'])

            self.success = parser.config_params('results')['success']
            self.failure = parser.config_params('results')['failure']
            self.host_domain = parser.config_params('host')['host_domain']

            print
            logger_settings.logger.info('[TEST] = {0}/{1} : {2}'.format(self.GROUP_name, self.endpoint_name, self.method_name))
            print

            if user is None:
                self.hpc_login(self.user_a, self.password_a)
                self.hpc_login(self.user_b, self.password_b)
                self.hpc_login(self.user_c, self.password_c)
            else:
                self.myboolean = False
                if user is 'user_a':
                    self.hpc_login(self.user_a, self.password_a)
                elif user is 'user_b':
                    self.hpc_login(self.user_b, self.password_b)
                elif user is 'user_c':
                    self.hpc_login(self.user_c, self.password_c)
                else:
                    raise (UATError(ExceptionType.AUTHENTICATION, 'What user?'))

        except UATError as e:
            logger_settings.logger.info('Test failed: {0}'.format(e.emsg('asString')))
        except Exception:
            logger_settings.logger.debug('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    def getTicket(self):
        return self.ticket

    def getTicketUser(self):
        return self.ticket, self.user

    def getUsers(self):
        return self.user_a, self.user_b, self.user_c

    def _check_host_in_ticket(self, user):
        if re.search(self.host_domain, self.ticket):
            logger_settings.logger.info('Ticket seems just fine for user {0}'.format(user))
            self.test_name.append('LOGIN-{0}'.format(user))
            self.result.append(self.success)
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
        else:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            raise (UATError(ExceptionType.RETURN_VALUES, 'error at check host token in response: mismatch'))
        print

    def hpc_login(self, user, password):
        try:
            hpc_login = login(self.url + '/' + 'login', user, password)
            assert isinstance(user, object)
            self.user = user
            self.ticket = str(hpc_login['data'])
            logger_settings.logger.info('ticket = [{0}]  user = [{1}]'.format(self.ticket, user))
            self._check_host_in_ticket(user)
        except UATError as e:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            raise (UATError(ExceptionType.AUTHENTICATION, 'User/Passwd incorrect?  {0}'.format(e.emsg('asString'))))
        except:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED unknown' + bcolors.ENDC)
            self.result.append(self.failure)
            raise (UATError(ExceptionType.AUTHENTICATION, 'undefined error at login' ))

    def generate_reports(self, append_multiple=None):
        '''
        This function is used by merge_test.sh
        When we run all tests, we don't want to have all logins in final report
        :param append_multiple:
        :return:
        '''
        if append_multiple is not None:
            self.suite_name = append_multiple
        report.report_testcase(self.suite_name, zip(self.test_name, self.result))
        report.report_testcasehtml(self.suite_name, zip(self.test_name, self.result))

    def _close(self):
        if self.myboolean:
            self.generate_reports()
        else:
            self.generate_reports('multiple-login')
        print
        logger_settings.logger.info('[CLOSING TEST] = {0}/{1}'.format(self.GROUP_name, self.endpoint_name))
        print
