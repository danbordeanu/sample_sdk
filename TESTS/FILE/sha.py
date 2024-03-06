from helpers import logger_settings
import sys
from helpers.unit_paramiko import nodeip
from .. InitDataTest import InitDataTest
from helpers.hpcapi_verbs.fileEndpoint import get_sha
from helpers.Error import UATError
from helpers.colors import bcolors


class FileShaTest(InitDataTest):
    def __init__(self, parser):
        super(FileShaTest, self).__init__(parser, 'FILE', 'sha', 'post')
        try:

            filepath_ssh = self.ssh_path + self.accesible_folder + self.user + '/' + self.random_dir+'.txt'
            nodeip.nodeipexecute(self.remotehost, 'touch {0}'.format(filepath_ssh))
            ret = nodeip.nodeipexecute(self.remotehost, 'ls {0}'.format(filepath_ssh))
            if ret != filepath_ssh:
                raise UATError
            # thank you Jan!!!!!!! refactoring is written everywhere on your code. We need to to remove from full file
            #  path the SSH_PATH, ex: /SFS/scratch/dev/QSPWBUSERS/user -> /QSPWBUSERS/user
            self.replaced_string = filepath_ssh.replace(self.ssh_path, '/')
            self._ssh_chk_sha_generic(filepath_ssh, 'sha1sum')
            self._ssh_chk_sha_generic(filepath_ssh, 'sha256sum', 'SHA256')
            self._ssh_chk_sha_generic(filepath_ssh, 'sha512sum', 'SHA512')
        except UATError as e:
            logger_settings.logger.info('Test failed: {0}'.format(e.emsg()))
        except BaseException:
            logger_settings.logger.debug('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    def _ssh_chk_sha_generic(self, filepath_ssh, sha_command, sha_type=None):
        if sha_type is None:
            test_name_string = 'Checking SHA1 signature for random file'
            ret_api = get_sha(self.url, self.ticket, self.replaced_string)
        else:
            test_name_string = 'Checking {0} signature for random file'.format(sha_type)
            ret_api = get_sha(self.url, self.ticket, self.replaced_string, sha_type)

        self.test_name.append(test_name_string)
        # TODO: fix this triple array in the api
        ret_api = str(ret_api['data'][0]['hashCode'])
        self._unit(ret_api, filepath_ssh, sha_command)

    def _unit(self, ret_api, filepath_ssh, sha_type):
        ret = nodeip.nodeipexecute(self.remotehost, '{0} {1}'.format(sha_type, filepath_ssh))
        assert isinstance(ret_api, object)

        if ret_api not in ret:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            raise UATError
        else:
            self.result.append(self.success)
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
