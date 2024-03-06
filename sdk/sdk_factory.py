


from sdk.sdk_base_ssh import HPCSDK_SSH


# TODO prepare a real factory
def SDK_FACTORY(backend, remotehost, user, passwd, port, debug=None):
    if backend == 'SSH':
        return HPCSDK_SSH(remotehost,  user, passwd, port, debug)
    elif backend == 'HPCAPI':
        return HPCSDK(remotehost,  user, passwd, port)
    else:
        raise Exception("bad choice at choosing backend implementation")


