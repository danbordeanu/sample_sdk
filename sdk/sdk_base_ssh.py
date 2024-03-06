# test 
import paramiko
import base64
import sys
import os
import ast
import socket
import re

from helpers import logger_settings
from helpers.Error import UATError
from helpers.Error import ExceptionType
# sys.path.append('..')

from concurrent.futures import ThreadPoolExecutor
import time

    
class HPCSDK_SSH(object):

    def __init__(self, hostname, custom_user=None, custom_password=None, custom_port=None, debug=None):

        self.hostname = hostname
        # self.user = ''
        # self.password = ''
        # self.port = ''
        self.ssh=''
        self.username = custom_user
        self.password = custom_password
        self.port= custom_port 
        self.futures = []
        self.debug_counter=0

        try:



            self.ssh = paramiko.SSHClient()
            # Policy for automatically adding the hostname and new host key to the local HostKeys object, and saving it.  
            # Interface for defining the policy that SSHClient should use when the SSH servers hostname is not in 
            # either the system host keys or the applications keys: adding the key to the applications HostKeys 
            # object (AutoAddPolicy), and for automatically rejecting the key (RejectPolicy).
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ret=self.ssh.connect(self.hostname, self.port, self.username, self.password)

            # TODO this is here just to catch any initial error at connecting, like module conflict 
            # import time
            # time.sleep(3)
            # ret=self.execute('ls')
            # logger_settings.logger.debug('Sucesfully connected'.format(ret))
            # logger_settings.logger.debug(ret)

        except paramiko.AgentKey as e:
            raise (UATError(ExceptionType.IO_SSH, ' at init ssh agent key [ {0} ]'.format(e)))

        # bad username/passw ---------------------------------------------------
        except paramiko.ssh_exception.PasswordRequiredException as e:
            raise (UATError(ExceptionType.IO_SSH, ' at init ssh - password required [ {0} ]'.format(e)))
        except paramiko.ssh_exception.AuthenticationException as e:
            raise (UATError(ExceptionType.IO_SSH, ' at init ssh - authentication failed [ {0} ]'.format(e)))
        except paramiko.ssh_exception.PartialAuthentication as e:
            raise (UATError(ExceptionType.IO_SSH, ' at init ssh - partial authentication failed [ {0} ]'.format(e)))
        except paramiko.ssh_exception.BadAuthenticationType as e:
            raise (UATError(ExceptionType.IO_SSH, ' at init ssh - authentication failed [ {0} ]'.format(e)))
        except paramiko.ssh_exception.BadHostKeyException as e:
            raise (UATError(ExceptionType.IO_SSH, ' at init ssh - server\'s host could not be verified [ {0} ]'.format(e)))

        except paramiko.ssh_exception.ProxyCommandFailure as e:
            raise (UATError(ExceptionType.IO_SSH, ' at init ssh - attemp to open a new channle fails] [ {0} ]'.format(e)))

        except paramiko.ssh_exception.ChannelException as e:
            raise (UATError(ExceptionType.IO_SSH, ' at init ssh - attemp to open a new channle fails] [ {0} ]'.format(e)))

        except paramiko.ssh_exception.NoValidConnectionsError as e:
            raise (UATError(ExceptionType.IO_SSH, ' at init ssh - not valid connnection [ {0} ]'.format(e)))

        except paramiko.ssh_exception.SSHException as e:
            raise (UATError(ExceptionType.IO_SSH, ' at init ssh - socket is open, but not SSH service responded [ {0} ]'.format(e)))

        except socket.timeout as e:
            raise (UATError(ExceptionType.IO_SSH, ' at init ssh - password is invalid [ {0} ]'.format(e)))

        except Exception as ee:
            raise (UATError(ExceptionType.IO_SSH, ' unexpected exeption at constructor probably not paramiko related but network/proxy [ {0} ]'.format(ee)))
            # self.ssh.close()
        if not (debug is None):

            if debug == ':debug:':
                logger_settings.logger.info('Fake mode for debugging, not stablishing SSH connection')

            else: 
                logger_settings.logger.error('Wrong option: {0}'.format(debug) )

        else:

            try:
                self.ssh = paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                ret=self.ssh.connect(self.hostname, self.port, self.username, self.password)
                # TODO this is here just to catch any initial error at connecting, like module conflict 
                # import time
                # time.sleep(3)
                # ret=self.execute('ls')
                # print(ret)

            except paramiko.AgentKey as e:
                raise (UATError(ExceptionType.IO_SSH, ' at init ssh agent key [ {0} ]'.format(e)))
            except paramiko.AuthenticationException as e:
                raise (UATError(ExceptionType.IO_SSH, ' at init ssh authentication failed because some reason [ {0} ]'.format(e)))
            except paramiko.BadHostKeyException as e:
                raise (UATError(ExceptionType.IO_SSH, ' at init ssh server\'s host could not be verified [ {0} ]'.format(e)))
            except paramiko.SSHException as e:
                raise (UATError(ExceptionType.IO_SSH, ' at init ssh password is invalid [ {0} ]'.format(e)))
            except Exception as ee:
                raise (UATError(ExceptionType.IO_SSH, ' unexpected exeption at constructor [ {0} ]'.format(ee)))
                # self.ssh.close()



    def job_submit(self, **kwargs):

        # in SFS/scratch/username
        # qsub -P normal -cwd -V -b y -l mem_free=20G -l virtual_free=20G -l mem_reserve=20G -l h_vmem=20G run.sh ;
        # qstat -j 36886 | grep job_state
        # job_state             1:    r

        # qacct -j thejob | grep failed 
        # >
        # failed 0

        job_id="123456789"

        for arg in kwargs:
            logger_settings.logger.debug('<arg> {0} <value> {1}:'.format(arg, kwargs[arg]))

        # check if we are parsing a "qsub params" string to be sumbitted
        literal=False
        for arg in kwargs:
            if arg == ':literal:':
                literal=True

        if literal == True:
            try:
                print("using {0}".format(kwargs['job']))
                ret=self.execute(kwargs['job'])

                matchObj = re.match( rb'Your job.* has been submitted', ret, re.M|re.I)
                if matchObj:
                   return matchObj.group().split()[2]
                else:
                   raise (UATError(ExceptionType.ARGUMENTS))

            except Exception as e:
                # print(e)
                raise (UATError(ExceptionType.ARGUMENTS, "at job_submit - {0}".format(e)))
        else:
            try:
                # TODO this is from the api, lets try to adapt to the SSH

                print("executing job submission {0}".format(kwargs['job_name']))
                return job_id


                '''
                Method will submit a job calling POST:/job by using an already uploaded script
                :param kwargs:
                :return: jobId
                '''
                print("executing job submission {0}".format(kwargs['job']))

                assert isinstance(kwargs['job_name'], str), 'Job name must be specified'
                assert isinstance(kwargs['src_file_uploaded'], str), 'Location of the uploaded file must be specified'
                assert isinstance(kwargs['content'], str), 'Content argument must be present'
                assert isinstance(kwargs['grid'], str), 'Grid argument must be present'
                assert isinstance(kwargs['jobsubmission'], str), 'Jobsubmission argument must be present'

                for i in kwargs:
                    print(i)

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
                        # job_id = str(data_post_job['data']['jobId'])
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
                        # job_id = str(data_post_job['data']['jobId'])
                        return job_id
                    except Exception:
                        logger_settings.logger.info('Error posting the job using already uploaded script')
            except Exception as e:
                print("error due to: ", e)
                raise (UATError(ExceptionType.ARGUMENTS, e))

# https://www.programcreek.com/python/example/7495/paramiko.SSHException
     # try:
        # log.info("Getting SCP Client")
        # scpclient = scp.SCPClient(client.get_transport())
        # log.info(scpclient)
        # log.info("Hostname: %s", hostname)
        # log.info("source file: %s", sfile)
        # log.info("target file: %s", tfile)
        # scpclient.put(sfile,tfile)
     # except scp.SCPException as e:

    
    def execute(self, cmd):
        '''
        Execute terminal cmds  
        '''

        try:
            # thecmd = 'Command to be executed {0} on server {1}'.format(cmd, self.hostname)
            # logger_settings.logger.debug(thecmd)
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            stderr_print = stderr.read().rstrip()
            stdout_print = stdout.read().rstrip()
            ret = {'stderr': stderr_print, 'stdout': stdout_print}

            # Examining return value from previous execution and raise an exception if necessary
            msg = '[ ' + cmd + ' ]' + ' -> Successful'

            # Nothing to be returned
            if len(stderr_print) == 0 and len(stdout_print) == 0:
                # logger_settings.logger.info(msg)
                return ''

            # Standard return
            elif len(stderr_print) == 0 and len(stdout_print) != 0:
                # logger_settings.logger.info(msg)
                msg2 = 'stdout = ' + stdout_print
                # logger_settings.logger.info(msg2)
                return stdout_print

            # Error return
            else:
                # return ret.get('stderr')
                return ret.get('stdout')
                # logger_settings.logger.info('stderr= {0} '.format(ret.get('stderr')))
                # logger_settings.logger.info('stdout= {0} '.format(ret.get('stdout')))
                # msg = str(ret.get('stderr')) + ' at function execute mm '
                # raise (UATError(ExceptionType.IO_SSH, msg))

        except paramiko.AgentKey as e:
            raise (UATError(ExceptionType.IO_SSH, ' at execute ssh agent key [ {0} ]'.format(e)))
        except paramiko.AuthenticationException as e:
            raise (UATError(ExceptionType.IO_SSH, ' at execute ssh authentication failed because some reason [ {0} ]'.format(e)))
        except paramiko.BadHostKeyException as e:
            raise (UATError(ExceptionType.IO_SSH, ' at execute ssh server\'s host could not be verified [ {0} ]'.format(e)))
        except paramiko.SSHException as e:
            raise (UATError(ExceptionType.IO_SSH, ' at execute ssh password is invalid [ {0} ]'.format(e)))
        except Exception as ee:
            raise (UATError(ExceptionType.IO_SSH, ' at execute SSH unexpected exception [ {0} ]'.format(ee)))
        # finally:
            # self.ssh.close()


    def subscribe(self, job_id, userfun=None):
        '''
        > Subscribing to a future whose promise is the jobid=DONE 
        > When done it will call userfun case is not None, otherwise 
        will print (logger.info) the job status
        '''
        pool = ThreadPoolExecutor(1)

        if userfun is not None:
            logger_settings.logger.info('Subscribing to job with userfun')
            self.futures.append(pool.submit(self.checkhpc, job_id, userfun))
        else:
            logger_settings.logger.info('Subscribing to job without userfun')
            self.futures.append(pool.submit(self.checkhpc, job_id))

    def checkhpc(self, job_id, userfun=None):
        '''
        > calling self.get_job_status and when finish execute userfun
        or print (logger.info) the job status
        '''
        while True:
            # TODO check errors of execution to prevent hangout
            # TODO check if the job is in ERROR

            if 'DONE' not in self.get_job_status(job_id):
                logger_settings.logger.info('waiting...')
                time.sleep(2)
            else:
                if userfun is None:
                    logger_settings.logger.info('Job {0} is DONE '.format(job_id))
                else:
                    userfun()
                break 

            
    def get_job_status(self, job_id):

        '''
        Get job status: DONE/RUNNING/QUEUED by calling qstat for the jobid
        '''

        # if self.debug_counter>6:
            # print('FINISHED')
            # return 'DONE' 

        # self.debug_counter=self.debug_counter+1
        job_status=""
        cmd = 'qstat -j ' + job_id 
        cmd2 = 'qacct -j ' + job_id 

        try:

            logger_settings.logger.info('Executing: {0}'.format(cmd))

            job_status=self.execute(cmd)
            # print(job_status)

            if job_status != '':

                # logger_settings.logger.info('Job status is {0}'.format(job_status))

                # self.analize_job_status(job_status, 'qstat')

                # return job_status
                # TODO when cannot be executed qstat remains in 
                #job_state             1:    Eqw
                # so this can be used for check
                return "RUNNING"


            # TODO inspect this in the future
            # job_status=self.execute(cmd2)
            # if job_status != '':
                # # logger_settings.logger.info('Executing: {0}'.format(cmd2)) 
                # self.analize_job_status(job_status, 'qacct')
                # # return job_status
                # return "RUNNING"

            # TODO cat /sfs/scratc/user/jobname.ejobid if empty => job finished
           # execute() 
            return "DONE"

        except Exception as e:
            raise (UATError(ExceptionType.IO_SSH, ' at get_job_status: [ {0} ]'.format(e)))

    def analize_job_status(self, job_status, monitor_type):

        from StringIO import StringIO

        try:

            # TODO fine grained check
            # we have to check if the -wdrun.shh.ejobid is empty or not
            # submit_cmd   qsub -V -b y -l mem_free=20G -l virtual_free=20G -l mem_reserve=20G -l h_vmem=20G -wd /SFS/scratch/username/ /home/username/SUB/run.shh
            # if we provide a name at submission time, is easier to locate the job:
            # testing.e37040*  instead of run.ssh.e37040

            if job_status != '':

                lines = (job_status.split('\n'))

                nbr_lines= len(job_status.split('\n'))
                print("number of olines ", nbr_lines) 
                for line in lines:
                    if monitor_type == 'qstat':
                        return "RUNNING"
                    elif monitor_type == 'qacct':

                        searchObj = re.search( r'job_state', line, re.M|re.I)
                        if searchObj:
                            print(line)
        except Exception as e:
            print(e)
        return 'RUN'




  
    def ssh_close(self):
        try:
            self.ssh.close()
            logger_settings.logger.info('Session paramiko closed')
        except paramiko.AgentKey as e:
            raise (UATError(ExceptionType.IO_SSH, ' at execute ssh agent key [ {0} ]'.format(e)))
        except paramiko.AuthenticationException as e:
            raise (UATError(ExceptionType.IO_SSH, ' at execute ssh authentication failed because some reason [ {0} ]'.format(e)))
        except paramiko.BadHostKeyException as e:
            raise (UATError(ExceptionType.IO_SSH, ' at execute ssh server\'s host could not be verified [ {0} ]'.format(e)))
        except paramiko.SSHException as e:
            raise (UATError(ExceptionType.IO_SSH, ' at execute ssh password is invalid [ {0} ]'.format(e)))
        except Exception as ee:
            raise (UATError(ExceptionType.IO_SSH, ' at execute SSH unexpected exception [ {0} ]'.format(ee)))


