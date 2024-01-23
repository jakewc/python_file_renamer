# -*- coding: utf-8 -*-
import os
import re
from collections import defaultdict

from image_extensions import IMAGE_EXTENSIONS_LOWERCASED
from renamer_exceptions import (
    AllFilesOrderedException,
    InsufficientPermissionException,
    InvalidDirectoryException,
    NamingCollisionException,
    NoWorkingFilesException
)


class RenameImageFilesService:

    TEMP_SUFFIX = '.temp'

    def __init__(self, directory):
        """
        Perform necessary pre-processing to ensure rename will succeed.
        """
        self.files_for_renaming = []
        self.unused_files = set()
        self.directory = directory
        self.validate_directory()
        self.set_files_for_renaming()
        self.check_for_naming_collisions_with_temp_suffix()
        self.check_for_file_access_permissions()

    def validate_directory(self):
        if (
            not os.path.isabs(self.directory)
            or not os.path.isdir(self.directory)
        ):
            raise InvalidDirectoryException(
                'This is not a valid directory. '
                'This utility must be passed an absolute, existing directory.'
            )

    def set_files_for_renaming(self):
        all_filenames_in_dir = [file for file in os.listdir(self.directory)]

        # Filenames need to match:
        # '<at least one char>.<any number>.<an image extension>'
        extensions_pattern = '|'.join(IMAGE_EXTENSIONS_LOWERCASED)
        valid_file_patterns = (
            re.compile(r'^.+\.[0-9]+\.(?:{})$'.format(extensions_pattern))
        )
        self.files_for_renaming = [
            filename for filename in all_filenames_in_dir
            if re.match(valid_file_patterns, filename.lower())
        ]
        if not self.files_for_renaming:
            raise NoWorkingFilesException(
                'No relevant files found in this directory'
            )
        self.unused_files = (
            set(all_filenames_in_dir) - set(self.files_for_renaming)
        )

    def check_for_naming_collisions_with_temp_suffix(self):
        for filename in self.files_for_renaming:
            for other_file_in_dir in self.unused_files:
                if (
                    other_file_in_dir
                    == f'{filename}{self.TEMP_SUFFIX}'
                ):
                    raise NamingCollisionException(
                        f'This directory contains a conflicting file. '
                        f'Please move {other_file_in_dir} out of this dir.'
                    )

    def check_for_file_access_permissions(self):
        for filename in self.files_for_renaming:
            if not os.access(os.path.join(self.directory, filename), os.W_OK):
                raise InsufficientPermissionException(
                    'Insufficient write permissions '
                    'to rename files in this dir.'
                )

    def rename(self):
        rename_scheme = self.get_rename_scheme()
        for old_filename, new_filename in rename_scheme.items():
            os.rename(
                os.path.join(self.directory, old_filename),
                os.path.join(self.directory, f'{new_filename}{self.TEMP_SUFFIX}')
            )
        for new_filename in rename_scheme.values():
            os.rename(
                os.path.join(self.directory, f'{new_filename}{self.TEMP_SUFFIX}'),
                os.path.join(self.directory, new_filename)
            )
        print(
            f'Successfully renamed {len(rename_scheme.keys())} '
            f'files in this directory'
        )

    def get_rename_scheme(self):
        ordered_files = self.order_files_for_renaming()
        files_to_rename = self.drop_already_ordered_files_from_working_set(
            ordered_files
        )
        return self.get_rename_scheme_from_ordered_files(files_to_rename)

    def order_files_for_renaming(self):
        """
        Returns list of lists, each containing a group of original filenames
        in ascending order.
        [[prefix_1.1.jpg, prefix_1.3.jpg], [prefix_2.1.jpg], ...]
        """
        filename_mapping_by_prefix_and_type = defaultdict(list)
        for filename in self.files_for_renaming:
            filename_parts = filename.split('.')
            filename_mapping_by_prefix_and_type[
                f'{filename_parts[0]} - {filename_parts[2].lower()}'
            ].append(filename)

        sorted_filename_groups = []
        for file_group in filename_mapping_by_prefix_and_type.values():
            # Sort by filenum, then alphabetically, to give
            # consistent ordering to cases where e.g. 'x.01.jpg' and 'x.1.jpg'
            # are both up for renaming (the one with more leading zeroes
            # will come first).
            sorted_filename_groups.append(list(
                sorted(file_group, key=lambda filename: (
                    int(filename.split('.')[1]), filename
                ))
            ))

        return sorted_filename_groups

    def drop_already_ordered_files_from_working_set(
        self, sorted_filename_groups
    ):
        """
        After ordering files matching the rename pattern, we can figure out
        which ones are perfectly ordered already and avoid running
        any rename operations on them.
        This adds complexity, but would rather do fewer IO operations
        than fewer loops over string arrays, within reason.
        """
        needs_renaming = []
        for filename_group in sorted_filename_groups:
            for i in range(len(filename_group)):
                # If any file in the group does not already follow the
                # intended rename pattern, that group needs renaming. This
                # includes checking for the leading zero.
                if (
                    filename_group[i].split('.')[1] != f'0{i + 1}'
                ):
                    needs_renaming.append(filename_group)
                    break
        if not needs_renaming:
            raise AllFilesOrderedException()

        return needs_renaming

    def get_rename_scheme_from_ordered_files(self, ordered_files):
        """
        args:
        - ordered_files: list of lists, each list containing a group of
          original filenames in ascending order.

        Returns a dict, mapping old names to new ones:
        {'old_name': 'new_name', ...}
        """
        rename_scheme = defaultdict(str)
        for file_group in ordered_files:
            for old_filename in file_group:
                filename_parts = old_filename.split('.')
                # No two filenames can be EXACTLY identical
                # (can only be as close as e.g x.1.jpg, x.01.jpg),
                # so building new name using index is safe
                file_index = file_group.index(old_filename)
                new_name = (
                    f'{filename_parts[0]}.0{file_index + 1}'
                    f'.{filename_parts[2]}'
                )
                rename_scheme[old_filename] = new_name

        print(
            f'Found {len(rename_scheme.keys())} files to rename, '
            f'in {len(ordered_files)} prefix groups')
        return rename_scheme
