# coding=utf-8

import sys
import os
import stat
import time
import datetime
from os.path import join
import re
import base64

from oslo_config import cfg
from oslo_log import log
from util import hashutil

import threading
import multiprocessing
import sqlite3

LOG = log.getLogger(__name__)

CONF = cfg.CONF

export_file_list_opts = [
    cfg.ListOpt('includes',
                default='',
                help='Include dirs'),
    cfg.ListOpt('excludes',
                default='',
                help='Exclude dirs'),
    cfg.StrOpt('export_sqlite_db',
               default='',
               help='Dest sqlite db file'),
]
CONF.register_opts(export_file_list_opts, group='export_file_list')

rLock = threading.RLock()

conn = None


def getTimestamp():
    time_now = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")
    return time_now


def initSqlite(dbfile):
    if os.path.isfile(dbfile):
        os.rename(dbfile, dbfile + "." + getTimestamp())

    conn = sqlite3.connect(dbfile)
    cursor = conn.cursor()
    # ERROR_STATE
    # 1 folder is not readable
    # 2 file is not exist
    # 3 file is not readable
    # 4 file is not readable
    table_create_sql = 'create table file (ID INTEGER PRIMARY KEY AUTOINCREMENT, FOLDER TEXT, FILE TEXT,'\
                       ' ERROR_STATE INT, CTMP REAL, MTMP REAL, FSIZE INTEGER(8), HASH CHARACTER(32))'
    cursor.execute(table_create_sql)
    cursor.close()
    conn.commit()
    conn.close()


def insert_data(data, conn = None):
    # logger = multiprocessing.log_to_stderr()

    dedicade_conn = conn is None
    if dedicade_conn:
        dbfile = CONF.export_file_list.export_sqlite_db
        conn = sqlite3.connect(dbfile)

    cursor = conn.cursor()
    # cursor.execute('insert into user (id, name) values (\'1\', \'Michael\')')
    table_insert_sql = "insert into file (FOLDER, FILE, ERROR_STATE, CTMP, MTMP, FSIZE, HASH)" \
                       " values ('{FOLDER}', '{FILE}', {ERROR_STATE}, {CTMP}, {MTMP}, {FSIZE}, '{HASH}')"
    if data.__class__.__name__ == "list":
        max_comm = 1024
        rec = 0
        for d in data:
            # print d
            sql = table_insert_sql.format(**d)
            cursor.execute(sql)
            # logger.info(sql)
            rec = rec + 1
            if rec >= max_comm:
                conn.commit()
                rec = 0
            if rec > 0:
                conn.commit()
                rec = 0
    elif data.__class__.__name__ == "dict":
        sql = table_insert_sql.format(**data)
        # logger.info(sql)
        cursor.execute(sql)
    cursor.close()
    conn.commit()

    if dedicade_conn:
        conn.close()


def dirworker(targetFolder):
    def onError(osError):
        dirname = osError.filename
        data = {
            "FOLDER": base64.encodestring(dirname),
            "FILE": '',
            "ERROR_STATE": 1,
            "CTMP": 0,
            "MTMP": 0,
            "FSIZE": 0,
            "HASH": '',
        }
        insert_data(data)

    def get_exclude_files_regex():
        exclude_files = CONF.export_file_list.excludes
        exclude_files.append(os.path.abspath(CONF.export_file_list.export_sqlite_db))
        exclude_files.append(os.path.dirname(os.path.dirname(__file__)))
        return [re.compile(f) for f in exclude_files]

    exclude_files_regex = get_exclude_files_regex()

    def match_excludes(file):
        # exclude_files_regex = get_exclude_files_regex()
        for regex in exclude_files_regex:
            if regex.match(file):
                return True

        return False

    global rLock

    dbfile = CONF.export_file_list.export_sqlite_db
    conn = sqlite3.connect(dbfile)

    for root, dirs, files in os.walk(top=targetFolder, topdown=True, onerror=onError, followlinks=False):
        print "Current root folder: " + root
        file_data = []
        for file_name in files:
            full_file_path = join(root, file_name)
            if match_excludes(full_file_path):
                continue

            ctmp = 0
            mtmp = 0
            fsize = 0
            error_state = 0
            hash = ''
            try:
                file_state = os.stat(full_file_path)
                ctmp = file_state.st_ctime
                mtmp = file_state.st_mtime
                fsize = file_state.st_size
            except:
                err = sys.exc_info()
                LOG.error(str(err))
                print(str(err))
                error_state = 2

            if (file_state.st_mode & stat.S_IFREG == stat.S_IFREG) and \
                    file_state.st_mode & stat.S_IFBLK != stat.S_IFBLK and \
                    file_state.st_mode & stat.S_IFSOCK != stat.S_IFSOCK and \
                    file_state.st_mode & stat.S_IFDIR != stat.S_IFDIR and \
                    file_state.st_mode & stat.S_IFCHR != stat.S_IFCHR and \
                    file_state.st_mode & stat.S_IFIFO != stat.S_IFIFO and \
                    os.access(full_file_path, os.R_OK):
                try:
                    hash = hashutil.md5sum(full_file_path)
                except:
                    err = sys.exc_info()
                    LOG.error(str(err))
                    print(str(err))
                    error_state = 4
            else:
                error_state = 3


            data = {
                "FOLDER": base64.encodestring(root),
                "FILE": base64.encodestring(file_name),
                "ERROR_STATE": error_state,
                "CTMP": ctmp,
                "MTMP": mtmp,
                "FSIZE": fsize,
                "HASH": hash,
            }
            file_data.append(data)
        rLock.acquire()
        insert_data(file_data, conn)
        rLock.release()

        ready_dirs = []
        for dir_name in dirs:
            full_dir_path = join(root, dir_name, os.path.pathsep)
            if not match_excludes(full_dir_path):
                ready_dirs.append(dir_name)
        dirs = ready_dirs

    conn.close()


def run():
    time1 = time.time()
    LOG.info('Started at: ' + getTimestamp())
    print('Started at: ' + getTimestamp())

    include_dirs = CONF.export_file_list.includes

    dbfile = CONF.export_file_list.export_sqlite_db
    initSqlite(dbfile)

    for targetFolder in include_dirs :
        p = multiprocessing.Process(target=dirworker, name="dirworker" + "." + getTimestamp(), args=(targetFolder,))
        p.start()
        p.join()
        # dirworker(targetFolder)

    time2 = time.time()
    LOG.info('Ended at: ' + getTimestamp())
    print('Ended at: ' + getTimestamp())
    LOG.info('Last ' + str(time2 - time1) + ' s')
    print('Last ' + str(time2 - time1) + ' s')
