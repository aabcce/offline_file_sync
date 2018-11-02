# coding=utf-8

import sys
import os
import sqlite3
import base64
import time
import datetime
import shutil
from zipfile import ZipFile

from oslo_config import cfg
from oslo_log import log

LOG = log.getLogger(__name__)

CONF = cfg.CONF

backup_file_list_opts = [
    cfg.StrOpt('incremental_sqlite_file',
               default='',
               help=''),
    cfg.BoolOpt('zip_file',
               default=False,
               help=''),
    cfg.StrOpt('backup_target',
               default='',
               help=''),
]
CONF.register_opts(backup_file_list_opts, group='backup_file_list')


def getTimestamp():
    time_now = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")
    return time_now


def conn_sqlite(sqlite_file):
    conn = sqlite3.connect(sqlite_file)

    return conn


def run():
    time1 = time.time()
    LOG.info('Started at: ' + getTimestamp())
    print('Started at: ' + getTimestamp())

    incremental_sqlite_file = CONF.backup_file_list.incremental_sqlite_file
    zip_file = CONF.backup_file_list.zip_file
    backup_target = CONF.backup_file_list.backup_target

    if zip_file:
        if os.path.exists(backup_target) and os.path.isfile(backup_target):
            os.rename(backup_target, backup_target + "." + getTimestamp())
    else:
        if os.path.exists(backup_target) and os.path.isdir(backup_target):
            try:
                shutil.rmtree(backup_target)
            except:
                err = sys.exc_info()
                LOG.error(err[1].message)
                print(err[1].message)
        if not os.path.isdir(backup_target):
            os.makedirs(backup_target)

    if not incremental_sqlite_file or not os.path.isfile(incremental_sqlite_file) or not os.access(incremental_sqlite_file, os.R_OK):
        LOG.error("File %s is not exists." %(incremental_sqlite_file))
        print("File %s is not exists." %(incremental_sqlite_file))
    conn = conn_sqlite(incremental_sqlite_file)

    cursor = conn.cursor()
    sql = "select * from file"
    cursor.execute(sql)
    for item in cursor:
        error_state = item[3]
        hash = item[7]

        if int(error_state) != 0 or not hash:
            continue

        folder = base64.decodestring(item[1])
        file = base64.decodestring(item[2])

        full_file_path = os.path.join(folder, file)

        if not os.path.isfile(full_file_path):
            continue

        if zip_file:
            with ZipFile(backup_target, "a", allowZip64 = True) as newzip:
                newzip.write(full_file_path)
        else:
            backup_folder = backup_target + os.path.sep + folder
            backup_folder = backup_folder.replace(":\\", "_Driver\\")

            if not os.path.isdir(backup_folder):
                os.makedirs(backup_folder)
            shutil.copy(full_file_path, backup_folder)

    cursor.close()
    conn.close()

    time2 = time.time()
    LOG.info('Ended at: ' + getTimestamp())
    print('Ended at: ' + getTimestamp())
    LOG.info('Last ' + str(time2 - time1) + ' s')
    print('Last ' + str(time2 - time1) + ' s')
