import helpers.textconsole as report
from helpers import logger_settings
import sys
import os
from helpers.colors import bcolors

from helpers.hpcapi_verbs.admin import logout

# error
from helpers.Error import UATError
from helpers.Error import ExceptionType


class LogoutTest(object):

    def __init__(self, parser, ticket):
        try:
            self.suite_name = 'Logout'
            self.result = []
            self.test_name = []
            self.GROUP_name = 'AUTHENTIFICATION'
            self.endpoint_name = 'Logout'
            self.method_name = 'post'

            self.parser = parser
            self.success = parser.config_params('results')['success']
            self.failure = parser.config_params('results')['failure']
            self.host_domain = parser.config_params('host')['host_domain']
            # if there is no env var for HPC_APIURL, use the one from config.ini
            self.url = os.environ.get('HPC_APIURL', parser.config_params('hpcapi')['url'])

            print
            logger_settings.logger.info('[TEST] = {0}/{1} : {2}'.format(self.GROUP_name, self.endpoint_name, self.method_name))
            print

            self.hpc_logout(ticket)

        except UATError as e:
            logger_settings.logger.info('Test failed: {0}'.format(e.emsg()))
        except BaseException:
            logger_settings.logger.debug('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    def hpc_logout(self, ticket):
        self.test_name.append('LOGOUT')
        ret_api = logout(self.url, ticket)
        # print 'ret ', str(ret_api['success'])
        if str(ret_api['success']) is 'True':
            self.result.append(self.success)
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
        else:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
        print

    def _close(self):
        report.report_testcase(self.suite_name, zip(self.test_name, self.result))
        report.report_testcasehtml(self.suite_name, zip(self.test_name, self.result))
        print
        logger_settings.logger.info('[CLOSING TEST] = {0}/{1}'.format(self.GROUP_name, self.endpoint_name))
        print
