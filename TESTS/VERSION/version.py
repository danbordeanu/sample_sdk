from ..InitDataTest import InitDataTest
from helpers import logger_settings
import sys
from helpers.hpcapi_verbs.versionEndpoint import get_version
from helpers.Error import UATError
from helpers.colors import bcolors


class GetVersionTest(InitDataTest):
    def __init__(self, parser):
        super(GetVersionTest, self).__init__(parser, 'VERSION', 'version', 'get')
        try:
            self._api_get_version()
        except UATError as e:
            logger_settings.logger.info('Test failed: {0}'.format(e.emsg()))
        except BaseException:
            logger_settings.logger.debug('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    @property
    def get_build_file(self):
        #grep version from build.gradle
        try:
            f = open('../build.gradle')
            for version in f:
                if 'apiVersion =' in version:
                    return version.replace('"', '').strip('\n')
        except IOError as e:
            print 'error on file operation {0}'.format(e)

    # GET API VERSION: Get version from HPC-API and compare with build.gradle version value
    def _api_get_version(self):
        self.test_name.append('Get version from HPC-API and compare with build.gradle version value')
        assert isinstance(self.url, object)
        ret_api = get_version(self.url)
        if self.get_build_file.split('= ')[1] in str(ret_api['data']['version']).split('|')[0]:
            logger_settings.logger.info(bcolors.OKGREEN + 'SUCCESS' + bcolors.ENDC)
            self.result.append(self.success)
        else:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
