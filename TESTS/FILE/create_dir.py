from helpers import logger_settings
import sys
from helpers.hpcapi_verbs.fileEndpoint import create_dir
from helpers.unit_paramiko.nodeip import nodeipexecute
from .. InitDataTest import InitDataTest
import time
from helpers.Error import ExceptionType
from helpers.Error import UATError
from helpers.colors import bcolors


class FileCreateTest(InitDataTest):
    def __init__(self,parser):
        super(FileCreateTest, self).__init__(parser, 'FILE', 'create', 'post')

        try:
            filepath = self.accesible_folder + self.user_a
            self._api_create_random_dir(filepath)
            self._api_create_custom_dir(filepath)
        except UATError as e:
            logger_settings.logger.info('Test failed: {0}'.format(e.emsg()))
        except BaseException:
            logger_settings.logger.info('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    def _api_create_random_dir(self, filepath):
        self.test_name.append('Create dir on remote server with random name')
        ret_api = create_dir(self.url, filepath + '/' + self.random_dir, self.ticket)
        ret_api = str(ret_api['data'])
        logger_settings.logger.info('Dir with random name {0} created on server'.format(ret_api))
        self._unit(ret_api)

    def _api_create_custom_dir(self, filepath):
        self.test_name.append('Create dir on remote server with custom name')
        # TODO: use self.randomfolder
        folderpath = filepath + '/' + 'HPCAPITEST-' + time.strftime('%Y%m%d-%H%M%S')
        ret_api = create_dir(self.url, folderpath, self.ticket)
        ret_api = str(ret_api['data'])
        logger_settings.logger.info('Dir with custom name {0} created on server'.format(ret_api))
        self._unit(ret_api)

    def _unit(self, ret_api):
        # "cd" to the created folder
        ret = ''
        try:
            ret = nodeipexecute(self.remotehost, 'cd {0}'.format(ret_api))
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            self.result.append(self.success)
        except UATError as e:
            self.result.append(self.failure)
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            raise (UATError(ExceptionType.RETURN_VALUES, 'at FileCreateTest {0}'.format(e.emsg())))
