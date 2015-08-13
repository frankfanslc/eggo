# Licensed to Big Data Genomics (BDG) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The BDG licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import random
import string
from os.path import join as pjoin
from uuid import uuid4
from shutil import rmtree
from hashlib import md5
from tempfile import mkdtemp
from datetime import datetime
from subprocess import check_call
from contextlib import contextmanager


def uuid():
    return uuid4().hex


def random_id(prefix='tmp_eggo', n=4):
    dt_string = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    rand_string = ''.join(random.sample(string.ascii_uppercase, n))
    return '{pre}_{dt}_{rand}'.format(pre=prefix.rstrip('_', 1), dt=dt_string,
                                      rand=rand_string)


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def sanitize(dirty):
    # for sanitizing URIs/filenames
    # inspired by datacache
    clean = re.sub(r'/|\\|;|:|\?|=', '_', dirty)
    if len(clean) > 150:
        prefix = md5(dirty).hexdigest()
        clean = prefix + clean[-114:]
    return clean


def uri_to_sanitized_filename(source_uri, decompress=False):
    # inspired by datacache
    digest = md5(source_uri.encode('utf-8')).hexdigest()
    filename = '{digest}.{sanitized_uri}'.format(
        digest=digest, sanitized_uri=sanitize(source_uri))
    if decompress:
        (base, ext) = os.path.splitext(filename)
        if ext == '.gz':
            filename = base
    return filename


@contextmanager
def make_local_tmp(prefix='tmp_eggo_', dir=None):
    tmpdir = mkdtemp(prefix=prefix, dir=dir)
    try:
        yield tmpdir
    finally:
        rmtree(tmpdir)


@contextmanager
def make_hdfs_tmp(prefix='tmp_eggo', dir='/tmp', permissions='755'):
    tmpdir = pjoin(dir, '_'.join([prefix, uuid()]))
    check_call('hadoop fs -mkdir {0}'.format(tmpdir).split())
    if permissions != '755':
        check_call(
            'hadoop fs -chmod -R {0} {1}'.format(permissions, tmpdir).split())
    try:
        yield tmpdir
    finally:
        check_call('hadoop fs -rm -r {0}'.format(tmpdir).split())
