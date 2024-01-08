#!/usr/bin/env python

"""
============
test_time.py
============

Unit tests for the util/time.py module.
"""
import os
import re
import tempfile
import unittest
from datetime import datetime
from os.path import abspath, join

from pkg_resources import resource_filename

from opera.util.time import get_catalog_metadata_datetime_str
from opera.util.time import get_current_iso_time
from opera.util.time import get_iso_time
from opera.util.time import get_time_for_filename


class TimeTestCase(unittest.TestCase):
    """Base test class using unittest"""

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up directories for testing
        Initialize regular expression
        Initialize other class variables

        """
        cls.starting_dir = abspath(os.curdir)
        cls.test_dir = resource_filename(__name__, "")
        cls.data_dir = join(cls.test_dir, os.pardir, "data")

        os.chdir(cls.test_dir)

        cls.config_file = join(cls.data_dir, "test_base_pge_config.yaml")
        cls.iso_regex = r'^(-?(?:[0-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):' \
                        r''r'([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)$'
        cls.match_iso_time = re.compile(cls.iso_regex).match
        cls.reps = 1000

    @classmethod
    def tearDownClass(cls) -> None:
        """
        At completion re-establish starting directory
        -------
        """
        os.chdir(cls.starting_dir)

    def setUp(self) -> None:
        """
        Use the temporary directory as the working directory
        -------
        """
        self.working_dir = tempfile.TemporaryDirectory(
            prefix="test_time_", suffix='temp', dir=os.curdir
        )
        os.chdir(self.working_dir.name)

    def tearDown(self) -> None:
        """
        Return to starting directory
        -------
        """
        os.chdir(self.test_dir)
        self.working_dir.cleanup()

    def test_get_current_iso_time(self):
        """
        These formated results
        ISO format: YYYY-MM-DDTHH:MM:SS.mmmmmmZ
        Verify that the date generated by the function produces a result that matches
        the above pattern

        """
        for index in range(self.reps):
            # Verify returned value
            time = get_current_iso_time()
            self.assertEqual(time, self.match_iso_time(time).group())

        # Test various bad strings
        time_1 = '20211102T15:51:39.95566Z'     # missing '-'
        time_2 = '2021-11-02T155139.955666Z'    # missing ':'
        time_3 = '202-11-02T15:51:39.955666Z'   # wrong # of time digits
        time_4 = '2021-1a-02T15:51:39.955666Z'  # wrong character in month
        time_5 = '2021-11-0215:51:39.955666Z'   # missing 'T'
        time_6 = '2021-11-02T15:5:39.955666Z'   # wrong # of minute digits
        time_7 = '2021-11-02T15:51:3.955666Z'   # wrong # of second digits
        time_8 = '2021-11-02T15:51:39.955666'   # missing 'Z'

        # Assert that none of the above strings match the regex pattern.
        self.assertIsNone(self.match_iso_time(time_1))
        self.assertIsNone(self.match_iso_time(time_2))
        self.assertIsNone(self.match_iso_time(time_3))
        self.assertIsNone(self.match_iso_time(time_4))
        self.assertIsNone(self.match_iso_time(time_5))
        self.assertIsNone(self.match_iso_time(time_6))
        self.assertIsNone(self.match_iso_time(time_7))
        self.assertIsNone(self.match_iso_time(time_8))

    def test_get_iso_time(self):
        """
        Convert datetime to ISO format
        Verify that the result of datetime.datetime.now() is successfully changed to ISO time

        """
        for index in range(self.reps):
            dt = datetime.now()
            time_in_iso = get_iso_time(dt)
            # Verify that the datetime.now() result has been changed to ISO format
            self.assertEqual(time_in_iso, self.match_iso_time(time_in_iso).group())

        dt_str = str(dt)  # cast datetime.now() result to string for regex
        # Verify that the datetime.now() format does not match iso_time
        self.assertIsNone(self.match_iso_time(dt_str))

    def test_get_time_for_filename(self):
        """
        Converts the provided datetime object to a time-tag string suitable for
        use with output filenames.
        Verify the proper number of digits separated by "T" in the string are returned
        """
        # Simple regex to test for YYYYMMDDTHHMMSS format ('Y'ear, 'M'onth, 'D'ay, 'T', 'H'our, 'M'inutes, 'S'econds)
        filename_regex = r'^\d{8}T\d{6}$'

        # Test multiple times
        for index in range(self.reps):
            dt = datetime.now()
            time_for_fname = get_time_for_filename(dt)
            self.assertEqual(time_for_fname, re.match(filename_regex, time_for_fname).group())

        # Sanity check to verify that bad dates will not pass.
        t1 = '202a1103T102328'  # bad year
        t2 = '2021103T102328'   # not enough digits for month or day
        t3 = '20211103102328'   # no 'T'
        t4 = '20211103T1n2328'  # bad hour
        t5 = '20211103T10228'   # bad min
        t6 = '20211103T10232b'  # bad sec

        # Assert that none of the above strings match the regex pattern.
        self.assertIsNone(re.match(filename_regex, t1))
        self.assertIsNone(re.match(filename_regex, t2))
        self.assertIsNone(re.match(filename_regex, t3))
        self.assertIsNone(re.match(filename_regex, t4))
        self.assertIsNone(re.match(filename_regex, t5))
        self.assertIsNone(re.match(filename_regex, t6))

    def test_get_cat_metadata_datetime_str(self):
        """
        Converts the provided datetime object to a time-tag string suitable for use
        in catalog metadata.

        """
        nano_regex = r'^\d{10}Z$'
        # Test multiple times
        for index in range(self.reps):
            dt = datetime.now()
            nano_str = get_catalog_metadata_datetime_str(dt).split('.')[-1]
            self.assertEqual(nano_str, re.match(nano_regex, nano_str).group())

        # Test some bad strings
        t1 = '012345678Z'    # too few digits
        t2 = '01234567899Z'  # too many digits
        t3 = '0123456789'    # no 'Z'

        self.assertIsNone(re.match(nano_regex, t1))
        self.assertIsNone(re.match(nano_regex, t2))
        self.assertIsNone(re.match(nano_regex, t3))


if __name__ == "__main__":
    unittest.main()
