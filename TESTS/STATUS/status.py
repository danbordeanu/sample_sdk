from ..InitDataTest import InitDataTest
from helpers import logger_settings
import sys
from helpers.hpcapi_verbs.statusEndpoint import get_status
from helpers.Error import UATError
from helpers.colors import bcolors

class GetStatusTest(InitDataTest):
    def __init__(self, parser):
        super(GetStatusTest, self).__init__(parser, 'STATUS', 'status', 'get')
        try:
            self._api_get_status()
        except UATError as e:
            logger_settings.logger.info('Test failed: {0}'.format(e.emsg()))
        except BaseException:
            logger_settings.logger.debug('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    def _api_get_status(self):
        # GET API STATUS
        self.test_name.append('Get status of hpc-api database')
        # TODO: an assert here brokes the error handling workflow
        # implement try-catch as usual 
        assert isinstance(self.url, object)
        ret_api = get_status(self.url)
        if ret_api['data']['dbUp']:
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            self.result.append(self.success)
        else:
            logger_settings.logger.info(bcolors.WARNING + 'FAILED' + bcolors.ENDC)
            self.result.append(self.success)

        self.test_name.append('Get status of hpc-api scheduler')
        if ret_api['data']['scheUp']:
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            self.result.append(self.success)
        else:
            logger_settings.logger.info(bcolors.WARNING + 'FAILED' + bcolors.ENDC)
            self.result.append(self.success)


