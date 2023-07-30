import os
from glob import glob
from core.utils import getDateStr
from .project import Project, isProject
from .const import *


class ProjectMgr(object):
    
    def __init__(self, repoPath: str):
        self.repoPath = repoPath
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
    
    def printProjects(self, bkpThresh=BACKUP_THRESHOLD):
        for key in self.prjDict:
            print('['+PROJECT_TYPESTR[key]+']')
            for prj in self.prjDict[key]:
                if prj.meta['writeTime'] - prj.meta['backupTime'] >= bkpThresh * 86400:
                    bkptag = '■'
                else:
                    bkptag = '□'
                print("{6} {0} | Create:{1} | Write:{2} | Bak:{3} | Ver:{4} | Type:{5}"
                      .format(prj.meta['name'][:10], getDateStr(prj.meta['createTime']),
                              getDateStr(prj.meta['writeTime']), getDateStr(prj.meta['backupTime']),
                              prj.meta['version'], prj.meta['type'], bkptag))
    
    def backupProjects(self, backupPath: str, saveCfg=True, bkpThresh=BACKUP_THRESHOLD):
        """Backup all projects to backupPath
        :param backupPath: The path to backup projects.
        :param saveCfg: Whether to save configs of projects.
        :param bkpThresh: The backup threshold. (How many days the modified time is ahead of the backup time).
        """
        for key in self.prjDict:
            for prj in self.prjDict[key]:
                createdate = getDateStr(prj.meta['createTime'])
                year = createdate[0:4]
                name = ' '.join([createdate, prj.meta['name']])
                prjbakpath = os.path.join(backupPath, PROJECT_TYPESTR[key], year, name)
                print("Backup {0} to {1}".format(prj.meta['name'], prjbakpath))
                if prj.meta['writeTime'] - prj.meta['backupTime'] >= bkpThresh * 86400:
                    prj.backup(prjbakpath, saveCfg=saveCfg)
        
    
    def _saveProjects(self):
        """Save Configs of all projects"""
        for key in self.prjDict:
            for prj in self.prjDict[key]:
                prj._save()