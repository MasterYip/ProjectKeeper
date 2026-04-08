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


def test_unc_path():
    import os

    # 请务必使用原始字符串 (r'...')，这可以防止反斜杠被误解为转义字符。
    unc_path = '\\\\Rcamc-r9000p\\sftr'  # 将这里的路径替换成你实际的UNC路径

    # 获取该目录下的所有文件和文件夹
    try:
        files = os.listdir(unc_path)
        print("文件和文件夹列表:", files)
    except FileNotFoundError:
        print(f"错误：无法找到UNC路径 '{unc_path}'，请检查路径和网络连接。")
    except PermissionError:
        print(f"错误：没有权限访问 '{unc_path}'。")


if __name__ == "__main__":
    # DO_OPERATION = True
    # rename2xmind8("D:\\SFTR\\PlayerOS")

    # # 要在PowerShell中运行的命令
    # powershell_command = 'Get-Process'

    # # 使用os.system()执行PowerShell命令
    # # os.system(f'powershell -command "{powershell_command}"')
    # os.system("attrib")

    test_unc_path()
