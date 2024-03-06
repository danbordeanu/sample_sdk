import os
import logger_settings


def write_file(fname_without_extension, file_type, data, path=None):
    # type: (object, object, object) -> object
    '''
    This function will create files if it doesn't already exists or if the file is already on disk it will append data
    :param fname_without_extension:
    :param file_type:
    :param data:
    :param path
    :return:
    '''

    file_name = fname_without_extension + '.' + file_type
    # File exists check
    if os.path.exists(file_name):
        # append data into file
        try:
            fh = file(file_name, 'a+')
            fh.write('\n')
            fh.write(data)
            fh.close()
            logger_settings.logger.info('Apending to file {0} a great success'.format(file_name))
        except IOError, e:
            logger_settings.logger.debug('Problems appending the file, reason: {0}'.format(e))

    else:
        try:
            if path:
                file_to_be_created = path + '/' + file_name
            else:
                file_to_be_created = file_name

            if not os.path.exists(path):
                logger_settings.logger.info('path:{0} is not on disk, we will create it for you'.format(path))
                try:
                    os.makedirs(path)
                except IOError as e:
                    logger_settings.logger.debug('Problems creating the path, reason:{0}'.format(e))

            # write data into file
            fh = file(file_to_be_created, 'w')
            fh.write(data)
            fh.close()
            logger_settings.logger.info('File {0} created'.format(file_name))
            return file_name
        except IOError, e:
            logger_settings.logger.debug('Problems creating a new file, reason:{0}'.format(e))


def delete_files_from_folder(path):
    '''
    This function is used to delete artifacts
    It accept the param path that is the dir from where files will be removed, EX: html
    :param path:
    :return:
    '''
    try:
        map(os.unlink, (os.path.join(path, f) for f in os.listdir(path)))
    except OSError as e:
        logger_settings.logger.debug('Issues deleting the files from logs and html dir {0}'.format(e))
