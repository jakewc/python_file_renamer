# -*- coding: utf-8 -*-
import os
from unittest import TestCase
from unittest.mock import patch

from renamer_exceptions import (
    AllFilesOrderedException,
    InsufficientPermissionException,
    InvalidDirectoryException,
    NamingCollisionException,
    NoWorkingFilesException
)
from renamer_service import RenameImageFilesService


class TestRenameImageFilesServiceValidation(TestCase):
    def setUp(self):
        self.absolute_path = os.path.dirname(os.path.realpath(__file__))

    def test_invalid_directory(self):
        with self.assertRaises(InvalidDirectoryException):
            RenameImageFilesService(directory='.')

    def test_no_files_for_renaming(self):
        with self.assertRaises(NoWorkingFilesException):
            RenameImageFilesService(
                directory=f'{self.absolute_path}/fixtures'
            )

    def test_working_file_identification(self):
        # When the working file set is identified from the contents of a dir
        renamer = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/ignore_some_files'
        )
        # Then the files which do not match the rename pattern are ignored
        self.assertEqual(6, len(renamer.files_for_renaming))
        self.assertEqual(5, len(renamer.unused_files))
        self.assertCountEqual(
            renamer.files_for_renaming,
            [
                'pref.1.jpg',
                'pref.01.jpg',
                'pref.2.jpg',
                'pref.1.png',
                'pref.01.png',
                'pref.2.png'
            ]
        )
        self.assertCountEqual(
            renamer.unused_files,
            [
                'pref.1.not_an_ext',
                'pref.01.not_an_ext',
                'pref.1x1.jpg',
                'pref.1x1.jpg.temp',
                'doesnt.match.at.all'
            ]
        )

    def test_temp_naming_collision(self):
        """
        Check service raises when renaming a file with a temp suffix
        would cause a conflict.
        """
        with self.assertRaises(NamingCollisionException):
            RenameImageFilesService(
                directory=f'{self.absolute_path}/fixtures/naming_collision'
            )

    @patch('os.access')
    def test_file_access_denied(self, os_access):
        """
        Check service raises when permission to rename a file would be denied.
        """
        os_access.return_value = False
        with self.assertRaises(InsufficientPermissionException):
            RenameImageFilesService(
                directory=f'{self.absolute_path}/fixtures/one_prefix'
            )


class TestRenameImageFilesServiceScheme(TestCase):
    """
    Test the rename mapping rather than the renaming, so that the tests
    do not have to perform IO operations.
    """
    def setUp(self):
        self.absolute_path = os.path.dirname(os.path.realpath(__file__))

    def test_one_file(self):
        # When
        rename_scheme = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/one_file'
        ).get_rename_scheme()
        # Then
        self.assertDictEqual(
            rename_scheme,
            {
                'pref.45.jpg': 'pref.01.jpg',
            }
        )

    def test_one_prefix_one_filetype(self):
        # When
        rename_scheme = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/one_prefix'
        ).get_rename_scheme()
        # Then
        self.assertDictEqual(
            rename_scheme,
            {
                'pref.01.jpg': 'pref.01.jpg',
                'pref.1.jpg': 'pref.02.jpg',
                'pref.2.jpg': 'pref.03.jpg',
                'pref.3.jpg': 'pref.04.jpg',
                'pref.4.jpg': 'pref.05.jpg',
                'pref.5.jpg': 'pref.06.jpg',
                'pref.7.jpg': 'pref.07.jpg',
                'pref.9.jpg': 'pref.08.jpg',
                'pref.10.jpg': 'pref.09.jpg'
            }
        )

    def test_zero_ordered_first(self):
        # When
        rename_scheme = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/zero_first'
        ).get_rename_scheme()
        # Then
        self.assertDictEqual(
            rename_scheme,
            {
                'pref.00.jpg': 'pref.01.jpg',
                'pref.01.jpg': 'pref.02.jpg',
            }
        )

    def test_two_prefixes_one_filetype(self):
        """
        Given two prefixes but only one file type, check they are grouped
        seperately.
        """
        # When
        rename_scheme = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/two_prefixes'
        ).get_rename_scheme()
        # Then
        self.assertDictEqual(
            rename_scheme,
            {
                'p1.1.jpg': 'p1.01.jpg',
                'p1.2.jpg': 'p1.02.jpg',
                'p2.1.jpg': 'p2.01.jpg',
                'p2.2.jpg': 'p2.02.jpg',
            }
        )

    def test_prefix_case_sensitivity(self):
        """
        Given two prefixes which are only different on case, check they are
        grouped seperately.
        """
        # When
        rename_scheme = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/same_prefix_different_case'
        ).get_rename_scheme()
        # Then
        self.assertDictEqual(
            rename_scheme,
            {
                'prefix.1.jpg': 'prefix.01.jpg',
                'prefix.2.jpg': 'prefix.02.jpg',
                'Prefix.1.jpg': 'Prefix.01.jpg',
                'Prefix.2.jpg': 'Prefix.02.jpg',
            }
        )

    def test_extension_case_insensitivity(self):
        """
        Given two extensions which are only different on case, check they are
        grouped together.
        """
        # When
        rename_scheme = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/same_suffix_different_case'
        ).get_rename_scheme()
        # Then
        self.assertDictEqual(
            rename_scheme,
            {
                'prefix.1.jpg': 'prefix.01.jpg',
                'prefix.2.jpg': 'prefix.02.jpg',
                'prefix.4.JPG': 'prefix.03.JPG',
            }
        )

    def test_two_extensions(self):
        """
        Given one prefix but two file types, check they are grouped seperately.
        """
        # When
        rename_scheme = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/two_extensions'
        ).get_rename_scheme()
        # Then
        self.assertDictEqual(
            rename_scheme,
            {
                'pref.1.jpg': 'pref.01.jpg',
                'pref.2.jpg': 'pref.02.jpg',
                'pref.1.png': 'pref.01.png',
                'pref.2.png': 'pref.02.png',
            }
        )

    def test_already_ordered(self):
        """
        Given a folder with perfectly ordered files, test they will not
        be renamed at all.
        """
        with self.assertRaises(AllFilesOrderedException):
            RenameImageFilesService(
                directory=f'{self.absolute_path}/fixtures/already_ordered'
            ).get_rename_scheme()

    def test_only_one_extension_needs_ordering(self):
        """
        Given a folder with two sets of rename-able files, one of which
        is already perfectly ordered, check only the imperfect ones
        will be renamed.
        """
        # When
        rename_scheme = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/two_exts_one_needs_ordering'
        ).get_rename_scheme()
        # Then
        self.assertDictEqual(
            rename_scheme,
            {
                'pref.1.jpg': 'pref.01.jpg',
                'pref.2.jpg': 'pref.02.jpg',
            }
        )

    def test_ignoring_files(self):
        """
        Given a dir with some files that don't match the rename pattern,
        check they are ignored.
        """
        # When
        rename_scheme = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/ignore_some_files'
        ).get_rename_scheme()
        # Then
        self.assertDictEqual(
            rename_scheme,
            {
                'pref.01.jpg': 'pref.01.jpg',
                'pref.1.jpg': 'pref.02.jpg',
                'pref.2.jpg': 'pref.03.jpg',
                'pref.01.png': 'pref.01.png',
                'pref.1.png': 'pref.02.png',
                'pref.2.png': 'pref.03.png',
            }
        )

    def test_leading_zeroes(self):
        """
        Test files with more leading zeroes come first in the rename order.
        """
        # When
        rename_scheme = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/leading_zeroes'
        ).get_rename_scheme()
        # Then
        self.assertDictEqual(
            rename_scheme,
            {
                'pref.00001.jpg': 'pref.01.jpg',
                'pref.01.jpg': 'pref.02.jpg',
                'pref.1.jpg': 'pref.03.jpg',
            }
        )

    def test_combined_case(self):
        """
        Test combining the previous situations in one directory
        still performs as expected.
        """
        # When
        rename_scheme = RenameImageFilesService(
            directory=f'{self.absolute_path}/fixtures/combined_case'
        ).get_rename_scheme()
        # When
        self.assertDictEqual(
            rename_scheme,
            {
                'order_this.001.png': 'order_this.01.png',
                'order_this.1.png': 'order_this.02.png',
                'order_this.3.png': 'order_this.03.png',
                'Order_this.2.tiff': 'Order_this.01.tiff',
                'Order_this.3.tiff': 'Order_this.02.tiff',
                'order_by_itself.3.jpeg': 'order_by_itself.01.jpeg',
            }
        )
