# coding=utf-8

import os
import sqlite3
import base64
import time
import datetime

from oslo_config import cfg
from oslo_log import log

CONF = cfg.CONF

LOG = log.getLogger(__name__)
log.register_options(CONF)

compare_file_list_opts = [
    cfg.StrOpt('src_sqlite_file',
               default='',
               help=''),
    cfg.StrOpt('dest_sqlite_file',
               default='',
               help=''),
    cfg.StrOpt('result_sqlite_file',
               default='',
               help=''),
    cfg.IntOpt('max_compare_group_size',
               default=1000,
               help=''),
]
CONF.register_opts(compare_file_list_opts, group='compare_file_list')


def getTimestamp():
    time_now = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")
    return time_now


def conn_sqlite(sqlite_file):
    conn = sqlite3.connect(sqlite_file)

    return conn


def init_dest_sqlite_file(conn):
    cursor = conn.cursor()

    table_drop_sql = 'drop table if exists file_src'
    cursor.execute(table_drop_sql)
    table_create_sql = 'create table file_src (ID INTEGER, FOLDER TEXT, FILE TEXT,' \
                       ' ERROR_STATE INT, CTMP REAL, MTMP REAL, FSIZE INTEGER(8), HASH CHARACTER(32))'
    cursor.execute(table_create_sql)
    
    cursor.close()
    conn.commit()


def init_result_sqlite_file(conn):
    cursor = conn.cursor()
    
    table_create_sql = 'create table file (ID INTEGER PRIMARY KEY AUTOINCREMENT, FOLDER TEXT, FILE TEXT,' \
                       ' ERROR_STATE INT, CTMP REAL, MTMP REAL, FSIZE INTEGER(8), HASH CHARACTER(32))'
    cursor.execute(table_create_sql)
    
    cursor.close()
    conn.commit()


def insert_data(data, conn, table="file", id_incremental=True):

    # logger = multiprocessing.log_to_stderr()

    cursor = conn.cursor()
    # cursor.execute('insert into user (id, name) values (\'1\', \'Michael\')')
    if id_incremental:
        table_insert_sql = "insert into %s (FOLDER, FILE, ERROR_STATE, CTMP, MTMP, FSIZE, HASH)" \
                           " values ('{FOLDER}', '{FILE}', {ERROR_STATE}, {CTMP}, {MTMP}, {FSIZE}, '{HASH}')" %(table)
    else:
        table_insert_sql = "insert into %s (ID, FOLDER, FILE, ERROR_STATE, CTMP, MTMP, FSIZE, HASH)" \
                           " values ({ID}, '{FOLDER}', '{FILE}', {ERROR_STATE}, {CTMP}, {MTMP}, {FSIZE}, '{HASH}')" %(table)

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


def process_src_data(file_data_src, conn_dest, conn_result):
    insert_data(file_data_src, conn_dest, "file_src", False)

    cursor_dest = conn_dest.cursor()
    sql_dest = "select file_src.*,file.ID as DEST_ID from file_src left outer join file"\
               " on file_src.HASH=file.HASH and file_src.FOLDER=file.FOLDER and file_src.FILE=file.FILE"
    cursor_dest.execute(sql_dest)

    file_data = []
    for item_dest in cursor_dest:
        if item_dest[8]:
            continue
        data = {
            "FOLDER": item_dest[1],
            "FILE": item_dest[2],
            "ERROR_STATE": item_dest[3],
            "CTMP": item_dest[4],
            "MTMP": item_dest[5],
            "FSIZE": item_dest[6],
            "HASH": item_dest[7],
        }
        file_data.append(data)

    sql_dest = "delete from file_src"
    cursor_dest.execute(sql_dest)
    cursor_dest.close()

    if len(file_data) > 0:
        insert_data(file_data, conn_result, "file", True)


def run():
    time1 = time.time()
    LOG.info('Started at: ' + getTimestamp())
    print('Started at: ' + getTimestamp())

    log.setup(CONF, 'harness')

    src_sqlite_file = CONF.compare_file_list.src_sqlite_file
    dest_sqlite_file = CONF.compare_file_list.dest_sqlite_file
    result_sqlite_file = CONF.compare_file_list.result_sqlite_file

    if not src_sqlite_file or not os.path.isfile(src_sqlite_file) or not os.access(src_sqlite_file, os.R_OK):
        LOG.error("File %s is not exists." %(src_sqlite_file))
        print("File %s is not exists." %(src_sqlite_file))
    if not dest_sqlite_file or not os.path.isfile(dest_sqlite_file) or not os.access(dest_sqlite_file, os.R_OK):
        LOG.error("File %s is not exists." %(dest_sqlite_file))
        print("File %s is not exists." %(dest_sqlite_file))
    if os.path.isfile(result_sqlite_file):
        os.rename(result_sqlite_file, result_sqlite_file + "." + getTimestamp())

    conn_src = conn_sqlite(src_sqlite_file)
    conn_dest = conn_sqlite(dest_sqlite_file)
    conn_result = conn_sqlite(result_sqlite_file)

    init_dest_sqlite_file(conn_dest)
    init_result_sqlite_file(conn_result)

    max_cmpare_group_size = CONF.compare_file_list.max_compare_group_size
    cursor_src = conn_src.cursor()

    sql_src = "select * from file"
    cursor_src.execute(sql_src)
    file_count = 0
    file_data = []
    for item_src in cursor_src:
        error_state = item_src[3]
        hash = item_src[7]

        if int(error_state) != 0 or not hash:
            continue

        data = {
            "ID": item_src[0],
            "FOLDER": item_src[1],
            "FILE": item_src[2],
            "ERROR_STATE": error_state,
            "CTMP": item_src[4],
            "MTMP": item_src[5],
            "FSIZE": item_src[6],
            "HASH": hash,
        }
        file_data.append(data)

        if len(file_data) >= max_cmpare_group_size:
            process_src_data(file_data, conn_dest, conn_result)
            file_count = file_count + len(file_data)
            print "%s items are done." %(file_count)
            file_data = []

    process_src_data(file_data, conn_dest, conn_result)
    file_count = file_count + len(file_data)
    print "%s items are done." %(file_count)

    cursor_src.close()
    conn_src.close()
    conn_dest.close()
    conn_result.close()

    time2 = time.time()
    LOG.info('Ended at: ' + getTimestamp())
    print('Ended at: ' + getTimestamp())
    LOG.info('Last ' + str(time2 - time1) + ' s')
    print('Last ' + str(time2 - time1) + ' s')
