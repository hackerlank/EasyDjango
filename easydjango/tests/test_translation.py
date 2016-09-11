# -*- coding: utf-8 -*-
"""Sample test module corresponding to the :mod:`{{ module_name }}.translation` module.

A complete documentation can be found at :mod:`unittest`.
"""from __future__ import unicode_literals
import sys
import unittest
from easydjango.translation import translation
__author__ = 'Matthieu Gallet'
__all__ = ['TranslationTest']


class TranslationTest(unittest.TestCase):
    """Base test cases for the sample function provided in
    :func:`easydjango.sample.sample_function`."""
    # pylint: disable=R0904

    def test_translation(self):
        """Test the sample_function with two arguments."""
        __trans = translation('easydjango', languages=['xx_XX'], fallback=True)
        _ = __trans.gettext
        test_str = '[ƒ——!test_string!—–]'
        if sys.version_info[0] == 2:
            _ = __trans.ugettext
            test_str = test_str.decode('utf-8')
        self.assertEqual(_('test_string'), test_str)

if __name__ == '__main__':
    unittest.main()



if __name__ == '__main__':
    import doctest
    doctest.testmod()
