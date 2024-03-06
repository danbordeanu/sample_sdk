from .. InitDataTest import InitDataTest
from helpers.colors import bcolors
from helpers import logger_settings
import sys
from helpers.hpcapi_verbs.fileEndpoint import remove_local_file
from helpers.hpcapi_verbs.fileEndpoint import create_dir
from helpers.hpcapi_verbs.fileEndpoint import create_random_file_locally
from helpers.hpcapi_verbs.fileEndpoint import upload
from helpers.hpcapi_verbs.fileEndpoint import delete_file
from helpers.Error import UATError


class FileDeleteTest(InitDataTest):

    def __init__(self, parser):
        super(FileDeleteTest, self).__init__(parser, 'FILE', 'file', 'delete')
        try:
            folderpath_hpc = self.accesible_folder + self.user_a + '/' + self.random_dir
            self._api_delete(folderpath_hpc)
        except UATError as e:
            logger_settings.logger.info('Test failed: {0}'.format(e.emsg()))
        except BaseException:
            logger_settings.logger.debug('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    # User_a creates and uploads a file
    # Delete the file
    def _api_delete(self, folderpath_hpc):

        # Create custom folder with apihpc
        self.test_name.append('Create dir on remote server with custom name')
        ret_api = create_dir(self.url, folderpath_hpc, self.ticket)
        ret_api = str(ret_api['data'])
        logger_settings.logger.info('Dir with custom name {0} created on server'.format(ret_api))

        # Create upload + local file with apihpc
        filepath,  local_filename = create_random_file_locally(str(self.random_dir+".txt"), 1024)
        hpc_folder_route = self.ssh_path + folderpath_hpc
        ret_api = upload(self.url, self.ticket,  filepath, local_filename, 'true', hpc_folder_route)
        logger_settings.logger.info('File {0} uploaded to the server'.format( str(ret_api['data']['files'][0]) ))
        remove_local_file(local_filename)
        # delete the file in hpc
        ret_api = delete_file(self.url, self.ticket,  hpc_folder_route + '/' + local_filename)
        ret_api = str(ret_api['success'])
        print
        if ret_api is 'True':
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            self.result.append(self.success)
        else:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            raise UATError
        print
