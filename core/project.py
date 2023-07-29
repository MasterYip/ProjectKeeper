import os
import shutil
import tempfile
import json
import zipfile
import re
import time
from datetime import datetime
from glob import glob
from .const import *
from .utils import getFileSha256, getDateStr, zipFolder


class Project(dict):

    def __init__(self, prjPath: str, create=True):
        """
        Load a project from a path.
        :param prjPath: The path of the project.
        :param create: If the project does not exist, create it when creat=True. If false, raise an exception.
        """
        
        self.name = os.path.basename(prjPath)  # Default Project name (If config file not found)
        self.meta = {}
        self.meta['name'] = self.name
        self.extFiles = []
        self.arcFiles = []
        # Not saved in config file
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
            self._init()
        else:
            raise FileNotFoundError('Project not found.')
        
        self.files = []
        self.subprojects = []
        
    def _init(self):
        os.makedirs(self.tmpPath, exist_ok=True)
        os.makedirs(self.extPath, exist_ok=True)
        os.makedirs(self.arcPath, exist_ok=True)
        self.meta['createTime'] = time.time()
        self.meta['writeTime'] = time.time()
        self.meta['backupTime'] = time.time()
        self.meta['version'] = 0
        # TODO:Type
        self.update()
        pass
    
    def _load(self):
        data = json.load(open(self.cfgPath, 'r'))
        self.meta = data.get('meta', {})
        self.extFiles = data.get('extFiles', [])
        self.arcFiles = data.get('arcFiles', [])
        pass
    
    def _loadLegacy(self):
        pass
    
    def _getLastModifiedTime(self):
        ltime = 0
        for file in glob(os.path.join(self.path, '**'), recursive=True):
            if os.path.isfile(file) and os.path.getmtime(file) > ltime:
                ltime = os.path.getmtime(file)
        return ltime
    
    def _getRelativePath(self, path):
        return os.path.relpath(path, self.path)
    
    def _getLastModifiedDateTime(self):
        return datetime.fromtimestamp(self._getLastModifiedTime())
    
    def _backupExtFiles(self, path):
        # FIXME: Not finished
        os.makedirs(os.path.join(path, PROJECT_EXT), exist_ok=True)
        for file in glob(os.path.join(self.path, PROJECT_EXT, '**'), recursive=True):
            relpath = self._getRelativePath(file)
            if relpath not in [item[0] for item in self.extFiles] and os.path.isfile(file):
                shutil.copy(file, os.path.join(path, relpath))
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
            
    def _backupCommonFiles(self, path):
        zipname = os.path.join(path, getDateStr() + ' ' + self.name + '.zip')
        commonFiles = glob(os.path.join(self.path, '**'), recursive=True) +\
                        glob(os.path.join(self.path, '**', '.*'), recursive=True)
        with zipfile.ZipFile(zipname, 'w') as zipf:
            for file in commonFiles:
                relpath = self._getRelativePath(file)
                print(relpath)
                if re.match('(?!'+'|'.join([PROJECT_TMP, PROJECT_EXT, PROJECT_ARC])+').*', relpath) and os.path.isfile(file):
                    zipf.write(file, relpath)
    
    def backup(self, path):
        self.meta['writeTime'] = self._getLastModifiedTime()
        self['meta'] = self.meta
        self['extFiles'] = self.extFiles
        self['arcFiles'] = self.arcFiles
        
        self._backupArcFiles(path)
        self._backupExtFiles(path)
        json.dump(self, open(os.path.join(self.path, PROJECT_CFG), 'w'), indent=4, ensure_ascii=False)
        self._backupCommonFiles(path)
        
    
    def update(self):
        pass
    
