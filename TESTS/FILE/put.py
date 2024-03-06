from ..InitDataTest import InitDataTest
from helpers.colors import bcolors
from helpers import logger_settings
import sys
from helpers.hpcapi_verbs.fileEndpoint import remove_local_file
from helpers.hpcapi_verbs.fileEndpoint import create_dir
from helpers.hpcapi_verbs.fileEndpoint import create_random_file_locally
from helpers.hpcapi_verbs.fileEndpoint import upload
from helpers.hpcapi_verbs.fileEndpoint import get_file
from helpers.hpcapi_verbs.fileEndpoint import put_file
from helpers.Error import UATError
from helpers.unit_paramiko.nodeip import nodeipexecute
import subprocess


class FilePutTest(InitDataTest):
    def __init__(self, parser):
        super(FilePutTest, self).__init__(parser, 'FILE', 'file', 'delete')
        try:
            folderpath_hpc = self.accesible_folder + self.user_a + '/' + self.random_dir
            self.test_string = 'testing put_file'
            self._api_put(folderpath_hpc)
        except UATError as e:
            logger_settings.logger.info('Test failed: {0}'.format(e.emsg()))
        except BaseException:
            logger_settings.logger.debug('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    def _api_put(self, folderpath_hpc):
        # Create custom folder with hpcapi
        ret_api = create_dir(self.url, folderpath_hpc, self.ticket)
        ret_api = str(ret_api['data'])
        logger_settings.logger.info('Dir with custom name {0} created on server'.format(ret_api))

        # Create + upload local file with hpcapi to custom folder
        filepath, local_filename = create_random_file_locally(str(self.random_dir + '.txt'), 1024)
        hpc_folder_route = self.get_path + folderpath_hpc
        ret_api = upload(self.url, self.ticket, filepath, local_filename, 'true', hpc_folder_route)
        logger_settings.logger.info('File {0} uploaded to the server'.format(str(ret_api['data']['files'][0])))
        remove_local_file(local_filename)

        # Modify the content of the file  with put_api call
        self.test_name.append('Modify the content of the file using put_api call')
        ret_api = put_file(self.url, self.ticket, hpc_folder_route + '/' + local_filename, self.test_string)
        ret_api = str(ret_api['success'])
        if ret_api is not 'True':
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            raise UATError
        else:
            logger_settings.logger.info(bcolors.OKGREEN + 'SUCCESS' + bcolors.ENDC)
            self.result.append(self.success)
            logger_settings.logger.info(
                'File {0} was updated with content: "{1}" '.format(hpc_folder_route + local_filename, self.test_string))

        # Download the file and check its content
        self.test_name.append('Download the file and check the content of file')
        get_file(self.url, self.ticket, hpc_folder_route + '/' + local_filename)


        bashcommand = 'cat /tmp/' + local_filename
        try:
            process = subprocess.Popen(bashcommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
        except OSError as e:
            logger_settings.logger('Some issue executing cat command {}'.format(e))
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            raise UATError

        if output not in self.test_string:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
        else:
            logger_settings.logger.info(bcolors.OKGREEN + 'SUCCESS' + bcolors.ENDC)
            self.result.append(self.success)

        print

        # Get lastModif date from API and compare with stat HPCAPI-290
        self.test_name.append('Get lastModifDate from hpc-api and compare with stat value')
        ret_api = get_file(self.url, self.ticket, hpc_folder_route, 'RECUR')
        lastmodifdate = str(ret_api['data'][0]['lastModifDate'])
        ret = nodeipexecute(self.remotehost, 'stat -c %Y {0}'.format(hpc_folder_route + '/' + local_filename))
        if ret not in lastmodifdate:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
        else:
            logger_settings.logger.info(bcolors.OKGREEN + 'SUCCESS' + bcolors.ENDC)
            self.result.append(self.success)

