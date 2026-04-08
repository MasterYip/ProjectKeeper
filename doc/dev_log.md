# Dev Log

## 20250408 SFTR Migration

#file:projectkeeper.py  is a simple backup scrpt to manage projects. The majoro impl is #file:projectmgr.py  and #file:project.py .
Now, I hope to implement a new feature: to copy selected project to a new directory (e.g. for miggration). So the new script sould generate a manifest file (yaml),  after user configured (copy_projoect, copy_event, copy_ext, etc). And offer a option that backup the prject before copy.