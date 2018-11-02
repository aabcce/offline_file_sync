Offline file sync
=================


About
------

Offline file sync is a tool for offline migration in P2V and V2V environment.

After P2V and V2V, VM(Windows or Linux) may differnent in * FILE * level. 
It's important to sync the incremental files.
It works in the following sequense:

- Export file list of certail folders in src and dest VM.
- Compare the file structure of the exported.
- Screen and filter the incremental list.
- Backup file from src.
- Restore file to dest.

Offline file sync provides tools to :

- Export file list
- Compare file structure
- Screen and filter file list
- Backup file list in zip or folder

Installation
-------------

# Windows: 
Copy offline_file_sync, envwindow.zip to targeted VM

Support tools: Export Backup

Usage：
1. Upzip envwindow.zip to current folder
2. Update offline_file_sync/conf/harness.conf, copied form harness.conf.windows
2. Run export.bat or backup.bat

Tested againt：
Windows Server 2008 R2 x64 / Windows Server 2003 R2 x86

# Linux:
Copy offline_file_sync, envlinux.tar.gz to targeted VM

Support tools: Export Backup

Usage：
1. Update offline_file_sync/conf/harness.conf, copied form harness.conf.linux
2. export.sh or backup.sh

Tested againt：
Centos 6,7 / Ubuntu 17


# Compare & Screen:
Runs on Linux *ONLY*.

1. Run before_setup.sh
2. Compare
    1. Update offline_file_sync/conf/harness.conf, copied form harness.conf.linux
    2. Run compare.sh
3. Screen
    1. Update offline_file_sync/conf/harness.conf, copied form harness.conf.linux
    2. Copy incremental file list to offline_file_sync/web/harness/db.sqlite3
    2. Run run_web_server.sh
    3. Open browser to visit http://127.0.0.1:8000


# resource
envwindow.zip packaged from WinPython-32bit
envlinux.zip packaged from anaoconda