import requests
from .. import logger_settings


# TODO: error handling as usual
def get_version(url):
    try:
        url_version = url + '/version'
        print url_version
        logger_settings.logger.info('Accessing, {0}'.format(url_version))
        r = requests.get(url_version)
        data = r.json()
        #print('Json : {}'.format(data))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        print e
    except requests.exceptions.HTTPError as e:
        print e
    except requests.exceptions.TooManyRedirects as e:
        logger_settings.logger.debug('Redirect with reason, {0}'.format(e))
    except requests.exceptions.RequestException as e:
        print e
    except:
        logger_settings.logger.debug('No idea')
