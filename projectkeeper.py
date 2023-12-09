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

def print_matchfiles(prj, *args, **kwargs):
    print(prj.meta['name'])
    print("\n".join(prj.matchCommonFiles("(.*)\.xmind$", depth=-1)))

global rename2xmind8_tot
rename2xmind8_tot = 0
def rename2xmind8(prj, *args, **kwargs):
    global rename2xmind8_tot
    print(prj.meta['name'])
    for file in prj.matchCommonFiles("(.*)\.xmind$", depth=TRAVERSE_DEPTH):
        os.rename(file, file + "8")
        rename2xmind8_tot += 1
        print(file + "8")
    print("Total: " + str(rename2xmind8_tot))
    
global rename2xmind_tot
rename2xmind_tot = 0
def rename2xmind(prj, *args, **kwargs):
    global rename2xmind_tot
    print(prj.meta['name'])
    for file in prj.matchCommonFiles("(.*)\.xmind8$", depth=TRAVERSE_DEPTH):
        os.rename(file, file[:-1])
        rename2xmind_tot += 1
        print(file[:-1])
    print("Total: " + str(rename2xmind_tot))

# Init ProjectMgr
# prjMgr = ProjectMgr("test")
prjMgr = ProjectMgr("D:\\SFTR")


# Backup
bkpThresh = 1
# prjMgr.printProjects(detail=True, bkpThresh=bkpThresh)
# prjMgr.backupProjects("D:\\SFTR\\PlayerOS\\6 Backup\\Backup", bkpThresh=bkpThresh)
# prjMgr.backupProjects("test\\bak", saveCfg=False, bkpThresh=0)


# Batch Modify
prjMgr._batchModify(rename2xmind8)
# prjMgr._saveProjects()

# prjMgr.addProject("飞行器设计综合实验", TYPE_STUDY)
# prjMgr.addProject("RCAMC实验室事务", TYPE_WORK)
