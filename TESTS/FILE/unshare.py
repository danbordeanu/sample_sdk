from ..InitDataTest import InitDataTest
from helpers import logger_settings
import sys

# admin
from ..AUTHENTICATION.login_test import LoginTest

# file
from helpers.hpcapi_verbs.fileEndpoint import remove_local_file
from helpers.hpcapi_verbs.fileEndpoint import create_dir
from helpers.hpcapi_verbs.fileEndpoint import create_random_file_locally
from helpers.hpcapi_verbs.fileEndpoint import upload
from helpers.hpcapi_verbs.fileEndpoint import get_file
from helpers.hpcapi_verbs.fileEndpoint import get_share
from helpers.hpcapi_verbs.fileEndpoint import get_unshare

# Errors
from helpers.Error import ExceptionType
from helpers.Error import UATError

from helpers.colors import bcolors


class FileUnshareTest(InitDataTest):
    def __init__(self, parser):
        super(FileUnshareTest, self).__init__(parser, 'FILE', 'unshare', 'get')
        try:
            folderpath_hpc = self.accesible_folder + self.user_a + '/' + self.random_dir
            self._api_unshare(folderpath_hpc)
        except UATError as e:
            e.emsg()
        except BaseException:
            logger_settings.logger.debug('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    # User_a creates and uploads a file
    # User_b has not access
    # Share with user_b -> now has access
    # Unshare with user_b
    def _api_unshare(self, folderpath):

        # Create custom folder with hcp-api
        self.test_name.append('User_a creates a random folder with api')
        ret_api_create_dir = create_dir(self.url, folderpath, self.ticket)
        ret_api_create_dir = str(ret_api_create_dir['data'])
        logger_settings.logger.info('Dir with custom name {0} created on server'.format(ret_api_create_dir))
        print

        # Create upload + local file with hpc-api
        self.test_name.append('User_a uploads a local file with api to the folder')
        filepath, local_filename = create_random_file_locally(str(self.random_dir + '.txt'), 1024)
        hpc_folder_route = self.ssh_path + self.accesible_folder + self.user_a + '/' + self.random_dir
        upload(self.url, self.ticket, filepath, local_filename, 'true', hpc_folder_route)
        remove_local_file(local_filename)
        print

        # user_b does not have access to file
        self.test_name.append('User_b has no access to file of user_a in server')
        self.login = LoginTest(self.parser, 'user_b')
        self.ticket, self.user = self.login.getTicketUser()

        self._do_actual_get_file(self.ticket, hpc_folder_route)
        print

        # user_b has access to file after sharing with him
        self.test_name.append('User_b has access to file after in server after being shared')
        self.login = LoginTest(self.parser, 'user_a')
        self.ticket, self.user = self.login.getTicketUser()
        get_share(self.url, self.ticket, hpc_folder_route, self.user_b)
        self.login = LoginTest(self.parser, 'user_b')
        self.ticket, self.user = self.login.getTicketUser()
        ret_api = get_file(self.url, self.ticket, hpc_folder_route, 'RECUR')

        # is file name in ret_api?
        self._chk_access_file_in_response(ret_api)
        print

        # user_b has no access to file after unsharing with him
        self.test_name.append('User_b has no access to file after it was unshared with him by user_a')
        self.login = LoginTest(self.parser, 'user_a')
        self.ticket, self.user = self.login.getTicketUser()
        get_unshare(self.url, self.ticket, hpc_folder_route, self.user_b)
        self.login = LoginTest(self.parser, 'user_b')
        self.ticket, self.user = self.login.getTicketUser()

        self._do_actual_get_file(self.ticket, hpc_folder_route)
        print

    def _do_actual_get_file(self, ticket, hpc_folder_route):
        try:
            # try to get_file, if it's possible the test failed
            get_file(self.url, ticket, hpc_folder_route, 'RECUR')
            self.result.append(self.failure)
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            logger_settings.logger.info(
                'FAILED User: {0} has access to file {1}, this is bad'.format(self.user, self.random_dir + '.txt'))
        except UATError as e:
            # test is successful if api not able to download the content of dir
            if 'Forbidden' in e.emsg('asString'):
                logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
                self.result.append(self.success)
                logger_settings.logger.info(
                    'OK User: {0} has no access to file {1}'.format(self.user, self.random_dir + '.txt'))
            else:
                logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
                self.result.append(self.failure)
                raise UATError
        print

    def _chk_access_file_in_response(self, ret_api):
        ret_api = str(ret_api['data'][0]['name'])
        expected_ret = '{0}.txt'.format(self.random_dir)
        if ret_api not in expected_ret:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            raise (UATError(ExceptionType.HPCAPI,
                            ' Some problem accessing the file {0} at unshare test'.format(self.random_dir + '.txt')))
        else:
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            self.result.append(self.success)
            logger_settings.logger.info(
                'OK: User does have access to file {1}'.format(self.user, self.random_dir + '.txt'))
