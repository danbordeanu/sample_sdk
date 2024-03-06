from helpers.hpcapi_verbs.admin import login
from helpers import logger_settings
from helpers.colors import bcolors
import sys
import random

from helpers.hpcapi_verbs.fileEndpoint import create_dir
from helpers.hpcapi_verbs.fileEndpoint import delete_file
from helpers.hpcapi_verbs.fileEndpoint import upload
from helpers.hpcapi_verbs.fileEndpoint import get_file
from helpers.hpcapi_verbs.fileEndpoint import get_sha
from helpers.hpcapi_verbs.fileEndpoint import get_share
from helpers.hpcapi_verbs.fileEndpoint import get_unshare

import helpers.hpcapi_verbs.JobEndpoint
import base64
import string

from concurrent.futures import ThreadPoolExecutor
import time


class HPCSDK(object):
    def __init__(self, url, user, password):
        '''
        :param url: HPC API url endpoint
        :param user: HPC API user name
        :param password: HPC API user password in base64 format
        '''
        assert isinstance(url, str), 'URL should be string'
        assert isinstance(user, str), 'User should be string'
        assert isinstance(password, str), 'Password should be string'

        self.url = url
        self.user = user
        self.password = password

        self.futures = []
        self.content = None
        self.grid = None
        self.jobsubmission = None

        # self.filepath = 'QSPWBUSERS/' + self.user
        self.filepath = '' 
        self.ssh_path = '/SFS/hpcapi/dev/'
        self.full_absolute_path = self.ssh_path + self.filepath
        self.range = 6

        try:
            post_login = login(url + '/' + 'login', user, base64.b64decode(password))
            self.ticket = post_login['data']
            logger_settings.logger.info('Ticket returned by API is:{0}'.format(self.ticket))
        except Exception:
            logger_settings.logger.error('Something was very wrong logging:{0}'.format(str(sys.exc_info()[1])))

    def io_operations(self, command, **kwargs):
        '''

            # flag=create, "path/folder"
            # flag=delete, "path/folder"
            # flag=upload, path/folder"
            # flag=download ,"path/folder"
            # flag=sha, "path/folder"
            # flag=share, isid
            # flag=unshare, isid
            :param command:
            :param kwargs:
        '''
        args = dict(new_dir='', delete_path='', src_dir='', src_file='', dst_dir='', issid='', get_file_path='',
                    get_file_view='', sha_type='', isid='')

        diff = set(kwargs.keys()) - set(args.keys())

        if diff:
            logger_settings.logger.info('Invalid args:', tuple(diff))
            return

        args.update(kwargs)

        # TODO we might want to remove this
        logger_settings.logger.info('Arguments received {0}'.format(args))

        if command == 'create':
            assert isinstance(kwargs['new_dir'], str), 'new directory name must be specified'
            if not kwargs['new_dir']:
                try:
                    random_dir = ''.join(
                        random.choice(string.ascii_uppercase + string.digits) for _ in range(self.range))
                    ret_api = create_dir(self.url, self.filepath + '/' + random_dir, self.ticket)
                    ret_api = str(ret_api['data'])
                    logger_settings.logger.info(
                        'Dir with random name {0} created on server'.format(ret_api).replace(self.full_absolute_path,
                                                                                             ''))
                except Exception:
                    logger_settings.logger.error(bcolors.FAIL + 'Error creating new random directory' + bcolors.ENDC)
            else:
                try:
                    ret_api = create_dir(self.url, self.filepath + '/' + kwargs['new_dir'], self.ticket)
                    logger_settings.logger.info(
                        'Dir with custom name {0} created on server'.format(str(ret_api['data'])).replace(
                            self.full_absolute_path, ''))
                except Exception:
                    logger_settings.logger.error(bcolors.FAIL + 'Error creating new directory' + bcolors.ENDC)

        elif command == 'delete':
            assert isinstance(kwargs['delete_path'], str), 'path to dir/file must be specified in order to delete'
            if not kwargs['delete_path']:
                logger_settings.logger.info('Provide path do be deleted')
            else:
                try:
                    delete_file(self.url, self.ticket, self.full_absolute_path + '/' + kwargs['delete_path'])
                    logger_settings.logger.info('Path:{0} deleted'.format(self.ssh_path + self.filepath + '/' +
                                                                          kwargs['delete_path']))
                except Exception:
                    logger_settings.logger.error(bcolors.FAIL + 'Error deleting path' + bcolors.ENDC)

        elif command == 'upload':
            assert isinstance(kwargs['src_dir'], str), 'local dir source must be specified'
            assert isinstance(kwargs['src_file'], str), 'local file source must be specified'
            random_dir = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(self.range))
            if kwargs['src_file'] and kwargs['src_dir'] and not kwargs['dst_dir']:
                try:
                    ret_api_mkdir = create_dir(self.url, self.filepath + '/' + random_dir, self.ticket)
                    logger_settings.logger.info(
                        'Dir with random name {0} created on server'.format(ret_api_mkdir['data']))

                    ret_api_upload = upload(self.url, self.ticket, kwargs['src_dir'], kwargs['src_file'], 'true',
                                            ret_api_mkdir['data'])

                    logger_settings.logger.info(
                        'File uploaded:{0}'.format(ret_api_upload['data']['files'][0]).replace(self.full_absolute_path,
                                                                                               ''))
                except Exception:
                    logger_settings.logger.error(bcolors.FAIL + 'Error creating new random directory' + bcolors.ENDC)

            if kwargs['src_file'] and kwargs['src_dir'] and kwargs['dst_dir']:
                try:
                    ret_api_upload = upload(self.url, self.ticket, kwargs['src_dir'], kwargs['src_file'], 'true',
                                            self.ssh_path + self.filepath + '/' + kwargs['dst_dir'])
                    logger_settings.logger.info(
                        'File uploaded:{0}'.format(ret_api_upload['data']['files'][0]).replace(self.full_absolute_path,
                                                                                               ''))
                except Exception:
                    logger_settings.logger.error(bcolors.FAIL + 'Error uploading file' + bcolors.ENDC)

        elif command == 'get':
            assert isinstance(kwargs['get_file_path'], str), 'Path to file must be specified in order to download'
            assert isinstance(kwargs['get_file_view'], str), 'Must specify view type: DIR/RECUR, or empty'

            if kwargs['get_file_path'] and kwargs['get_file_view']:
                try:

                    ret_api = get_file(self.url, self.ticket, self.full_absolute_path + '/' + kwargs['get_file_path'],
                                       kwargs['get_file_view'])
                    logger_settings.logger.info('Api returned:{0}'.format(ret_api['data']))
                    return ret_api['data']
                except Exception:
                    logger_settings.logger.error(bcolors.FAIL + 'Error downloading file' + bcolors.ENDC)
            else:
                try:
                    get_file(self.url, self.ticket, self.full_absolute_path + '/' + kwargs['get_file_path'])
                    logger_settings.logger.info('File downloaded in /tmp dir on local disk')
                except Exception:
                    logger_settings.logger.error(bcolors.FAIL + 'Error downloading file' + bcolors.ENDC)

        elif command == 'sha':
            assert isinstance(kwargs['get_file_path'], str), 'Path to file must be specified in order to get sha'
            assert isinstance(kwargs['sha_type'], str), 'SHA type must be specified:SHA1/256/512, ' \
                                                        'if empty SHA1 will be used'
            if kwargs['get_file_path'] and kwargs['sha_type']:
                try:
                    ret_api = get_sha(self.url, self.ticket, self.filepath + kwargs['get_file_path'],
                                      kwargs['sha_type'])
                    logger_settings.logger.info('SHA file is {0}'.format(str(ret_api['data'][0]['hashCode'])))
                except Exception:
                    logger_settings.logger.error(bcolors.FAIL + 'Error getting sha file' + bcolors.ENDC)
            else:
                try:
                    ret_api = get_sha(self.url, self.ticket, self.filepath + kwargs['get_file_path'])
                    logger_settings.logger.info('SHA file is {0}'.format(str(ret_api['data'][0]['hashCode'])))
                except Exception:
                    logger_settings.logger.error(bcolors.FAIL + 'Error getting sha file' + bcolors.ENDC)

        elif command == 'share':
            assert isinstance(kwargs['src_dir'], str), 'Path  must be specified in order to share'
            assert isinstance(kwargs['isid'], str), 'Must specify user to share with'
            if kwargs['src_dir'] and kwargs['isid']:
                try:
                    get_share(self.url, self.ticket, self.full_absolute_path + kwargs['src_dir'], kwargs['isid'])
                except Exception:
                    logger_settings.logger.error(bcolors.FAIL + 'Error sharing directory' + bcolors.ENDC)

        elif command == 'unshare':
            assert isinstance(kwargs['src_dir'], str), 'Path  must be specified in order to unshare'
            assert isinstance(kwargs['isid'], str), 'Must specify user to unshare with'
            if kwargs['src_dir'] and kwargs['isid']:
                try:
                    get_unshare(self.url, self.ticket, self.full_absolute_path + kwargs['src_dir'], kwargs['isid'])
                except Exception:
                    logger_settings.logger.error(bcolors.FAIL + 'Error unsharing directory' + bcolors.ENDC)

        else:
            logger_settings.logger.info('We need a command in order to do some action')

    def command_submit(self, **kwargs):
        '''

        :param kwargs:
        :return:
        Method will submit a job calling the POST command plugin first and submitting the generated sh file into job submission
        '''

        assert isinstance(kwargs['job_name'], str), 'Job name must be specified'
        assert isinstance(kwargs['plugin_version'],
                          str), 'Plugin version must be specified'
        assert isinstance(kwargs['code'], str), 'Code must be provided'  # TODO replace this with reading from a file
        assert isinstance(kwargs['dst_dir'],
                          str), 'Destination of code must be provided'  # NB if path not provided API will return just the code
        assert isinstance(kwargs['grid'], str), 'Grid param must pe provided'
        assert isinstance(kwargs['jobsubmission'], str), 'Jobsubmission argument must be present'

        plugins_available = self.get_available_plugins()

        if not kwargs['job_name']:
            logger_settings.logger.info('It would be nice to give a name to your job :) '
                                        'Anyway, we will assign a random name for the job')
            kwargs['job_name'] = ''.join(
                        random.choice(string.ascii_uppercase + string.digits) for _ in range(self.range))

        if not kwargs['grid']:
            self.grid = None
        else:
            self.grid = kwargs['grid']

        if not kwargs['jobsubmission']:
            self.jobsubmission = None
        else:
            self.jobsubmission = kwargs['jobsubmission']

        if kwargs['plugin_version'] not in plugins_available:
            logger_settings.logger.info(
                'Uhh ohhh, plugin specified is not available.Use mini_sdk.get_available_plugins().')
        else:
            try:
                ret_api_submit_job = helpers.hpcapi_verbs.JobEndpoint.post_command_plugin_name(
                    self.url, self.ticket, kwargs['code'],
                    kwargs['plugin_version'],
                    kwargs['job_name'], self.full_absolute_path + kwargs['dst_dir'], self.grid, self.jobsubmission)

                logger_settings.logger.info('Command plugin: {0} '
                                            'submited'.format(str(ret_api_submit_job['data'])))

                job_id = str(ret_api_submit_job['data']['jobId'])
                logger_settings.logger.info('Job has id: {0}'.format(job_id))
                return job_id
            except Exception:
                logger_settings.logger.info('Error posting the command plugin')

    def job_submit(self, **kwargs):
        '''
        Method will submit a job calling POST:/job by using an already uploaded script
        :param kwargs:
        :return: jobId
        '''

        assert isinstance(kwargs['job_name'], str), 'Job name must be specified'
        assert isinstance(kwargs['src_file_uploaded'], str), 'Location of the uploaded file must be specified'
        assert isinstance(kwargs['content'], str), 'Content argument must be present'
        assert isinstance(kwargs['grid'], str), 'Grid argument must be present'
        assert isinstance(kwargs['jobsubmission'], str), 'Jobsubmission argument must be present'

        if not kwargs['job_name']:
            logger_settings.logger.info('It would be nice to give a name to your job :) '
                                        'Anyway, we will assign a random name for the job')
            kwargs['job_name'] = ''.join(
                        random.choice(string.ascii_uppercase + string.digits) for _ in range(self.range))

        if not kwargs['grid']:
            self.grid = None
        else:
            self.grid = kwargs['grid']

        if not kwargs['jobsubmission']:
            self.jobsubmission = None
        else:
            self.jobsubmission = kwargs['jobsubmission']

        if kwargs['content']:
            self.content = kwargs['content']
            try:
                data_post_job = helpers.hpcapi_verbs.JobEndpoint.post_job(
                    self.url,
                    self.ticket,
                    kwargs['job_name'],
                    self.content,
                    None,
                    self.grid,
                    self.jobsubmission
                )
                logger_settings.logger.info('Job using content '
                                            ': {0} submited on server'.format(str(data_post_job['data'])))
                job_id = str(data_post_job['data']['jobId'])
                return job_id
            except Exception:
                logger_settings.logger.info('Error posting the job using content')

        if kwargs['src_file_uploaded']:
            try:
                data_post_job = helpers.hpcapi_verbs.JobEndpoint.post_job(
                    self.url,
                    self.ticket,
                    kwargs['job_name'],
                    self.content,
                    self.full_absolute_path + kwargs['src_file_uploaded'],
                    self.grid,
                    self.jobsubmission
                )
                logger_settings.logger.info('Job using uploaded '
                                        'file: {0} submited on server'.format(str(data_post_job['data'])))
                job_id = str(data_post_job['data']['jobId'])
                return job_id
            except Exception:
                logger_settings.logger.info('Error posting the job using already uploaded script')

    def password_encode(self, password_string):
        '''
        Return base64 encoded password
        :param password_string:
        :return: encoded_password in base64 format
        '''
        try:
            encoded_password = base64.b64encode(password_string)
            return encoded_password
        except Exception:
            logger_settings.logger.info(
                'Something was very wrong encoding the password:{0}'.format(str(sys.exc_info()[1])))

    def get_available_plugins(self):
        '''
        Method will query GET /command
        :return: available plugins installed on cluster
        '''

        plugins = helpers.hpcapi_verbs.JobEndpoint.get_command(self.url, self.ticket)
        return plugins['data']

    def get_job_status(self, job_id):
        '''
        Get job status: DONE/RUNNING/QUEUD
        Method is calling Get job/job_info
        :param job_id:
        :return: status of job
        '''
        try:
            get_job_status = helpers.hpcapi_verbs.JobEndpoint.get_job_info(self.url, self.ticket, job_id)
            status = get_job_status['data']['status']
            logger_settings.logger.info('Job status is {0}'.format(status))
            return status
        except Exception:
            print 'exception on getting the status of job'

    def subscribe(self, job_id, userfun=None):
        '''
        Method will subscribe to listener and check job status
        :param job_id:
        :param userfun:
        :return:
        '''
        pool = ThreadPoolExecutor(1)

        if not (userfun is None):
            self.futures.append(pool.submit(self.checkhpc, job_id, userfun))
        else:
            self.futures.append(pool.submit(self.checkhpc, job_id))

    def checkhpc(self, job_id, userfun=None):
        '''
        Method will check the job status
        :param job_id:
        :param userfun:
        :return:
        '''
        while True:
            # TODO check errors of execution to prevent hangout
            if 'DONE' not in self.get_job_status(job_id):
                # print("waiting")
                time.sleep(2)
            else:
                if not (userfun is None):
                    userfun()
                else:
                    logger_settings.logger.info('Job status is {0}'.format(job_id))
                break
