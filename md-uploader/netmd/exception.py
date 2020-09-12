class NetMDException(Exception):
    """
      Base exception for all NetMD exceptions.
    """
    pass


class NetMDNotImplemented(NetMDException):
    """
      NetMD protocol "operation not implemented" exception.
    """
    pass


class NetMDRejected(NetMDException):
    """
      NetMD protocol "operation rejected" exception.
    """
    pass
