import os
import tempfile
import json
from datetime import datetime
from glob import glob
from typing import overload
from .const import *

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
            print(file)
            if os.path.isfile(file) and os.path.getmtime(file) > ltime:
                ltime = os.path.getmtime(file)
        return ltime
    
    def _getLastModifiedDateTime(self):
        return datetime.fromtimestamp(self._getLastModifiedTime())
    
    def update(self):
        pass
