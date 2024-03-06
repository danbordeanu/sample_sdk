from ..InitDataTest import InitDataTest
from helpers import logger_settings
import sys
import helpers.hpcapi_verbs.JobEndpoint
from helpers.Error import UATError
from helpers.Error import ExceptionType
from helpers.colors import bcolors
from helpers.hpcapi_verbs.fileEndpoint import create_dir
from helpers.hpcapi_verbs.fileEndpoint import upload
import random
from helpers.unit_paramiko.nodeip import nodeipexecute
import time


class CommandJobTest(InitDataTest):
    def __init__(self, parser, plugin_name):
        super(CommandJobTest, self).__init__(parser, 'Command', plugin_name, 'post')
        try:
            filepath = self.accesible_folder + self.user_a
            self._api_create_random_dir(filepath)
            # get the command plugin available
            ret_api_command = helpers.hpcapi_verbs.JobEndpoint.get_command(self.url, self.ticket)
            if plugin_name in 'R':
                # TODO: skip the QSP Standard R Library  and let Ed know
                # TODO: regex instead of plain R
                versions = [x for x in ret_api_command['data'] if 'R' in x]
                for index in range(len(versions)):
                    self.plugin_version = versions[index]
                    self._api_R_scenario_first()
                    self._api_R_scenario_second()
                    self._api_R_scenario_third()
                    self._api_R_scenario_forth()
                    self._api_R_scenario_fifth()
            elif plugin_name in 'nonmem':
                versions = [x for x in ret_api_command['data'] if 'NONMEM' in x]
                self._api_nonmem_upload_scripts()
                for index in range(len(versions)):
                    self.plugin_version = versions[index]
                    self._api_nonmem_scenario()
                    # TODO check if this test has to be executed for all nonmem versions, atm only once
                    self._api_nonmem_param_scenario()
            elif plugin_name == 'array':
                self.plugin_version = plugin_name
                self._api_nonmem_upload_scripts()
                self._api_array_scenario_first()
            else:
                logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
                self.result.append(self.failure)
                raise (UATError(ExceptionType.ARGUMENTS,
                                'Invalid argument for workflows: Maybe the plugin name is incorrect?'))

        except UATError as e:
            logger_settings.logger.info('Test failed: {0}'.format(e.emsg()))
        except Exception:
            logger_settings.logger.info('Something was very wrong with test:{0}'.format(str(sys.exc_info()[1])))
        finally:
            self._close()

    # R ========================================================================

    # Scenario 1: submit to command plugin a R script that will be uploaded into an existing directory
    # 1. encapsulate in a bash scritpt with the HPC environment the provided command
    # 2. upload the script into a specific folder
    # 3. submit the script for execution in the current folder
    def _api_R_scenario_first(self):
        try:
            self.test_name.append('{0}: simple script submitted to specific folder'.format(self.plugin_version))
            ret_api = helpers.hpcapi_verbs.JobEndpoint.post_command_plugin_name(
                self.url,
                self.ticket,
                '-e ' '\'print("myHelloString")\'',
                self.plugin_version,
                'appjobgrid{0}'.format(''.join(random.choice('abcde') for _ in range(3))),
                self.ret_api_random_dir, None, '-P normal -l mem_reserve=128M')
            logger_settings.logger.info('Job with ID: {0} for pluging type {1} '
                                        'submited on server'.format(ret_api['data']['jobId'], self.plugin_version))
            self._unit_job_status(ret_api)
        except Exception:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)

    # Scenario 2: submit to command plugin a R script without existing directory
    # The api will return in response the .sh script that will be submitted to POST:/job
    def _api_R_scenario_second(self):
        try:
            self.test_name.append('{0}: Get script with environment, '
                                  'and submit it as a regular job in random folder'.format(self.plugin_version))
            # create the script using command plugin: generates a script with the cluster environment
            ret_api_submit_job_no_dir = helpers.hpcapi_verbs.JobEndpoint.post_command_plugin_name(
                self.url, self.ticket, '-e '
                                       '\'print("myHelloString")\'',
                self.plugin_version,
                'appjobgridrandom{0}'.format(''.join(random.choice('abcde'))))
            command = '\n'.join(ret_api_submit_job_no_dir['data'])

            # submit the script for execution
            data_post_job = helpers.hpcapi_verbs.JobEndpoint.post_job(self.url, self.ticket, 'test123', command)
            logger_settings.logger.info('Job without directory: {0} '
                                        'submited on grid'.format(str(ret_api_submit_job_no_dir['data'])))
            logger_settings.logger.info('Job has id:{0}'.format(data_post_job['data']['jobId']))

            self._unit_job_status(data_post_job)
        except Exception:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)

    # Scenario 3: Upload the R script using the POST:/file/create and submit using POST:job
    def _api_R_scenario_third(self):
        self.test_name.append('Upload R script file')
        self.file_to_be_uploaded = 'hello_world.sh'

        # Upload the R file
        do_upload = upload(self.url, self.ticket, self.blob_dir,
                           self.file_to_be_uploaded, 'false', self.ret_api_random_dir)
        logger_settings.logger.info('R script uploaded in:{0}'.format(str(do_upload['data']['files'])))
        # TODO: ssh validation (unit) not api
        if do_upload['success']:
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            self.r_location = str(do_upload['data']['files'][0])
            self.result.append(self.success)
        else:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            assert do_upload['success'] is True, 'Server returned something else than TRUE when uploading the R file'
            raise (UATError(ExceptionType.RETURN_VALUES, 'issue uploading R file'))

    # Scenario 4: submit using POST:/job by using an already uploaded R script file
    def _api_R_scenario_forth(self):
        self.test_name.append('{0}: Submit job with an already uploaded file'.format(self.plugin_version))
        content = None
        data_post_job = helpers.hpcapi_verbs.JobEndpoint.post_job(
            self.url,
            self.ticket,
            'test123',
            content,  # None option
            self.r_location)
        logger_settings.logger.info('Job using uploaded '
                                    'file: {0} submited on server'.format(str(data_post_job['data'])))

        self._unit_job_status(data_post_job)

    # Scenario 5: submit using POST:/job by using an already uploaded R script file and providing extra jobsubmission param
    def _api_R_scenario_fifth(self):
        self.test_name.append('{0}: Submit job with an already uploaded file and provide jobsubmission params'.format(
            self.plugin_version))
        content = None
        data_post_job = helpers.hpcapi_verbs.JobEndpoint.post_job(
            self.url,
            self.ticket,
            'test123customparams',
            content,  # None option
            self.r_location,
            jobsubmission='-P normal -l mem_reserve=128M'
        )
        logger_settings.logger.info('Job with custom jobsubmission params using uploaded '
                                    'file: {0} submited on server'.format(str(data_post_job['data'])))

        self._unit_job_status(data_post_job)

    # NONMEM ===================================================================

    # Upload the NONMEM scripts using the POST:/file/create
    def _api_nonmem_upload_scripts(self):
        self.file_to_be_uploaded = 'nonmem.zip'
        self.test_name.append('Upload script files: {0}'.format(self.file_to_be_uploaded))
        # Upload the NONMEM zip file
        do_upload = upload(self.url, self.ticket, self.blob_dir,
                           self.file_to_be_uploaded, 'false', self.ret_api_random_dir)
        logger_settings.logger.info('NONMEM script files uploaded in:{0}'.format(str(do_upload['data']['files'])))
        # API should return True
        if do_upload['success']:
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            self.result.append(self.success)
        else:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            assert do_upload['success'] is True, 'Server returned something else than TRUE when uploading the R file'
            raise (UATError(ExceptionType.RETURN_VALUES, 'issue uploading NONMEM file'))

    # Scenario five: submit a job to POST:/job by using an already uploaded NONMEM script files
    def _api_nonmem_scenario(self):
        self.test_name.append('{0}: Submit job with already uploaded script files'.format(self.plugin_version))
        content = None
        data_post_job = helpers.hpcapi_verbs.JobEndpoint.post_job(
            self.url, self.ticket, 'test123nonmem{0}'.format(''.join(random.choice('abcde'))),
            content,
            self.ret_api_random_dir + '/' + 'nonmem' + '/' + 'nonmem_test.sh')
        logger_settings.logger.info('Job using uploaded NONMEM '
                                    'file: {0} submited on server'.format(str(data_post_job['data'])))
        self._unit_out(data_post_job)

    # Scenario six: submit a job using command plugin with custom parameters and check the output. See issue HPCAPI-397
    def _api_nonmem_param_scenario(self):
        self.test_name.append(
            '{0}: Generate a script calling command plugin with custom parameters'.format(self.plugin_version))

        # list of the custom commands input described in issue 397
        custom_command_input = ['run1.mod',
                                'run1.mod run2',
                                'run1.mod run2.lst [nodes=4]',
                                'run1.mod run2.lst [nodes=4] -pop=value1 value2 [parafile=/SFS/product/REGULATED/parafiles/nmpara4.pnm]',
                                'run1.mod run2 [nodes=4] [threads=4] [parafile=/SFS/product/REGULATED/parafiles/nmpara4.pnm]']

        # list of the expected output generated script
        custom_command_output = ['run1.mod run1.lst',
                                 'run1.mod run2.lst',
                                 'run1.mod run2.lst [nodes=4]',
                                 'run1.mod run2.lst [nodes=4] value2 [parafile=/SFS/product/REGULATED/parafiles/nmpara4.pnm]',
                                 'run1.mod run2.lst [nodes=4] [threads=4] [parafile=/SFS/product/REGULATED/parafiles/nmpara4.pnm]']

        # call command plugin endpoint with all the custom input commands and compare the response body with the custom input value
        for f, b in zip(custom_command_input, custom_command_output):
            ret_api_command_param = helpers.hpcapi_verbs.JobEndpoint.post_command_plugin_name(self.url, self.ticket, f,
                                                                                              self.plugin_version,
                                                                                              'plugincustomparam{0}'.format(
                                                                                                  ''.join(random.choice(
                                                                                                      'abcde') for _ in
                                                                                                          range(3))),
                                                                                              None, None,
                                                                                              None)  # appending random string with 3 chars to appjobgrid

            logger_settings.logger.info(
                'Plugin command for: {0} with custom cmdline: {1} returned: {2}'.format(self.plugin_version, f, str(
                    ret_api_command_param['data'])))

            self._unit_out_custom_command(b, ret_api_command_param)

    # JOB ARRAYS ===============================================================

    # Scenario 1: submit to POST:/job/array an uploaded nonmem script
    def _api_array_scenario_first(self):
        self.test_name.append('{0}: Submit job array with already uploaded NONMEM files'.format(self.plugin_version))
        ret_api = helpers.hpcapi_verbs.JobEndpoint.post_job_array(
            self.url, self.ticket,
            self.ret_api_random_dir + '/' + 'nonmem' + '/' + 'nonmem_test.sh',
            'testarray123nonmema{0}'.format(''.join(random.choice('abcde'))), '1', '3')

        logger_settings.logger.info('Job Array using uploaded '
                                    'NONMEM file: {0} submited on server'.format(str(ret_api['data'])))

        # TODO we need to investigate if unit_ssh_out_err makes sense, disabling atm. Alejandro, please investigate this
        # self._unit_ssh_out_err(self.ret_api_random_dir)
        self._unit_out(ret_api)

    # HELPERS ==================================================================

    def _api_create_random_dir(self, filepath):
        self.test_name.append('Create random directory on remote storage')
        ret_api_random_dir = create_dir(self.url, filepath + '/' + self.random_dir, self.ticket)
        self.ret_api_random_dir = str(ret_api_random_dir['data'])
        if ret_api_random_dir['success']:
            logger_settings.logger.info('Directory name {0} created on server'.format(self.ret_api_random_dir))
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            self.result.append(self.success)
        else:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            # TODO: asserts are for code development, in final version only exceptions
            assert ret_api_random_dir[
                       'success'] is True, 'Server returned something else than TRUE when creating ' 'random directory'
            raise (UATError(ExceptionType.RETURN_VALUES, 'issue creating random directory'))

    # TESTS ====================================================================

    # Check if the api return value for "job status" coincide with qacct (accesing the scheduler via SSH)
    def _unit_job_status(self, ret_api):
        job_id = str(ret_api['data']['jobId'])
        get_job_status = helpers.hpcapi_verbs.JobEndpoint.get_job_info(self.url, self.ticket, job_id)

        if get_job_status['data']['status'] == 'RUNNING' or get_job_status['data']['status'] == 'DONE' or \
                get_job_status['data']['status'] == 'QUEUED_ACTIVE':

            # If the API is returning QUEUED_ACTIVE, the job requires a few seconds to be
            # executed into the cluster and qacct to be able to get the job status.
            if get_job_status['data']['status'] == 'QUEUED_ACTIVE':
                # TODO: Alejandro investigate this
                logger_settings.logger.info('Job was queued: QUEUED_ACTIVE  << waiting 30 seconds')
                time.sleep(30)

            try:
                ret_job_status = nodeipexecute(self.remotehost, 'qacct -j {0}|egrep "failed"'.format(str(job_id)))
                if '0' in ret_job_status:
                    self.result.append(self.success)
                    logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
                else:
                    logger_settings.logger.info(
                        'Job with id:{0} is in status: {1} and qacct returned something different than 0: {2}'.format(
                            job_id,
                            get_job_status['data']['status'],
                            ret_job_status))
                    raise
            except Exception:
                logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
                self.result.append(self.failure)
                raise (UATError(ExceptionType.RETURN_VALUES, 'issue getting job status'))

        else:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            logger_settings.logger.error(
                'Job with id:{0} is in status: {1}'.format(job_id, get_job_status['data']['status']))
            self.result.append(self.failure)
            raise (UATError(ExceptionType.RETURN_VALUES, 'issue getting job status with qacct'))

    def _unit_ssh_out_err(self, directory):
        # TODO: alejandro investigate
        # adding delay, ssh is faster than the actual job execution
        time.sleep(10)

        # If err file (from scheduler) exist => something was wrong
        try:
            ret_job_err = nodeipexecute(self.remotehost, 'cat {0}/*.err'.format(directory + '/' + 'nonmem'))
            if len(ret_job_err) == 0:
                self.result.append(self.success)
                logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            else:
                self.result.append(self.failure)
                raise
        except Exception:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            raise (UATError(ExceptionType.RETURN_VALUES, 'there is something in err file'))

    def _unit_out(self, ret_api):
        job_id_value = str(ret_api['data']['jobId'])

        try:
            get_job_output = helpers.hpcapi_verbs.JobEndpoint.get_job_output(self.url, self.ticket, job_id_value)
            if not str(get_job_output['data']['error']):
                logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
                self.result.append(self.success)
            else:
                raise
        except Exception:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
            raise (UATError(ExceptionType.RETURN_VALUES, 'there is an error in job output'))

    def _unit_out_custom_command(self, custom_out, ret_api_command_param):
        '''
        :param custom_out:
        :param ret_api_command_param:
        '''
        if custom_out in str(ret_api_command_param['data']):
            logger_settings.logger.info(bcolors.OKGREEN + 'PASSED' + bcolors.ENDC)
            self.result.append(self.success)
        else:
            logger_settings.logger.info(bcolors.FAIL + 'FAILED' + bcolors.ENDC)
            self.result.append(self.failure)
