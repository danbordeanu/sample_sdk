import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from .. import logger_settings
import os

from helpers.Error import ExceptionType
from helpers.Error import UATError


# import os.path

def put_file(url, ticket, filepath, content):
    try:
        url = url + '/file' + '?ticket=' + ticket + '&path=' + filepath + '&content=' + content
        r = requests.put(url)

        data = r.json()
        if str(data['success']) is 'False':
            print('Json : %s' % str(data))
            raise (UATError(ExceptionType.HPCAPI_RET_FALSE, ' unsucesfull'))
        # print('Json : %s' % str(data))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at put_file [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at put_file [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at put_file [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at put_file [ {0} ]'.format(e)))

    except:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at put_file'))


def delete_file(url, ticket, filepath):
    try:

        logger_settings.logger.info('Trying to delete file {0}'.format(filepath))
        url = url + '/file' + '?ticket=' + ticket + '&path=' + filepath
        r = requests.delete(url)
        data = r.json()
        # print('Json : %s' % str(data))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at delete_file [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at delete_file [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at delete_file [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at delete_file [ {0} ]'.format(e)))

    except:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at delete_file'))


# Download AND/OR list files
# TODO this is not finished
def get_file(url, ticket, filepath, view=None):
    try:

        logger_settings.logger.info('Trying to Download/List {0}'.format(filepath))

        if view is None:
            # get the file
            url = url + '/file' + '?ticket=' + ticket + '&path=' + filepath
            r = requests.get(url)

            filename = os.path.basename(filepath)
            if r.status_code == 200:
                with open("/tmp/" + filename, 'wb') as f:
                    f.write(r.content)
            return

        elif view is 'DIR':
            url = url + '/file' + '?ticket=' + ticket + '&view=' + view + '&path=' + filepath
        elif view is 'RECUR':
            url = url + '/file' + '?ticket=' + ticket + '&view=' + view + '&path=' + filepath
        else:
            raise (UATError(ExceptionType.ARGUMENTS, ' wrong arguments at get_file'))
        r = requests.get(url)
        data = r.json()
        #print('Json: %s' % str(data))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at get_file [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at get_file [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at get_file [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at get_file [ {0} ]'.format(e)))

    except:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at get_file'))


# TODO: check multiple isids
def get_share(url, ticket, filepath, isid):
    try:

        logger_settings.logger.info('Trying to share {0} with {1}'.format(filepath, isid))

        url_share = url + '/share' + '?ticket=' + ticket + '&path=' + filepath + '&isid=' + isid
        r = requests.get(url_share)
        data = r.json()
        # print('Json : %s' % str(data))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at get_share [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at get_share [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at get_share [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at get_share [ {0} ]'.format(e)))

    except:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at get_share'))


# TODO: check multiple isids
def get_unshare(url, ticket, filepath, isid):
    try:

        logger_settings.logger.info('Trying to unshare {0} with {1}'.format(filepath, isid))

        url = url + '/unshare' + '?ticket=' + ticket + '&path=' + filepath + '&isid=' + isid
        r = requests.get(url)
        data = r.json()
        # print('Json : %s' % str(data))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at get_unshare [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at get_unshare [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at get_unshare [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at get_unshare [ {0} ]'.format(e)))

    except:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at get_unshare'))


# Uploads to an specific location.
# if none is specified then creates a random folder
# filepath, filename = from the local file to be uploaded
def upload(url, ticket, filepath, filename, binary, filepath_server=None):
    try:
        file_route_local_file = filepath + '/' + filename
        url_upload = url + '/file' + '?ticket=' + ticket

        # print 'uploading:', file_route_local_file

        if filepath_server is None:
            m = MultipartEncoder(
                fields=dict(binary=binary, content=(filename, open(file_route_local_file, 'rb').read(), 'text/plain')))
        else:
            m = MultipartEncoder(fields=dict(binary=binary, path=filepath_server, content=(
                filename, open(file_route_local_file, 'rb').read(), 'text/plain')))

        r = requests.post(url_upload, data=m, headers={'Content-Type': m.content_type})

        data = r.json()
        if str(data['success']) is 'False':
            print('Json : %s' % str(data))
            raise (UATError(ExceptionType.HPCAPI_RET_FALSE, ' unsucesfull'))
        # print('Json : %s' % str(data))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:
        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at upload [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at upload [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at upload [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at upload [ {0} ]'.format(e)))

    except:
        logger_settings.logger.debug('No idea')
        raise (UATError(ExceptionType.HPCAPI, ' at upload'))


# TODO: check other types of sha: 256,512
def get_sha(url, ticket, path, shatype=None):
    try:
        if shatype is None:
            url_sha = url + '/file/sha' + '?ticket=' + ticket + '&path=' + path
        else:
            url_sha = url + '/file/sha' + '?ticket=' + ticket + '&path=' + path + '&sha=' + shatype
        print url_sha
        logger_settings.logger.info('Accesing, {0}'.format(url_sha))
        r = requests.get(url_sha)
        data = r.json()
        # print('Json : %s' % str(data))
        #  hash = str( data['data'][0]['hashCode'])
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:

        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at get_sha [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:

        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at get_sha [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:

        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at get_sha [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:

        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at get_sha [ {0} ]'.format(e)))

    except:

        logger_settings.logger.debug('No idea')

        raise (UATError(ExceptionType.HPCAPI, ' at get_sha'))


def create_dir(url, dirname, ticket):
    # '''
    # This function will create a directory using HPC-API
    # Take a look on swagger 8080/v2/docs/#!/File/post_file_create
    # curl -X POST --header 'Content-Type: application/x-www-form-urlencoded' --header 'Accept: application/json' -d
    # 'name=12345' 'http://ip:8080/api/v2/file/create?ticket=token'
    # :param dirname:
    # :return:
    # '''
    try:
        url = url + '/file/create' + '?ticket=' + ticket
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
        r = requests.post(url, headers=headers, data={'name': dirname})
        data = r.json()
        if str(data['success']) is 'False':
            print('Json : %s' % str(data))
            raise (UATError(ExceptionType.HPCAPI_RET_FALSE, ' unsucesfull'))
        # print('Json : %s' % str(data))
        r.raise_for_status()
        return data

    except requests.exceptions.Timeout as e:

        raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at create_dir [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:

        raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at create_dir [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:

        raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at create_dir [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:

        raise (UATError(ExceptionType.HPCAPI_OTHER, ' at create_dir [ {0} ]'.format(e)))

    except:

        logger_settings.logger.debug('No idea')

        raise (UATError(ExceptionType.HPCAPI, '  at create_dir'))


# HELPERS ======================================================================

# if path = None -> path =/tmp/
def create_random_file_locally(file_name, size_in_kb, path=None):
    # Create a file with random content with a specific size in kb
    try:
        if path:
            file_route = path + '/'
            if os.path.exists(file_route + file_name):
                remove_local_file(file_name + file_name)
        else:
            file_route = '/tmp/'
            if os.path.exists(file_route + file_name):
                remove_local_file(file_name)
        with open(str(file_route + file_name), 'wb') as fout:
            fout.write(os.urandom(size_in_kb))
            logger_settings.logger.info(
                'File {0} with size {1} was created.'.format(file_route + file_name, size_in_kb))
            return file_route, file_name
    except IOError, e:
        logger_settings.logger.debug('Problems creating random content file, reason:{0}'.format(e))
        raise (UATError(ExceptionType.IO_LOCAL, " at create_random_file_content"))


# if path = None -> path =/tmp/
def remove_local_file(file_name, path=None):
    try:
        if path:
            file_route = path + '/'
        else:
            file_route = '/tmp/'
        file_path = file_route + file_name
        if os.path.exists(file_route + file_name):
            os.remove(file_path)
            logger_settings.logger.info('File {0} deleted, great success'.format(file_path))
        else:
            logger_settings.logger.info('File {0} cannot be deleted, does not exist'.format(file_path))
            raise (UATError(ExceptionType.IO_LOCAL, " at remove_file_content: file does not exist"))

    except IOError, e:
        logger_settings.logger.debug('No way to delete the file, reason: {0}'.format(e))
        raise (UATError(ExceptionType.IO_LOCAL, " at remove_file_content"))
