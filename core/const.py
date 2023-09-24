# Project
PROJECT_CFG = '.projectcfg'
PROJECT_CFG_LEGACY = '_CacheInfo'

PROJECT_TMP = '_Temp'               # Temporary
PROJECT_EXT = '_Extension Package'  # Extension
PROJECT_ARC = '_Event Records'      # Archive

TYPE_OTHER = -1

TYPE_STUDY = 0
TYPE_PROJECT = 1
TYPE_WORK = 2
TYPE_DAILY = 3
TYPE_RECREATION = 4

PROJECT_TYPE = [TYPE_STUDY, TYPE_PROJECT, TYPE_WORK,
                TYPE_DAILY, TYPE_RECREATION, TYPE_OTHER]  # Legacy Support: No.0-4

# Project Type String (Used as directory name when backup)
PROJECT_TYPESTR = ['Course', 'Project', 'Work',
                   'Daily Life', 'Recreation', 'Other']  # TYPE_OTHER(-1): 'Other'
# SFTR Directory Name of each project type
SFTR_PROJECT_DIR = ['1 Course', '2 Project', '3 Work',
                    '4 Daily Life', '5 Recreation']

TRAVERSE_DEPTH = 3  # Depth of traversing when getting last modified time

# ProjectMgr
BACKUP_THRESHOLD = 15  # Days the modified time ahead of the backup time