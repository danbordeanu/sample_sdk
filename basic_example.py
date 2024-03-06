

from sdk.sdk_base import HPCSDK

if __name__ == '__main__':

    try:
        URL = 'https://host/api/v2'
        USER = 'username'
        PASSWORD = 'user_encoded_passw='

        # Opening a new session into the cluster
        sdk = HPCSDK(URL, USER, PASSWORD)
 
    except Exception as e:
        logger_settings.logger.info('Error: {0}' .format(e))
