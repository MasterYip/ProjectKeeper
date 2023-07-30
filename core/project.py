from math import e
import os
import shutil
import tempfile
import json
import zipfile
import re
import time
import struct
from datetime import datetime
from glob import glob
from .const import *
from .utils import getFileSha256, getDateStr, zipFolder, traverseFolder


def isProject(path: str):
    return os.path.isdir(path) and\
            (os.path.isfile(os.path.join(path, PROJECT_CFG)) or\
             os.path.isfile(os.path.join(path, PROJECT_CFG_LEGACY)))


class Project(dict):

    def __init__(self, prjPath: str, create=False, initType=TYPE_OTHER):
        """
        Load a project from a path.
        :param prjPath: The path of the project.
        :param create: If the project does not exist, create it when creat=True. If false, raise an exception.
        TODO: Subproject?
        """
        # Config
        self.meta = {}
        self.extFiles = []
        self.arcFiles = []

        # Path (Won't be saved in config)
        self.path = prjPath
        self.cfgPath = os.path.join(self.path, PROJECT_CFG)
        self.cfgPathLegacy = os.path.join(self.path, PROJECT_CFG_LEGACY)
        self.tmpPath = os.path.join(self.path, PROJECT_TMP)
        self.extPath = os.path.join(self.path, PROJECT_EXT)
        self.arcPath = os.path.join(self.path, PROJECT_ARC)

        if os.path.isdir(self.path) and os.path.isfile(self.cfgPath):
            self._load()
        elif os.path.isdir(self.path) and os.path.isfile(self.cfgPathLegacy):
            self._loadLegacy()
        elif create:
            os.makedirs(self.path, exist_ok=True)
            os.makedirs(self.tmpPath, exist_ok=True)
            os.makedirs(self.extPath, exist_ok=True)
            os.makedirs(self.arcPath, exist_ok=True)

            self.meta['name'] = os.path.basename(prjPath)
            self.meta['createTime'] = time.time()
            self.meta['backupTime'] = time.time()
            self.meta['writeTime'] = time.time()
            self.meta['version'] = 0
            self.meta['type'] = initType
        else:
            raise FileNotFoundError('Not a project.')
        self._update()
        # self.subprojects = []

    def _load(self):
        data = json.load(open(self.cfgPath, 'r', encoding='utf-8'), encoding='utf-8')
        self.meta = data.get('meta', {})
        self.extFiles = data.get('extFiles', [])
        self.arcFiles = data.get('arcFiles', [])

    def _loadLegacy(self):
        """Load project from legacy config file.(Not fully supported)"""
        with open(self.cfgPathLegacy, 'rb') as file:
            data = file.read()
        struct_format = '60sqqqqii'  # format string
        project_data = struct.unpack(struct_format, data[0:104])
        self.meta['name'] = project_data[0].decode('gbk').rstrip('\x00')
        self.meta['createTime'] = project_data[1]
        self.meta['backupTime'] = project_data[2]
        self.meta['writeTime'] = project_data[3]
        # self.meta['backupMark'] = project_data[4] # Not used
        self.meta['version'] = project_data[5]
        self.meta['type'] = PROJECT_TYPE[project_data[6]] if project_data[6]<len(PROJECT_TYPE) else TYPE_OTHER
        # self.meta['type'] = project_data[6]
        self._save()
                
    def _getLastModifiedTime(self, depth=TRAVERSE_DEPTH):
        ltime = 0
        for file in traverseFolder(self.path, depth=depth, file_only=True):
            if os.path.getmtime(file) > ltime:
                ltime = os.path.getmtime(file)
        return ltime

    def _getRelativePath(self, path):
        return os.path.relpath(path, self.path)

    def _getLastModifiedDateTime(self):
        return datetime.fromtimestamp(self._getLastModifiedTime())

    def _save(self):
        """Save project config file."""
        # Aux Info
        # self.meta['name'] = os.path.basename(self.path)
        self.meta['createDate'] = getDateStr(self.meta['createTime'])
        self.meta['backupDate'] = getDateStr(self.meta['backupTime'])
        self.meta['writeDate'] = getDateStr(self.meta['writeTime'])
        
        self['meta'] = self.meta
        self['extFiles'] = self.extFiles
        self['arcFiles'] = self.arcFiles
        json.dump(self, open(os.path.join(self.path, PROJECT_CFG), 'w', encoding="utf-8"),
                  indent=4, ensure_ascii=False)

    def _update(self):
        self.meta['writeTime'] = self._getLastModifiedTime()
    
    # Backup
    def _backupExtFiles(self, path):
        # FIXME: Not finished
        
        for file in glob(os.path.join(self.path, PROJECT_EXT, '**'), recursive=True):
            relpath = self._getRelativePath(file)
            if relpath not in [item[0] for item in self.extFiles] and os.path.isfile(file):
                dst = os.path.join(path, relpath)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy(file, dst)
                self.extFiles.append([relpath, getFileSha256(file)])

    def _backupArcFiles(self, path):
        arcdir = os.path.join(path, PROJECT_ARC)
        os.makedirs(arcdir, exist_ok=True)
        for arcfile in glob(os.path.join(self.path, PROJECT_ARC, '*')):
            name = os.path.basename(arcfile)
            if name not in self.arcFiles and os.path.exists(arcfile):
                if os.path.isdir(arcfile):
                    zipFolder(arcfile, os.path.join(arcdir, name+'.zip'))
                else:
                    shutil.copy(arcfile, os.path.join(arcdir, name))
                self.arcFiles.append(name)
        # Remove arcdir if empty
        if not os.listdir(arcdir):
            os.rmdir(arcdir)

    def _backupCommonFiles(self, path):
        zipname = os.path.join(path, getDateStr() + ' ' +
                               self.meta.get('name') + '.zip')
        commonFiles = glob(os.path.join(self.path, '**'), recursive=True) +\
            glob(os.path.join(self.path, '**', '.*'), recursive=True)
        with zipfile.ZipFile(zipname, 'w') as zipf:
            for file in commonFiles:
                relpath = self._getRelativePath(file)
                if re.match('(?!'+'|'.join([PROJECT_TMP, PROJECT_EXT, PROJECT_ARC])+').*', relpath) and os.path.isfile(file):
                    zipf.write(file, relpath)

    def backup(self, path, saveCfg=True):
        self.meta['writeTime'] = self._getLastModifiedTime()
        self.meta['backupTime'] = time.time()
        self.meta['version'] = self.meta['version'] + 1

        self._backupArcFiles(path)
        self._backupExtFiles(path)
        
        if saveCfg:
            self._save()
        self._backupCommonFiles(path)


