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
        
    def printProjects(self):
        for key in self.prjDict:
            print('['+key+']')
            for prj in self.prjDict[key]:
                print("{0} | Create:{1} | Write:{2} | Backup:{3} | Version:{4}"
                      .format(prj.meta['name'], getDateStr(prj.meta['createTime']),
                              getDateStr(prj.meta['writeTime']), getDateStr(prj.meta['backupTime']),
                              prj.meta['version']))
    
    def backupProjects(self, backupPath: str):
        """Backup all projects to backupPath"""
        for key in self.prjDict:
            for prj in self.prjDict[key]:
                createdate = getDateStr(prj.meta['createTime'])
                year = createdate[0:4]
                name = ' '.join([createdate, prj.meta['name']])
                prjbakpath = os.path.join(backupPath, key, year, name)
                print("Backup {0} to {1}".format(prj.meta['name'], prjbakpath))
                prj.backup(prjbakpath)
        
    
    def _saveProjects(self):
        """Save Configs of all projects"""
        for key in self.prjDict:
            for prj in self.prjDict[key]:
                prj._save()