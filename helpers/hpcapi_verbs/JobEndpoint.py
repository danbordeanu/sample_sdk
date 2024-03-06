import requests
from .. import logger_settings
from helpers.Error import ExceptionType
from helpers.Error import UATError
from requests_toolbelt.multipart.encoder import MultipartEncoder
# from requests_toolbelt.utils import dump


# Will encapsulate in a bash script with correspoinding environment ready for submission, whatever cmdline is provided
# if path parameter specified, service will save the plugin generated script to given path and post the job to execute that scrip
# otherwise will use random folder

def post_command_plugin_name(url, ticket, cmdline, plugin_name, appname, path=None, grid=None, jobsubmission=None):

    # type: (object, object, object, object, object, object, object, object) -> object
    '''
    :param url:
    :param ticket:
    :param cmdline:
    :param plugin_name:
    :param path:
    :param appname:
    :param grid:
    :param jobsubmission:
    :return:
    '''
    try:
        url = url + '/' + 'command' + '/' + plugin_name
        assert isinstance(grid, object)
        # TODO: parameters not in the right order
        if grid is None:
            data = dict(ticket=ticket, cmdline=cmdline, plugin_name=plugin_name, path=path, execution='grid',
                        appname=appname, jobsubmission=jobsubmission)
        else:
            data = dict(ticket=ticket, cmdline=cmdline, plugin_name=plugin_name, path=path, execution=grid,
                        appname=appname, jobsubmission=jobsubmission)

        r = requests.post(url, data)
        r.raise_for_status()
        data = r.json()
        # print 'data is {0})'.format(str(data))
        if str(data['success']) is 'False':
            print 'Json: {0}'.format(str(data))
            raise (UATError(ExceptionType.HPCAPI_RET_FALSE, ' unsuccessful job submission'))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at post_command_plugin_name [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at post_command_plugin_name [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at post_command_plugin_name [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at post_command_plugin_name [ {0} ]'.format(e)))

    except Exception:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at post_command_plugin_name'))


def get_job_info(url, ticket, jobid):
    # type: (object, object, object) -> object
    """
    :param url:
    :param ticket:
    :param jobid:
    """
    try:
        url = url + '/' + 'job' + '/' + jobid + '/' + 'info' + '?ticket=' + ticket
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        #print 'data job info{0})'.format(str(data))
        if str(data['success']) is 'False':
            print 'Json: {0}'.format(str(data))
            raise (UATError(ExceptionType.HPCAPI_RET_FALSE, ' unsuccessful'))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at get_job_info [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at get_job_info [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at get_job_info [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at get_job_info [ {0} ]'.format(e)))

    except Exception:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at get_job_info'))


def get_job_status(url, ticket, jobid):
    # !!!NB!!! This is a websocket endpoint
    # type: (object, object, object) -> object
    """
    :param url:
    :param ticket:
    :param jobid:
    """
    try:
        url = url + '/' + 'job' + '/' + jobid + '/' + 'status' + '?ticket=' + ticket
        print url
        r = requests.get(url, headers='Accept: application/json')
        print r.raise_for_status()
        data = r.json()
        print r.text
        print 'data job status {0})'.format(str(data))
        if str(data['success']) is 'False':
            print 'Json: {0}'.format(str(data))
            raise (UATError(ExceptionType.HPCAPI_RET_FALSE, ' unsuccessful'))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at get_job_status [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at get_job_status [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at get_job_status [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at get_job_status [ {0} ]'.format(e)))

    except Exception:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at get_job_status'))


def get_job_output(url, ticket, jobid):
    # type: (object, object, object) -> object
    '''
    :param url:
    :param ticket:
    :param jobid:
    :return:
    '''
    try:
        url = url + '/' + 'job' + '/' + jobid + '/' + 'output' + '?ticket=' + ticket
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        #print 'data job info {0})'.format(str(data))
        if str(data['success']) is 'False':
            print 'Json: {0}'.format(str(data))
            raise (UATError(ExceptionType.HPCAPI_RET_FALSE, ' unsuccessful'))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at get_job_output [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at get_job_output [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at get_job_output [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at get_job_output [ {0} ]'.format(e)))

    except Exception:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at get_job_output'))


def post_job(url, ticket, appname, content=None, path=None, grid=None, jobsubmission=None):
    # type: (object, object, object, object, object, object, object) -> object
    """
    :param url:
    :param ticket:
    :param content:
    :param appname:
    :param path:
    :param grid:
    :param jobsubmission:
    """
    try:
        url_job = url + '/' + 'job' + '?ticket=' + ticket
        if grid is None:
            m = MultipartEncoder(
                fields=dict(path=path, content=content, appname=appname, execution='grid', jobsubmission=jobsubmission))
        else:
            m = MultipartEncoder(
                fields=dict(path=path, content=content, appname=appname, execution=grid, jobsubmission=jobsubmission))

        r = requests.post(url_job, data=m, headers={'Content-Type': m.content_type})
        r.raise_for_status()
        data = r.json()
        if str(data['success']) is 'False':
            print 'Json: {0}'.format(str(data))
            raise (UATError(ExceptionType.HPCAPI_RET_FALSE, ' unsuccessful'))
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at post_job [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at post_job [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at post_job [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at post_job [ {0} ]'.format(e)))

    except Exception:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at post_job'))


def post_job_array(url, ticket, path, appname, beginindex, endindex):
    #TODO no need to have begin and end index, can be used as a single list
    """
    :param url:
    :param ticket:
    :param path:
    :param appname:
    :param beginindex:
    :param endindex:
    """
    try:
        url_job_array = url + '/' + 'job' + '/' + 'array' + '?ticket=' + ticket
        print url_job_array
        print appname, path, beginindex, endindex
        m = MultipartEncoder(
                fields=dict(path=path, appname=appname, beginIndex=beginindex, endIndex=endindex))
        r = requests.post(url_job_array, data=m, headers={'Content-Type': m.content_type})
        #debugging the requests response
        #data = dump.dump_all(r)
        #print data.decode('utf-8')
        r.raise_for_status()
        data = r.json()
        if str(data['success']) is 'False':
            print 'Json: {0}'.format(str(data))
            raise (UATError(ExceptionType.HPCAPI_RET_FALSE, ' unsuccessful'))
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at post_job_array [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at post_job_array [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at post_job_array [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at post_job_array [ {0} ]'.format(e)))

    except Exception:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at post_job_array'))


def get_command(url, ticket):
    # type: (object, object, object) -> object
    """
    :param url:
    :param ticket:
    """
    try:
        url = url + '/' + 'command' + '?ticket=' + ticket
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        #print 'data get command {0})'.format(str(data))
        if str(data['success']) is 'False':
            print 'Json: {0}'.format(str(data))
            raise (UATError(ExceptionType.HPCAPI_RET_FALSE, ' unsuccessful'))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at get_command [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at get_command [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at get_command [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at post_job_array [ {0} ]'.format(e)))

    except Exception:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at get_command'))
