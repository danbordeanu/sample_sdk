import requests
from .. import logger_settings

# error
from helpers.Error import UATError
from helpers.Error import ExceptionType

def login(url, user, passwd):
    # type: (object, object, object) -> object
    try:
        data = {'login': user, 'password': passwd}
        logger_settings.logger.debug('User: {0} is logging in using this url:{1}'.format(user, url))
        r = requests.post(url, data)
        logger_settings.logger.debug('Returned token: {0}'.format(data))
        data = r.json()
        # print('Json : %s' % str(data))
        # print('Json : %s' % str(data['message']))
        # if str(data['message'])  in 'Wrong credentials':
            # raise (UATError(ExceptionType.HPCAPI, ' Authentication error: {0}'.format(str(data['message']) )))
        r.raise_for_status()
        return data

    except UATError as e:
        raise (UATError(ExceptionType.HPCAPI, '{0}',e.emsg()))

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at loging [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at loging [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at loging [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at loging [ {0} ]'.format(e)))

    except e:
        logger_settings.logger.debug('No idea {0} '.format(e))
        raise (UATError(ExceptionType.HPCAPI, ' at loging'))


def logout(url, ticket):
    # This function will invalidate login token
    try:
        url = url + '/logout' + '?ticket=' + ticket
        logger_settings.logger.debug('Ticket {0} will be invalidated'.format(str(ticket)))
        r = requests.get(url)
        data = r.json()
        # print('Json : %s' % str(data))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at logout [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at logout [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at logout [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at logout [ {0} ]'.format(e)))

    except:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at logout'))
