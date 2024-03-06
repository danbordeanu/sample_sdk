

import base64
import os
import sys
from os import path


if __name__ == '__main__':
    if __package__ is None:
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
        from sdk.sdk_base_ssh import HPCSDK_SSH
        from sdk.sdk_factory import SDK_FACTORY
        from helpers.unit_paramiko.nodeip import nodeipexecute

        from helpers.Error import UATError
        from helpers.Error import ExceptionType

    else:
        from ..sdk.sdk_base_ssh import HPCSDK_SSH
        from ..sdk.sdk_factory import SDK_FACTORY
        from ..helpers.unit_paramiko.nodeip import nodeipexecute
        from ..helpers.Error import UATError
        from ..helpers.Error import ExceptionType


def execute():
    msg='jobid'
    print("Userfun called for: {0} ".format(msg)) 




remotehost = 'host'


# Checking credentials ---------------------------------------------------------
# After codifying the user passworkd using the b64sencode script provided in the root folder
# you have to make it available in your environment:
# hpckey="..."
# export hpckey
password=''
username=''
try:
    password = base64.b64decode(os.environ['hpc_key'] )
    username = os.environ['hpc_user']
    # print("Username: {0}".format(username))
except Exception as e:
    print("problem: {0}".format(e))
    sys.exit()

    
# Using the api ----------------------------------------------------------------
sdk=""
try:

    sdk=SDK_FACTORY('SSH', remotehost,  username, password, '2022')

    # job="qsub -N testing -V -b y -l mem_free=20G -l virtual_free=20G -l mem_reserve=20G -l h_vmem=20G -wd /SFS/scratch/username/ /home/username/SUB/run.sh"
    # job="qsub -N testing -V -b y -l mem_free=20G -l virtual_free=20G -l mem_reserve=20G -l h_vmem=20G  /home/username/SUB/run.sh"

    # Submit a "literal" string to the scheduler -------------------------------
    job=str("qsub -N testing -V -b y -l mem_free=20G -l virtual_free=20G -l mem_reserve=20G -l h_vmem=20G -wd /tmp60days/{0}/ /home/{0}/SUB/run.sh".format(username) )
    kwargs = {':literal:' : 'yes', "job": job}
    print(job)
    jobid = sdk.job_submit(**kwargs)

    # Asyncronous job monitoring -----------------------------------------------
    # Option A:
    # sdk.subscribe(jobid)
    # Option B:
    sdk.subscribe(jobid, execute)

    # Execute a command in the cluster shell -----------------------------------
    ret = sdk.execute('cd SUB; ls')
    print('Content of ~/SUB/: ',ret)

except UATError as e:
    print(e.emsg())
    # logger_settings.logger.info('FAILED at main: {0}'.format(e.emsg('asString')))
    # raise (UATError(ExceptionType.RETURN_VALUES, 'at FileCreateTest {0}'.format(e.emsg()))) T3Nvc2Ftb3Jvc29zMjAxOTQ=
except Exception as ee:
    print(ee)
finally:
    print("finish")
    sdk.ssh_close()



