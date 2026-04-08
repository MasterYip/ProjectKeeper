import os
from glob import glob
from core.utils import getDateStr
from .project import Project, isProject
from .utils import isFolderEmpty
from .const import *


class ProjectMgr(object):

    def __init__(self, repoPath: str):
        self.repoPath = os.path.abspath(repoPath)
        self.prjDict = dict([[key, []] for key in PROJECT_TYPE])
        # for dir in os.listdir(self.repoPath):
        #     basename = os.path.basename(dir)
        #     if basename in PROJECT_TYPE:
        #         print(os.listdir(dir))
        #         for prj in os.listdir(dir):
        #             if isProject(os.path.join(dir, prj)):
        #                 self.prjDict[basename].append(Project(os.path.join(dir, prj)))
        # FIXME: This is a temporary solution
        for dir in glob("{0}/*/*".format(self.repoPath)):
            if isProject(dir):
                prj = Project(dir)
                self.prjDict[prj.meta.get('type', TYPE_OTHER)].append(prj)

    def _batchModify(self, func, *args, **kwargs):
        """
        Batch modify all projects.
        :param func: The function to modify a project.
            func will be called like this: func(prj, *args, **kwargs)
        :param args: The arguments of the function.
        :param kwargs: The keyword arguments of the function.
        """
        for key in self.prjDict:
            for prj in self.prjDict[key]:
                func(prj, *args, **kwargs)

    def _saveProjects(self):
        """Save Configs of all projects"""
        for key in self.prjDict:
            for prj in self.prjDict[key]:
                prj._save()

    def listProjects(self):
        """List all projects with brief metadata."""
        data = []
        for key in self.prjDict:
            for prj in self.prjDict[key]:
                data.append({
                    'name': prj.meta.get('name'),
                    'type': key,
                    'typeStr': PROJECT_TYPESTR[key],
                    'path': prj.getPath(),
                })
        return data

    def getProject(self, name, type=None):
        """Get a project by name and optional type."""
        keys = [type] if type is not None else list(self.prjDict.keys())
        for key in keys:
            for prj in self.prjDict.get(key, []):
                if prj.meta.get('name') == name:
                    return prj, key
        return None, None

    def _backupProjectForMigration(self, prj, key, backupPath, saveCfg=True):
        createdate = getDateStr(prj.meta['createTime'])
        year = createdate[0:4]
        name = ' '.join([createdate, prj.meta['name']])
        prjbakpath = os.path.join(backupPath, PROJECT_TYPESTR[key], year, name)
        os.makedirs(prjbakpath, exist_ok=True)
        prj.backup(prjbakpath, saveCfg=saveCfg)
        return prjbakpath

    def copySelectedProjects(self,
                             destinationRoot,
                             selections,
                             copyProject=True,
                             copyEvent=True,
                             copyExt=True,
                             copyTemp=False,
                             includeConfig=True,
                             overwrite=False,
                             backupBeforeCopy=False,
                             backupPath=None,
                             saveCfg=True,
                             keepTypeDir=True):
        """Copy selected projects for migration.

        Args:
            destinationRoot (str): root output path.
            selections (list): list of {'name': str, 'type': int(optional)}.
            keepTypeDir (bool): keep project type folder in destination.
        """
        destinationRoot = os.path.abspath(destinationRoot)
        os.makedirs(destinationRoot, exist_ok=True)
        if backupBeforeCopy and not backupPath:
            raise ValueError('backupPath is required when backupBeforeCopy is True.')

        results = {
            'copied': [],
            'failed': [],
            'backups': []
        }

        for item in selections:
            name = item.get('name')
            typeValue = item.get('type')
            prj, key = self.getProject(name, type=typeValue)
            if prj is None:
                results['failed'].append({
                    'name': name,
                    'reason': 'Project not found'
                })
                continue

            try:
                if backupBeforeCopy:
                    bkp = self._backupProjectForMigration(prj, key, backupPath, saveCfg=saveCfg)
                    results['backups'].append({'name': name, 'path': bkp})

                dstParent = destinationRoot
                if keepTypeDir:
                    dstParent = os.path.join(destinationRoot, PROJECT_TYPESTR[key])
                os.makedirs(dstParent, exist_ok=True)
                dst = os.path.join(dstParent, prj.meta.get('name'))
                summary = prj.copyTo(
                    dst,
                    copyProject=copyProject,
                    copyEvent=copyEvent,
                    copyExt=copyExt,
                    copyTemp=copyTemp,
                    includeConfig=includeConfig,
                    overwrite=overwrite
                )
                results['copied'].append(summary)
            except Exception as ex:
                results['failed'].append({
                    'name': name,
                    'reason': str(ex)
                })

        return results

    def printProjects(self, detail=False, bkpThresh=BACKUP_THRESHOLD):
        for key in self.prjDict:
            print('[' + PROJECT_TYPESTR[key] + ']')
            for prj in self.prjDict[key]:
                if prj.meta['writeTime'] - prj.meta['backupTime'] >= bkpThresh * 86400:
                    bkptag = '■'
                else:
                    bkptag = '□'
                print("{6} {0} | Create:{1} | Write:{2} | Bak:{3} | Ver:{4} | Type:{5}"
                      .format(prj.meta['name'][:10], getDateStr(prj.meta['createTime']),
                              getDateStr(prj.meta['writeTime']), getDateStr(
                                  prj.meta['backupTime']),
                              prj.meta['version'], prj.meta['type'], bkptag))
                if detail:
                    newExtFiles, modifiedExtFiles = prj.getChangedExtFiles()
                    if len(newExtFiles) > 0:
                        print("\033[92m  NewExtFiles:\n    " + "\n    ".join([item[0] for item in newExtFiles]) + "\033[0m")
                    if len(modifiedExtFiles) > 0:
                        print("\033[93m  ModExtFiles:\n    " + "\n    ".join([item[0] for item in modifiedExtFiles]) + "\033[0m")
                    if len(prj.getNewArcFiles()) > 0:
                        print("\033[94m  NewArcFiles:\n    " + "\n    ".join([item for item in prj.getNewArcFiles()]) + "\033[0m")

    def addProject(self, name, type):
        """Add a new project"""
        prj = Project(os.path.join(self.repoPath, SFTR_PROJECT_DIR[type], name), create=True, initType=type)
        # prj = Project(os.path.join(self.repoPath, PROJECT_TYPESTR[type], name), create=True, initType=type)
        prj._save()
        self.prjDict[type].append(prj)
        return prj

    def backupProjects(self, backupPath: str, saveCfg=True, bkpThresh=BACKUP_THRESHOLD):
        """Backup all projects to backupPath
        :param backupPath: The path to backup projects.
        :param saveCfg: Whether to save configs of projects.
        :param bkpThresh: The backup threshold. (How many days the modified time is ahead of the backup time).
        """
        if isFolderEmpty(backupPath):
            for key in self.prjDict:
                for prj in self.prjDict[key]:
                    createdate = getDateStr(prj.meta['createTime'])
                    year = createdate[0:4]
                    name = ' '.join([createdate, prj.meta['name']])
                    prjbakpath = os.path.join(
                        backupPath, PROJECT_TYPESTR[key], year, name)
                    if prj.meta['writeTime'] - prj.meta['backupTime'] >= bkpThresh * 86400:
                        print("Backup {0} to {1}".format(prj.meta['name'], prjbakpath))
                        prj.backup(prjbakpath, saveCfg=saveCfg)
        else:
            print("Warning: please empty the files in backupPath")
