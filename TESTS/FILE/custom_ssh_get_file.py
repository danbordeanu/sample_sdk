from ..InitDataTest import InitDataTest
from helpers import logger_settings
import sys
import string
import random

# admin
from ..AUTHENTICATION.login_test import LoginTest

# file
from helpers.hpcapi_verbs.fileEndpoint import create_random_file_locally
from helpers.hpcapi_verbs.fileEndpoint import upload
from helpers.hpcapi_verbs.fileEndpoint import get_file


#ssh
from helpers.unit_paramiko.nodeip import nodeipexecute

# Errors
from helpers.Error import UATError

from helpers.colors import bcolors


class CustomGetSshFIle(InitDataTest):
    def __init__(self, parser):
        super(CustomGetSshFIle, self).__init__(parser, 'FILE', 'upload', 'ssh')
        try:
            self._ssh_create_file_same_user_has_access()
            self._ssh_create_file_other_user_no_access()

        except UATError as e:
            logger_settings.logger.info('Test failed: {0}'.format(e.emsg()))
        except BaseException:
            logger_settings.logger.debug('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    # A different isid has no access to the folder/file created with ssh through the api
    # User has access to his own files created with ssh/mkdir through the API
    # There are two tests because is much more convenient to investigate ownership

    def _ssh_create_file_same_user_has_access(self):
        try:
            # User has access to his own files created with ssh/mkdir through the API
            self.test_name.append('User_A creates directory/file using ssh/mkdir - '
                                  'User_A can access the file using API')
            folderpath_hpc_access = self.accesible_folder + self.user_a + '/' + \
                                    ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            hpc_folder_route_access = self.ssh_path + folderpath_hpc_access
            # Isid creates a folder ssh/mkdir
            nodeipexecute(self.remotehost, 'mkdir -p {0}'.format(hpc_folder_route_access))
            # Isid uploads a file to same folder using api
            filepath, filename = create_random_file_locally(self.random_dir + '.txt', 1024)
            self.login = LoginTest(self.parser, 'user_a')
            self.ticket, self.user = self.login.getTicketUser()
            upload(self.url, self.ticket, filepath, filename, 'true', hpc_folder_route_access)
            # read file using API calls
            ret_api = get_file(self.url, self.ticket, hpc_folder_route_access, 'RECUR')
            ret_api = str(ret_api['success'])
            if ret_api is 'True':
                logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
                self.result.append(self.success)
            else:
                logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
                self.result.append(self.failure)
                raise UATError

        except Exception:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)

    def _ssh_create_file_other_user_no_access(self):
        # A different isid has no access to the folder/file created with ssh through the api
        self.test_name.append('User_A creates directory/file using ssh/mkdir - '
                              'User_B no access to read file using API')
        folderpath_hpc_no_access = self.accesible_folder + self.user_a + '/' + \
                                   ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

        hpc_folder_route_no_access = self.ssh_path + folderpath_hpc_no_access
        # Isid creates a folder ssh/mkdir
        nodeipexecute(self.remotehost, 'mkdir -p {0}'.format(hpc_folder_route_no_access))
        # Isid uploads a file to same folder using api
        filepath, filename = create_random_file_locally(self.random_dir + '.txt', 1024)
        self.login = LoginTest(self.parser, 'user_a')
        self.ticket, self.user = self.login.getTicketUser()
        upload(self.url, self.ticket, filepath, filename, 'true', hpc_folder_route_no_access)
        # A different isid has no acces to the folder through the api
        self.login = LoginTest(self.parser, 'user_b')
        self.ticket, self.user = self.login.getTicketUser()
        # read the file using API call
        try:
            get_file(self.url, self.ticket, hpc_folder_route_no_access, 'RECUR')
            self.result.append(self.failure)
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            logger_settings.logger.info(
                'FAILED User: {0} has access to file {1}, this is bad'.format(self.user, self.random_dir + '.txt'))
        except Exception:
            self.result.append(self.success)
            logger_settings.logger.info(
                'SUCCESS User: {0} has no access to file {1}, this is great'.format(self.user,
                                                                                    self.random_dir + '.txt'))
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)

