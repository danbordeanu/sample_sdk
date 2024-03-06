from sdk.sdk_base import HPCSDK


def userfun():
    print 'jo:job is done, so do something very crazy'






import os
import sys
from os import path
if __name__ == '__main__':
    if __package__ is None:
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
        from sdk.sdk_base_ssh import HPCSDK_SSH
    else:
        from ..sdk.sdk_base_ssh import HPCSDK_SSH




if __name__ == '__main__':
    try:
        mini_sdk = HPCSDK('https://host/api/v2', 'user', 'passwed==')
        # create
        mini_sdk.io_operations('create', new_dir='testsdkkk')
        # delete: 
        mini_sdk.io_operations('delete', delete_path='testsdkkk')
        # create new dir:
        mini_sdk.io_operations('create', new_dir='')
        # create
        mini_sdk.io_operations('create', new_dir='/N165F3')
        # upload: 

        mini_sdk.io_operations('upload', src_dir='/tmp', src_file='uploadme.txt', dst_dir='/N165F3')
        # mini_sdk.io_operations('upload', put_file_path='/N165F3/uploadme.txt', get_file_view='')
        # download: 
        mini_sdk.io_operations('get', get_file_path='/N165F3/uploadme.txt', get_file_view='')
        # sha: 
        mini_sdk.io_operations('sha', get_file_path='/N165F3/uploadme.txt', sha_type='SHA256')
        # share: 
        mini_sdk.io_operations('share', src_dir='/N165F3', isid='hpctestusertwo')
        # unshare: 
        mini_sdk.io_operations('ushare', src_dir='/N165F3', isid='hpctestusertwo')
        # delete: 
        mini_sdk.io_operations('delete', delete_path='N165F3')
        # job submit using an already uploaded file:
        mini_sdk.job_submit(job_name='myjob', content='', src_file_uploaded='/N165F3/uploadme.txt', grid='')
        # job submit content:
        mini_sdk.job_submit(job_name='myjob', content='echo 123', src_file_uploaded='', grid='')
        # job submit using command plugin:
        mini_sdk.command_submit(job_name='myjob', plugin_version='R331', code='-e print hello world',
                                dst_dir='/N165F3', grid='')

        # Monitoring example
        jobId = mini_sdk.job_submit(job_name='myjob', src_file_uploaded='/N165F3/uploadme.txt')
        
        mini_sdk.subscribe(jobId)

        mini_sdk.subscribe(jobId, userfun)

        print 'The main loop has finished!'

    except Exception as e:
        print 'Error: {0}'.format(e)
