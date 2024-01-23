# -*- coding: utf-8 -*-
import getopt
import sys

from renamer_exceptions import (
    AllFilesOrderedException,
    NoWorkingFilesException
)
from renamer_service import RenameImageFilesService


def main(argv):
    failure_string = (
        'Invalid arguments or options. Use `python renamer_run.py -h` for help.'
    )
    help_string = (
        f"""
        Usage: `python renamer_run.py <absolute_directory_to_work_on>`\n
        This script accepts one, and only one, absolute directory path.\n
        It will rename all files which exactly match the filename pattern:
        '[one or more characters].[any positive integer].[an image file extension]'\n
        There must not be other files in the given directory which match the pattern:
        '[filename which matches first pattern]{RenameImageFilesService.TEMP_SUFFIX}'\n
        The user must have write permissions for all working files.\n
        To run tests, run `python -m unittest renamer_tests -b`.
        """
    )
    if len(argv) != 1:
        print(failure_string)
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv, '-h')
    except getopt.GetoptError:
        print(failure_string)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_string)
            sys.exit(2)

    try:
        RenameImageFilesService(argv[0]).rename()
    # Not really 'invalid' uses of the util, so these cases just exit
    # instead of raising
    except NoWorkingFilesException:
        print('No files matching rename pattern found in this directory')
    except AllFilesOrderedException:
        print('All files matching the rename pattern are already ordered')

    sys.exit(2)


if __name__ == '__main__':
    main(sys.argv[1:])
