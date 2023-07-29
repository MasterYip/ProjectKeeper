from core import Project

prj = Project('test\\prj1', create=True)
print(prj._getLastModifiedDateTime())
