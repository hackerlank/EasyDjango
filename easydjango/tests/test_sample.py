# -*- coding: utf-8 -*-
"""
Sample test module corresponding to the :mod:`easydjango.sample` module.

A complete documentation can be found at :mod:`unittest`.

"""from __future__ import unicode_literals


import unittest
from easydjango.sample import sample_function

__author__ = 'Matthieu Gallet'

__all__ = ['SampleTest']


class SampleTest(unittest.TestCase):
    """Base test cases for the sample function provided in
    :func:`easydjango.sample.sample_function`."""
    # pylint: disable=R0904

    def test_1(self):
        """Test the sample_function with two arguments."""
        self.assertEqual(sample_function(4, 4), 8)

    def test_2(self):
        """Test the sample_function with a single argument."""
        self.assertEqual(sample_function(4), 8)




if __name__ == '__main__':
    unittest.main()
