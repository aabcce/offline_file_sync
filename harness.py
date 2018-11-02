# coding=utf-8

import sys
import os

import multiprocessing

from export_file_list import export_file_list
from compare_file_list import compare_file_list
from backup_file_list import backup_file_list

work_folder = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(work_folder)

from oslo_config import cfg
from oslo_log import log


CONF = cfg.CONF

# LOG = log.getLogger(__name__)
# log.register_options(CONF)

CLI_OPTS = [
    cfg.ListOpt('task',
               default=[],
               help='Task type'),
]
CONF.register_cli_opts(CLI_OPTS)

CONF(default_config_files=[work_folder + "/conf/harness.conf"])

# log.setup(CONF, 'harness')

LOG = multiprocessing.log_to_stderr()


def __help():
    print """
Usage:
harness --task=export
harness --task=compare [Linux Only]
harness --task=backup
"""


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) == 0 :
        print __help()
        exit()
    if argv[0].rfind("harness.py") > -1:
        argv.pop(0)
    if len(argv) == 0 :
        print __help()
        exit()

    if CONF.task[0] == "export":
        try:
            export_file_list.run()
        except:
            err = sys.exc_info()
            LOG.error(str(err))
            print(str(err))
    elif CONF.task[0] == "compare":
        if sys.platform == "win32":
            print "Error: Windows is not well tested."
            exit()
        try:
            compare_file_list.run()
        except:
            err = sys.exc_info()
            LOG.error(str(err))
            print(str(err))
    elif CONF.task[0] == "backup":
        try:
            backup_file_list.run()
        except:
            err = sys.exc_info()
            LOG.error(str(err))
            print(str(err))

    else:
        print __help()
        exit()