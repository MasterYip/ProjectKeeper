import re
import os
from glob import glob

DO_OPERATION = False

def rename2xmind8(path):
    tot = 0
    for file in glob(os.path.join(path, "**/*.xmind"), recursive=True):
        if DO_OPERATION:
            os.rename(file, file + "8")
        tot += 1
        print(file + "8")
    print("Total: " + str(tot))
    
def rename2xmind(path):
    tot = 0
    for file in glob(os.path.join(path, "**/*.xmind8"), recursive=True):
        if DO_OPERATION:
            os.rename(file, file[-1])
        tot += 1
        print(file[:-1])
    print("Total: " + str(tot))
    
if __name__ == "__main__":
    DO_OPERATION = True
    rename2xmind8("D:\\SFTR\\PlayerOS")