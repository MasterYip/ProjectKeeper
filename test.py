from core import *

def modify(prj, *args, **kwargs):
    print(prj.meta['name'])
    print(args)
    print(kwargs)
    if prj.meta['type'] == TYPE_STUDY:
        prj.meta['type'] = 0
    elif prj.meta['type'] == TYPE_PROJECT:
        prj.meta['type'] = 1
    elif prj.meta['type'] == TYPE_WORK:
        prj.meta['type'] = 2
    elif prj.meta['type'] == TYPE_DAILY:
        prj.meta['type'] = 3
    elif prj.meta['type'] == TYPE_RECREATION:
        prj.meta['type'] = 4
    else:
        prj.meta['type'] = 5


# prjMgr = ProjectMgr("test")
prjMgr = ProjectMgr("D:\\SFTR")

# prjMgr.printProjects(detail=True)
prjMgr.backupProjects("D:\\SFTR\\PlayerOS\\6 Backup\\Backup")
# prjMgr.backupProjects("test\\bak", saveCfg=False, bkpThresh=0)


# Batch Modify
# prjMgr._batchModify(modify)
# prjMgr._saveProjects()

# prjMgr.addProject("test", 1)