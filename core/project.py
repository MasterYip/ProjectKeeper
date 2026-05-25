import os
import shutil
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
        (os.path.isfile(os.path.join(path, PROJECT_CFG)) or
         os.path.isfile(os.path.join(path, PROJECT_CFG_LEGACY)))


class Project(dict):
    # Private
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
        with open(self.cfgPath, 'r', encoding='utf-8') as cfgfile:
            data = json.load(cfgfile)
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
        self.meta['type'] = PROJECT_TYPE[project_data[6]
                                         ] if project_data[6] < len(PROJECT_TYPE) else TYPE_OTHER
        # self.meta['type'] = project_data[6]
        self._save()

    def _getRelativePath(self, path):
        """Get relative path of a file in project."""
        return os.path.relpath(path, self.path)

    def _getAbsolutePath(self, relpath):
        return os.path.join(self.path, relpath)

    def _getLastModifiedTime(self, depth=TRAVERSE_DEPTH):
        # FIXME: deleting files will not be recorded
        ltime = 0
        for file in traverseFolder(self.path, depth=depth, file_only=True):
            if os.path.getmtime(file) > ltime and os.path.basename(file) != PROJECT_CFG:
                ltime = os.path.getmtime(file)
        return ltime

    def _getLastModifiedDateTime(self):
        return datetime.fromtimestamp(self._getLastModifiedTime())

    def _save(self):
        """Save project config file."""
        # Aux Info
        self.meta['createDate'] = getDateStr(self.meta['createTime'])
        self.meta['backupDate'] = getDateStr(self.meta['backupTime'])
        self.meta['writeDate'] = getDateStr(self.meta['writeTime'])

        self['meta'] = self.meta
        self['extFiles'] = self.extFiles
        self['arcFiles'] = self.arcFiles
        # Set it visible to read
        if (os.path.isfile(os.path.join(self.path, PROJECT_CFG))):
            os.system('attrib -h ' + '\"' + os.path.join(self.path, PROJECT_CFG) + '\"')
        json.dump(self, open(os.path.join(self.path, PROJECT_CFG), 'w', encoding="utf-8"),
                  indent=4, ensure_ascii=False)
        # Set it invisible
        os.system('attrib +h ' + '\"' + os.path.join(self.path, PROJECT_CFG) + '\"')

    def _update(self):
        """Update project info (Write time only for now).
        """
        self.meta['writeTime'] = self._getLastModifiedTime()
        # FIXME: Maybe it is not a good idea because it will modify config file.
        # self._save()

    def _copyCommonFiles(self, dstPath):
        """Copy common files (exclude temp/ext/arc folders)."""
        copied = 0
        exclude_names = {PROJECT_TMP, PROJECT_EXT, PROJECT_ARC}
        for item in os.listdir(self.path):
            src = os.path.join(self.path, item)
            dst = os.path.join(dstPath, item)
            if item in exclude_names:
                continue
            self._copyPath(src, dst, overwrite=True)
            if os.path.isfile(src):
                copied += 1
            elif os.path.isdir(src):
                for _, _, files in os.walk(src):
                    copied += len(files)
        return copied

    def _removePath(self, path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    def _copyPath(self, src, dst, overwrite=False):
        if overwrite and os.path.exists(dst):
            self._removePath(dst)
        if os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            shutil.copytree(src, dst)

    def copyTo(self,
               dstPath,
               copyProject=True,
               copyEvent=True,
               copyExt=True,
               copyTemp=False,
               includeConfig=True,
               overwrite=False):
        """Copy project content to a new directory.

        Args:
            dstPath (str): destination project directory.
            copyProject (bool): copy common project files.
            copyEvent (bool): copy event records folder.
            copyExt (bool): copy extension package folder.
            copyTemp (bool): copy temp folder.
            includeConfig (bool): copy project config file.
            overwrite (bool): allow existing destination directory.

        Returns:
            dict: copy summary.
        """
        dstPath = os.path.abspath(dstPath)
        if os.path.exists(dstPath) and (not overwrite):
            raise FileExistsError("Destination exists: {0}".format(dstPath))

        os.makedirs(dstPath, exist_ok=True)

        summary = {
            'project': self.meta.get('name', os.path.basename(self.path)),
            'srcPath': self.path,
            'dstPath': dstPath,
            'copiedCommonFiles': 0,
            'copiedEvent': False,
            'copiedExt': False,
            'copiedTemp': False,
            'copiedConfig': False
        }

        if copyProject:
            summary['copiedCommonFiles'] = self._copyCommonFiles(dstPath)

        if copyEvent and os.path.isdir(self.arcPath):
            self._copyPath(self.arcPath, os.path.join(dstPath, PROJECT_ARC), overwrite=overwrite)
            summary['copiedEvent'] = True

        if copyExt and os.path.isdir(self.extPath):
            self._copyPath(self.extPath, os.path.join(dstPath, PROJECT_EXT), overwrite=overwrite)
            summary['copiedExt'] = True

        if copyTemp and os.path.isdir(self.tmpPath):
            self._copyPath(self.tmpPath, os.path.join(dstPath, PROJECT_TMP), overwrite=overwrite)
            summary['copiedTemp'] = True

        if includeConfig:
            cfgSrc = self.cfgPath if os.path.isfile(self.cfgPath) else self.cfgPathLegacy
            if os.path.isfile(cfgSrc):
                self._copyPath(cfgSrc, os.path.join(dstPath, os.path.basename(cfgSrc)), overwrite=overwrite)
                summary['copiedConfig'] = True

        return summary

    # Public
    def getPath(self):
        return self.path

    # Analysis
    def getChangedExtFiles(self):
        """Get new extended files in project.

        Returns:
            list: lists of new extended files and modified extended files.
        """
        newExtFiles = []
        modifiedExtFiles = []
        for file in glob(os.path.join(self.path, PROJECT_EXT, '**'), recursive=True):
            if os.path.isfile(file):
                relpath = self._getRelativePath(file)
                sha256 = getFileSha256(file)
                # New extended files
                if relpath not in [item[0] for item in self.extFiles]:
                    newExtFiles.append([relpath, sha256])
                else:
                    index = [item[0] for item in self.extFiles].index(relpath)
                    if self.extFiles[index][1] != sha256:
                        modifiedExtFiles.append([relpath, sha256])
        return newExtFiles, modifiedExtFiles

    def getNewArcFiles(self):
        newArcFiles = []
        for arcfile in glob(os.path.join(self.path, PROJECT_ARC, '*')):
            name = os.path.basename(arcfile)
            if name not in self.arcFiles and os.path.exists(arcfile):
                newArcFiles.append(name)
        return newArcFiles

    def matchCommonFiles(self, pattern, depth=TRAVERSE_DEPTH):
        """Match common files by pattern.
        This only searches common files, not including external files and arc files.
        :param pattern: The re pattern to match.
        :param depth: The depth to search.
        """
        files = []
        for file0 in os.listdir(self.path):
            file0 = self._getAbsolutePath(file0)
            if os.path.isfile(file0):
                if re.match(pattern, os.path.basename(file0)):
                    files.append(file0)
            elif os.path.isdir(file0) and\
                    file0 != self.tmpPath and file0 != self.extPath and file0 != self.arcPath:
                for file in traverseFolder(file0, depth=depth, file_only=True):
                    if re.match(pattern, os.path.basename(file)):
                        files.append(file)
        return files

    # Backup
    def _backupExtFileNew(self, path, relpath, sha256):
        """Backup extended files.

        Args:
            path (str): Backup destination path.
            relpath (str): relative path of the file.
            sha256 (str): sha256 value of the file.
        """
        src = self._getAbsolutePath(relpath)
        dst = os.path.join(path, relpath)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        self.extFiles.append([relpath, sha256])

    def _backupExtFileMod(self, path, relpath, sha256, index):
        """Backup modified extended files.

        Args:
            path (str): Backup destination path.
            relpath (str): relative path of the file.
            sha256 (str): sha256 value of the file.
            index (int): index of the file in extFiles list.
        """
        src = self._getAbsolutePath(relpath)
        dst = os.path.join(path, relpath)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        self.extFiles[index][1] = sha256

    def _backupExtFiles(self, path):
        """Backup extended files.

        Args:
            path (str): Backup destination.
        Note:
            1. For newly added files, append them to extFiles list, backup them to path.
            2. For modified files, update the sha256 value in extFiles list, backup them to path
            (BaiduCloud will rename them with number suffix). 
            3. For newly added duplicated files with sha256 repeated, deem them as new files.
        """
        for file in glob(os.path.join(self.path, PROJECT_EXT, '**'), recursive=True):
            if os.path.isfile(file):
                relpath = self._getRelativePath(file)
                sha256 = getFileSha256(file)
                # Newly added files
                if relpath not in [item[0] for item in self.extFiles]:
                    self._backupExtFileNew(path, relpath, sha256)
                else:
                    index = [item[0] for item in self.extFiles].index(relpath)
                    if self.extFiles[index][1] != sha256:
                        self._backupExtFileMod(path, relpath, sha256, index)

    def _backupArcFiles(self, path):
        arcdir = os.path.join(path, PROJECT_ARC)
        os.makedirs(arcdir, exist_ok=True)
        for name in self.getNewArcFiles():
            src = os.path.join(self.path, PROJECT_ARC, name)
            if os.path.isdir(src):
                zipFolder(src, os.path.join(arcdir, name + '.zip'))
            else:
                shutil.copy(src, os.path.join(arcdir, name))
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
                if re.match('(?!' + '|'.join([PROJECT_TMP, PROJECT_EXT, PROJECT_ARC]) + ').*', relpath) and os.path.isfile(file):
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
