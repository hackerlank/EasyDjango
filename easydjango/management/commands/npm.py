# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import glob
import os
import shutil
import subprocess
from argparse import ArgumentParser

from django.conf import settings
from django.core.management import BaseCommand

from easydjango.utils import ensure_dir

__author__ = 'Matthieu Gallet'


class Command(BaseCommand):
    help = 'Use npm to download all packages that are keys of "settings.NPM_FILE_PATTERNS"'

    # def add_arguments(self, parser):
    #     assert isinstance(parser, ArgumentParser)
    #     parser.add_argument('--favicon', default=None,
    #                         help=('path or URL of to master favicon. '
    #                               'Otherwise use "icons/favicon.ico" from the static files'))

    def handle(self, *args, **options):
        ensure_dir(settings.NPM_ROOT_PATH, False)
        for npm_package, patterns in settings.NPM_FILE_PATTERNS.items():
            subprocess.check_output([settings.NPM_EXECUTABLE_PATH, 'install', npm_package],
                                    cwd=settings.NPM_ROOT_PATH)
            src_package_root = os.path.join(settings.NPM_ROOT_PATH, 'node_modules', npm_package)
            dst_package_root = os.path.join(settings.STATIC_ROOT, settings.NPM_STATIC_FILES_PREFIX, npm_package)
            ensure_dir(dst_package_root)
            for pattern in patterns:
                for src_path in glob.glob(os.path.join(src_package_root, pattern)):
                    dst_path = os.path.join(dst_package_root, os.path.relpath(src_path, src_package_root))
                    ensure_dir(dst_path, parent=True)
                    if os.path.isfile(dst_path):
                        os.remove(dst_path)
                    elif os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    if os.path.isfile(src_path):
                        shutil.copy(src_path, dst_path)
                    else:
                        shutil.copytree(src_path, dst_path)
