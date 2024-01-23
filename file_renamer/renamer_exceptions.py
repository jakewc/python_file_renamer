# -*- coding: utf-8 -*-


class AllFilesOrderedException(Exception):
    pass


class InsufficientPermissionException(Exception):
    pass


class InvalidDirectoryException(Exception):
    pass


class NamingCollisionException(Exception):
    pass


class NoWorkingFilesException(Exception):
    pass
