# 日志管理
# 创建人：曾逸夫
# 创建时间：2022-01-14

import sys

from rich.console import Console

from opencv_webcam.utils.fonts_opt import fonts_color

ROOT_PATH = sys.path[0]  # 项目根目录


# 检查日志格式
def is_logSuffix(logName):
    console = Console()
    suffixList = ["log", "txt", "data"]  # 日志后缀列表
    log_suffix = logName.split(".")[-1]  # 获取日志后缀
    if log_suffix not in suffixList:
        # 判断日志是否符合格式
        console.print("[bold red]日志格式不正确！程序结束！[/bold red]")
        sys.exit()  # 结束程序


# 日志管理
def log_management(logContent, logName, logSaveMode):
    # -------------过滤Bash Shell字体颜色符号-------------
    color_dict, end_color = fonts_color()
    for k in color_dict.keys():
        logContent = logContent.replace(color_dict[k], "").replace(end_color, "")

    logFile = open(f"{ROOT_PATH}/{logName}", logSaveMode)  # 日志文件
    logFile.write(logContent)  # 日志写入


# 日期时间&帧数
def date_time_frames(date_time, frames, fdn, fsd):
    f = open(f"{ROOT_PATH}/date_time_frames.csv", "a")  # 创建文件
    f.write(f"{date_time},{frames},{fdn},{fsd}\n")  # 写入


# 日志管理（rich版）
def rich_log(logContent, logName, logSaveMode):
    report_file = open(f"{ROOT_PATH}/{logName}", logSaveMode)
    console = Console(file=report_file)
    console.log(logContent)
