# HPCAPI Python SDK

A python-based SDK for the [HPCAPI-WS] project.


## Introduction && Installation

A  simple and yet quite flexible python-based SDK intended to simplify  the development of a client application that uses the RESTfull HPCAPI to access the cluster services.




#### Installation

Simply clone this repo and use the code as in the provided example: `sdk_use.py`
You need a valid account to access the HPC.

The user's password must be provided in base64 format.
The below snippet will encode your `password` in the required base64 format (you might have to install base64 firstly: pip install pybase64).
A script with the below code is in the repository:

```python
    import base64

    passw=base64.b64encode("user_passw")
    print "",passw
```
 



## Examples

* login to the cluster (opening a sesstion)
* submit jobs to the cluster scheduler 
* interact with the storage sytem (uploading/downloadig, deleting, sharing folders wiht another user).

In the below examples you can find all the  possible operations:

 


##### Example 1: opening a session in the cluster
```python
from sdk.sdk_base import HPCSDK

if __name__ == '__main__':

    try:
        URL = 'https://host/api/v2'
        USER = 'user_name'
        PASSWORD = 'user_encoded_password'

        # Opening a new session into the cluster
        sdk = HPCSDK(URL, USER, PASSWORD)
 
    except Exception as e:
        logger_settings.logger.info('Error: {0}' .format(e))
```

##### Example 2: file operations
```python
from sdk.sdk_base import HPCSDK

if __name__ == '__main__':

    try:
        URL = 'https://host/api/v2'
        USER = 'user_name'
        PASSWORD = 'user_password'

        # Opening a new session into the cluster
        sdk = HPCSDK(URL, USER, PASSWORD)

        # create a new folder with name MMM into users directory
        sdk.io_operations('create', new_dir='/MMM')
        # delete the folder: 
        sdk.io_operations('delete', delete_path='MMM')
        # create a folder with random name into useres directory:
        sdk.io_operations('create', new_dir='')
        # upload a local file to the previously created folder MMM:
        sdk.io_operations('upload', src_dir='/tmp', src_file='text.txt', dst_dir='/MMM')
        # download the file: 
        sdk.io_operations('get', get_file_path='/MMM/text.txt', get_file_view='')
        # list the files in the cluster in the folder: 
        sdk.io_operations('get', get_file_path='/MMM', get_file_view='DIR')
        # get the sha signature of somefile (available: SHA, SHA256, SHA512): 
        sdk.io_operations('sha', get_file_path='/MMM/text.txt', sha_type='SHA256')
        # share the file with another user: 
        sdk.io_operations('share', src_dir='/MMM', isid='user_guest')
        # unshare the file: 
        sdk.io_operations('ushare', src_dir='/N165F3', isid='user_guest')
 
    except Exception as e:
        print 'Error: {0}' .format(e)
```
##### Example 3: submitting jobs to the cluster

```python
from sdk.sdk_base import HPCSDK

if __name__ == '__main__':

    try:
        URL = 'https://host/api/v2'
        USER = 'user_name'
        PASSWORD = 'user_password'

        # Opening a new session into the cluster
        sdk = HPCSDK(URL, USER, PASSWORD)


        # Submiting a single command line job
        sdk.job_submit(job_name='myjob', 
                content='echo 123', src_file_uploaded='', grid='', jobsubmission='')
        # Submiting a single job to the cluster scheduler using an uploaded file
        sdk.job_submit(job_name='myjob', 
                content='', src_file_uploaded='/MM/text.txt', grid='', jobsubmission='')
        # Submiting a single job to the cluster scheduler using an uploaded file 
        # and providing jobsubmission extra parameters 
        sdk.job_submit(job_name='myjob', 
                content='', src_file_uploaded='/MM/text.txt', grid='', jobsubmission='-P normal -l mem_reserve=128M')
        # Submiting a single job to the fast execution queue using an uploaded file
        sdk.job_submit(job_name='myjob', 
                content='', src_file_uploaded='/MM/text.txt', grid='local', jobsubmission='')
        # Submiting a job (to the cluster scheduler vs to the fast execution queue) by first 
        # getting the correct environment using command plugin 
        sdk.get_available_plugins()
        sdk.command_submit(job_name='myjob', plugin_version='R331', code='-e print hello world', dst_dir='/MM', 
                    grid='', jobsubmission='')
        sdk.command_submit(job_name='myjob', plugin_version='R331', code='-e print hello world', dst_dir='/MM', 
                    grid='local', jobsubmission='')
        sdk.command_submit(job_name='myjob', plugin_version='R331', code='-e print hello world', dst_dir='/MM', 
                    grid='local', jobsubmission='-P normal -l mem_reserve=128M')

    except Exception as e:
        logger_settings.logger.info('Error: {0}' .format(e))
```
##### Example 4: asyncronous non-blocking job monitoring

```python
from sdk.sdk_base import HPCSDK

def userfun():
    print 'job is done, execute some code'

if __name__ == '__main__':

    try:
        URL = 'https://host/api/v2'
        USER = 'user_name'
        PASSWORD = 'user_password'

        # Opening a new session into the cluster
        sdk = HPCSDK(URL, USER, PASSWORD)

        # Submiting a single command line job
        jobId = sdk.job_submit(job_name='myjob', content='echo 123', src_file_uploaded='', grid='', jobsubmission='')
        
        # Monitoring the job and printing on screen "DONE" when finished
        sdk.subscribe(jobId)

        # Monitoring the job and calling back the user defined function: userfun()
        # when the job is finished
        sdk.subscribe(jobId, userfun)

        # Since the previous "sdk.subscribe" calls will be running on different threads,
        # the user can continue introducing commands at this point

 
    except Exception as e:
        logger_settings.logger.info('Error: {0}' .format(e))
```






