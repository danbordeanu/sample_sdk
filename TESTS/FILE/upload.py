
from helpers.hpcapi_verbs.fileEndpoint import upload
from helpers.hpcapi_verbs.fileEndpoint import create_random_file_locally
from helpers.hpcapi_verbs.fileEndpoint import remove_local_file
from helpers.unit_paramiko.nodeip import nodeipexecute
from helpers import logger_settings
import sys
from ..InitDataTest import InitDataTest
from helpers.Error import ExceptionType
from helpers.Error import UATError

from helpers.colors import bcolors


class FileUploadTest(InitDataTest):
    def __init__(self, parser):
        super(FileUploadTest, self).__init__(parser, 'FILE', 'upload', 'post')

        filepath_ssh = self.ssh_path + self.accesible_folder + '/' + self.user_a + '/' + self.random_dir

        try:
            self._api_upload_file_to_random_folder()
            self._api_upload_file_to_custom_folder(filepath_ssh)
            self._api_upload_4k_issue_182()
        except UATError as e:
            logger_settings.logger.info('Test failed: {0}'.format(e.emsg()))
        except BaseException:
            logger_settings.logger.debug('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    def _api_upload_file_to_random_folder(self):
        self.test_name.append('Upload local file to random folder in server')
        filepath,  filename= create_random_file_locally(self.random_dir+'.txt', 1024)
        ret_api = upload(self.url, self.ticket,  filepath, filename, 'true')
        ret_api = str(ret_api['data']['files'][0])
        self._unit(ret_api, filename)

    def _api_upload_file_to_custom_folder(self, filepath_ssh):
        self.test_name.append('Upload local file to custom folder in server')
        # create folder on server
        nodeipexecute(self.remotehost, 'mkdir {0}'.format(filepath_ssh))
        #lets set the permission for this dir
        #on prod server this line must be disabled, for internal stuff is ok to have it
        #nodeipexecute(self.remotehost, 'nfs4_setfacl -s A:d:{0}:rwaDdxtTnNcoy,A:fi:{1}:rwaDdtTnNcoy,A:d:OWNER@:rwaDdxtTnNcCoy,A:fi:OWNER@:rwaDdtTnNcCoy {2}'.format(self.user_a, self.user_a, filepath_ssh))
        # create + upload a  local file
        filepath,  filename= create_random_file_locally(self.random_dir+'.txt', 1024)
        ret_api = upload(self.url, self.ticket,  filepath, filename, 'true', filepath_ssh)
        ret_api = str(ret_api['data']['files'][0])
        self._unit(ret_api, filename)

    def _api_upload_4k_issue_182(self):
        '''
        This test will do regression for JIRA item 182, uploading 4k zip file
        :return:
        '''
        self.test_name.append('Upload 4k zip file')
        #TODO, use jira-python to download the file from jira ticket, MAGIC
        self.file_to_be_uploaded = 'issue-182.zip'
        #let's upload the big zip file
        do_upload = upload(self.url, self.ticket, self.blob_dir, self.file_to_be_uploaded, 'true')
        #API should return True
        if do_upload['success']:
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            self.result.append(self.success)
        else:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            assert do_upload['success'] is True, 'Server returned something else than TRUE when uploading the 4k zip file'
            raise (UATError(ExceptionType.RETURN_VALUES, 'issue uploading 4k zip bomb'))

    def _unit(self, ret_api, local_file):
        ret = nodeipexecute(self.remotehost, 'ls {0}'.format(ret_api))
        if not ret:
            remove_local_file(local_file)
            self.result.append(self.failure)
            raise(UATError(ExceptionType.RETURN_VALUES, 'at _api_upload_file_random_folder: mistmatch'))
        else:
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            remove_local_file(local_file)
            self.result.append(self.success)
