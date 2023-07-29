# Project
from zmq import TYPE


PROJECT_CFG = '.projectcfg'
PROJECT_CFG_LEGACY = '_CacheInfo'

PROJECT_TMP = '_Temp'               # Temporary
PROJECT_EXT = '_Extension Package'  # Extension
PROJECT_ARC = '_Event Records'      # Archive

TYPE_STUDY = 'Study'
# TYPE_STUDY = 'Course'
TYPE_PROJECT = 'Project'
TYPE_WORK = 'Work'
TYPE_DAILY = 'Daily'
# TYPE_DAILY = 'Daily Life'
TYPE_RECREATION = 'Recreation'
TYPE_OTHER = 'Other'
PROJECT_TYPE = [TYPE_STUDY, TYPE_PROJECT, TYPE_WORK,
                TYPE_DAILY, TYPE_RECREATION, TYPE_OTHER]  # Legacy Support: No.0-4
