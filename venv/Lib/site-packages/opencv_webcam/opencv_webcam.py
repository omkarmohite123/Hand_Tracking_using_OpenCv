# OpenCV Webcam Script v0.9
# 创建人：曾逸夫
# 创建时间：2022-04-09

# ----------------- 检查依赖 -----------------
from opencv_webcam.utils.check_opt import check_hotkey, check_requirements

check_requirements()

import argparse
import ast
import gc
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
from PIL import ImageFont
from pyfiglet import figlet_format
from rich.console import Console

from opencv_webcam.utils.args_yaml import argsYaml
from opencv_webcam.utils.compress import is_compressFile, webcam_compress
from opencv_webcam.utils.fonts_opt import is_fonts
from opencv_webcam.utils.frame_opt import file_size, frame_opt, frames_transform
from opencv_webcam.utils.log import date_time_frames, is_logSuffix, rich_log
from opencv_webcam.utils.path_opt import increment_path
from opencv_webcam.utils.plot import csv2chart
from opencv_webcam.utils.rm_bgColor import rm_bg_color
from opencv_webcam.utils.sys_opt import cpus_ram, disk_msg, pre_saveImgs
from opencv_webcam.utils.time_format import time_format

ROOT_PATH = sys.path[0]  # 项目根目录
OWS_VERSION = "OpenCV Webcam Script v0.9"  # 项目名称与版本号
COUNTDOWN_FRAMES = 150  # 倒计时帧数
COUNTDOWN_FONTSIZE = 25  # 倒计时字体大小

console = Console()


def parse_args(known=False):
    parser = argparse.ArgumentParser(description="OpenCV Webcam Script v0.9")
    parser.add_argument(
        "--device",
        "-dev",
        default="0",
        type=str,
        help="device index for webcam, 0 or rtsp",
    )
    parser.add_argument("--quit", "-q", default="q", type=str, help="quit key for webcam")
    parser.add_argument("--is_autoSaveFrame", "-isasf", action="store_true", help="is auto save frame")
    parser.add_argument("--is_handSaveFrame", "-ishsf", action="store_true", help="is hand save frame")
    parser.add_argument("--is_resizeFrame", "-isrf", action="store_true", help="is resize frame")
    parser.add_argument(
        "--frame_saveDir",
        "-fsd",
        default="WebcamFrame",
        type=str,
        help="save frame dir",
    )
    parser.add_argument(
        "--frame_dirName",
        "-fdn",
        default="frames",
        type=str,
        help="save frame dir name",
    )
    parser.add_argument(
        "--frame_nSave",
        "-fns",
        default=1,
        type=int,
        help="n frames save a frame (auto save frame)",
    )
    parser.add_argument(
        "--frame_capKey",
        "-fck",
        default="a",
        type=str,
        help="frame capture key (hand save frame)",
    )
    parser.add_argument("--resize_frame", "-rf", default="640,480", type=str, help="resize frame save")
    parser.add_argument(
        "--resizeRatio_frame",
        "-rrf",
        default=1.0,
        type=float,
        help="resize ratio frame save",
    )
    parser.add_argument(
        "--frame_namePrefix",
        "-fnp",
        default="frame",
        type=str,
        help="frame name prefix",
    )
    parser.add_argument("--frame_saveStyle", "-fss", default="jpg", type=str, help="frame save style")
    parser.add_argument(
        "--jpg_quality",
        "-jq",
        default=95,
        type=int,
        help="frame save jpg quality (0-100) default 95",
    )
    parser.add_argument(
        "--png_quality",
        "-pq",
        default=3,
        type=int,
        help="frame save jpg quality (0-9) default 3",
    )
    parser.add_argument("--pause", "-p", default="p", type=str, help="webcam pause")
    parser.add_argument(
        "--auto_frameNum",
        "-afn",
        default=0,
        type=int,
        help="auto save number of frames",
    )

    # 日志
    parser.add_argument("--logName", "-ln", default="ows.log", type=str, help="log save name")
    parser.add_argument("--logMode", "-lm", default="a", type=str, help="log write mode")
    # 压缩
    parser.add_argument("--is_compress", "-isc", action="store_true", help="is compress file")
    parser.add_argument("--compressStyle", "-cs", default="zip", type=str, help="compress style")
    parser.add_argument(
        "--is_autoCompressName",
        "-isacn",
        action="store_true",
        help="is auto compress name",
    )
    parser.add_argument("--compressName", "-cn", default="ows", type=str, help="compress save name")
    parser.add_argument(
        "--compressMode",
        "-cm",
        default="w",
        type=str,
        help="compress save mode, tar w:gz",
    )

    # 去除背景色
    parser.add_argument(
        "--is_rmbgColor",
        "-isrbgc",
        action="store_true",
        help="is remove background color",
    )
    parser.add_argument(
        "--rmbgColorMode",
        "-rbgcm",
        default="green",
        type=str,
        help="remove background color mode",
    )

    # 手动调整窗体大小
    parser.add_argument(
        "--is_resizeWindow",
        "-isrw",
        action="store_true",
        help="is resize window",
    )

    args = parser.parse_known_args()[0] if known else parser.parse_args()
    return args


# Webcam OpenCV
def webcam_opencv(
        device_index="0",  # 设备号
        quit_key="q",  # 退出键
        pause_key="p",  # 暂停键
        is_autoSaveFrame=False,  # 自动保存帧
        frame_saveDir="WebcamFrame",  # 帧保存路径
        frame_dirName="frames",  # 帧目录
        frame_nSave=1,  # 每隔n帧保存一次
        auto_frameNum=0,  # 自动保存最大帧数
        is_handSaveFrame=False,  # 手动保存帧
        frame_capKey="a",  # 设置帧捕获键
        is_resizeFrame=False,  # 重塑帧
        resize_frame="640,480",  # 自定义帧尺寸
        resizeRatio_frame=1.0,  # 自定义帧缩放比
        frame_namePrefix="frame",  # 自定义帧前缀
        frame_saveStyle="jpg",  # 帧保存类型
        jpg_quality=95,  # jpg质量系数
        png_quality=3,  # png质量系数
        logName="ows.log",  # 日志名称
        logMode="a",  # 日志模式
        is_compress=False,  # 压缩帧
        compressStyle="zip",  # 压缩类型
        is_autoCompressName=False,  # 自动命名压缩文件
        compressName="ows",  # 自定义压缩文件名称
        compressMode="w",  # 压缩模式
        is_rmbgColor=False,  # 去除背景色
        rmbgColorMode="green",  # 背景色模式
        is_resizeWindow=False,  # 调整窗体大小
):

    # ----------------- 快捷键 ------------------
    keyList = [quit_key, frame_capKey, pause_key]  # 快捷键列表
    check_hotkey(keyList)  # 快捷键冲突判断

    # ----------------- 日志文件 ------------------
    is_logSuffix(logName)  # 检测日志格式
    logTime = f"{datetime.now():%Y-%m-%d %H:%M:%S}"  # 日志时间
    rich_log(f"{logTime}\n", logName, logMode)  # 记录日志时间

    # ----------------- 压缩文件 ------------------
    is_compressFile(compressStyle)  # 检测压缩文件格式

    # ----------------- 设备管理 ------------------
    dev_index = (ast.literal_eval(device_index) if device_index.isnumeric() else device_index)  # 设备选择 (usb 0,1,2; rtsp)
    cap = cv2.VideoCapture(dev_index)  # 设备连接
    is_capOpened = cap.isOpened()  # 判断摄像头是否正常启动

    if is_capOpened:  # 设备连接成功
        # ------------------ 程序开始 ------------------
        s_time = time.time()  # 起始时间
        console.print(figlet_format("O W S", font="alligator"))  # ows logo
        console.print(f"🚀 欢迎使用[bold blue]{OWS_VERSION}[/bold blue]，摄像头连接成功！\n")

        # ------------------ 系统信息 ------------------
        console.rule("💡 系统信息")
        console.print(
            f"[bold blue]操作系统：[/bold blue]{platform.uname()[0]}, [bold blue]计算机名：[/bold blue]{platform.uname()[1]}, "
            f"[bold blue]系统版本：[/bold blue]{platform.uname()[3]}, [bold blue]系统架构：[/bold blue]{platform.uname()[4]}, "
            f"[bold blue]Python版本：[/bold blue]{platform.python_version()}\n")

        cpus, ram = cpus_ram()
        total, used, free = disk_msg()
        console.print(
            f"[bold blue]CPU：[/bold blue]{cpus} CPUs, [bold blue]RAM：[/bold blue]{ram} GB RAM, "
            f"[bold blue]当前硬盘已用：[/bold blue]{used} GB|[bold blue]空闲：[/bold blue]{free} GB|[bold blue]共计：[/bold blue]{total} GB\n"
        )

        # ------------------ 参数显示 ------------------
        console.rule(f"✨ {OWS_VERSION} 参数信息")
        console.print(
            f"{device_index=}, {quit_key=}, {pause_key=}, {is_autoSaveFrame=}, {frame_saveDir=},\n"
            f"{frame_dirName=}, {frame_nSave=}, {auto_frameNum=}, {is_handSaveFrame=}, {frame_capKey=},\n"
            f"{is_resizeFrame=}, {resize_frame=}, {resizeRatio_frame=}, {frame_namePrefix=}, {frame_saveStyle=},\n"
            f"{jpg_quality=}, {png_quality=}, {logName=}, {logMode=}, {is_compress=}, {compressStyle=},\n"
            f"{is_autoCompressName=}, {compressName=}, {compressMode=}\n")

        # ----------------- 设备参数 ------------------
        bufferSize = cap.get(cv2.CAP_PROP_BUFFERSIZE)  # 缓存数
        frame_width = int(cap.get(3))  # 帧宽度
        frame_height = int(cap.get(4))  # 帧高度
        fps = int(cap.get(5))  # 帧率

        x_c = frame_width // 2  # 中心点横坐标
        y_c = frame_height // 2  # 中心点纵坐标

        console.rule(f"🔥 {OWS_VERSION} 程序开始！")
        console.print(f"[bold blue]宽度：[/bold blue]{frame_width}, [bold blue]高度：[/bold blue]{frame_height}, "
                      f"[bold blue]FPS：[/bold blue]{fps}, [bold blue]缓存数：[/bold blue]{bufferSize}")

        # ----------------- 帧保存路径管理 ------------------
        frame_savePath = ""  # 保存路径
        if is_autoSaveFrame or is_handSaveFrame:
            # 帧保存路径管理
            frame_savePath = increment_path(Path(f"{ROOT_PATH}/{frame_saveDir}") / frame_dirName,
                                            exist_ok=False)  # 增量运行
            frame_savePath.mkdir(parents=True, exist_ok=True)  # 创建目录

        # ----------------- 帧相关参数 ------------------
        frame_num = 0  # 总帧数
        frame_countdown = 0  # 倒计时
        frame_hand_num = 0  # 手动保存帧数
        frame_n_num = 0  # 每隔n帧保存一次
        save_flag = 0  # 保存标志

        windows = []  # 窗体

        # ----------------- 字体库 ------------------
        is_fonts(f"{ROOT_PATH}/fonts")  # 检查字体文件
        # 加载字体
        textFont = ImageFont.truetype(str(f"{ROOT_PATH}/fonts/SimSun.ttc"), size=COUNTDOWN_FONTSIZE)

        # ------------------ OWS 循环 ------------------
        while is_capOpened:
            wait_key = cv2.waitKey(20) & 0xFF  # 键盘监听
            _, frame = cap.read()  # 捕获画面
            frame_countdown += 1  # 倒计时
            if is_resizeWindow:
                if platform.system() == 'Linux' and OWS_VERSION not in windows:
                    # 参考：https://github.com/ultralytics/yolov5/pull/8330
                    # 参考：https://github.com/ultralytics/yolov5/pull/8318
                    # 参考：https://github.com/ultralytics/yolov5/pull/8712
                    # 手动调整窗体大小，不影响保存尺寸
                    windows.append(OWS_VERSION)
                    cv2.namedWindow(OWS_VERSION, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                    cv2.resizeWindow(OWS_VERSION, frame_width, frame_height)
            else:
                cv2.namedWindow(OWS_VERSION)  # 设置窗体

            # ------------------ 倒计时150帧启动程序 ------------------
            if frame_countdown <= COUNTDOWN_FRAMES:
                # 倒计时提示信息
                countdown_msg = f"倒计时：{COUNTDOWN_FRAMES - frame_countdown + 1}帧\n请将设备调整到合适的位置，\n准备开始。。。"
                # 帧转换
                frame_array = frames_transform(frame, countdown_msg, textFont, (x_c, y_c), COUNTDOWN_FONTSIZE)
                cv2.imshow(OWS_VERSION, frame_array)  # 显示画面
                del frame_array  # 释放数组资源

            else:
                frame_num += 1  # 帧计数
                frame_write = frame.copy()  # 复制帧
                # 加入帧ID输出信息
                cv2.putText(
                    frame,
                    f"Frame ID: {frame_num}",
                    (50, 50),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL,
                    1,
                    (205, 250, 255),
                    2,
                )
                cv2.imshow(OWS_VERSION, frame)  # 显示画面

                # ------------------ 帧保存模式 ------------------
                if is_autoSaveFrame:  # 自动保存
                    if auto_frameNum > 0 and frame_num > auto_frameNum:
                        # 设置自动最大保存帧数
                        frame_num -= 1  # 修复帧数显示问题
                        break
                    if frame_num % frame_nSave == 0:  # 每隔n帧保存一次
                        frame_n_num += 1
                        frame_opt(
                            frame_write,
                            frame_savePath,
                            frame_num,
                            is_resizeFrame,
                            resize_frame,
                            resizeRatio_frame,
                            frame_namePrefix,
                            frame_saveStyle,
                            jpg_quality,
                            png_quality,
                        )
                elif is_handSaveFrame:  # 手动保存
                    if wait_key == ord(frame_capKey):  # 保存键
                        frame_hand_num += 1  # 手动帧计数
                        frame_opt(
                            frame_write,
                            frame_savePath,
                            frame_num,
                            is_resizeFrame,
                            resize_frame,
                            resizeRatio_frame,
                            frame_namePrefix,
                            frame_saveStyle,
                            jpg_quality,
                            png_quality,
                        )

                # ------------------ 预保存图片数 ------------------
                if (save_flag == 0 and frame_savePath != "" and os.listdir(frame_savePath) != []):
                    save_img = open(f"{frame_savePath}/{os.listdir(frame_savePath)[0]}", "rb")  # 读取保存目录中的一张图片
                    save_imgSize = len(save_img.read())  # 获取保存图片的大小
                    pre_imgNum = pre_saveImgs(save_imgSize)  # 获取预计保持图片数
                    console.print(f"[bold green]预计存储{pre_imgNum}张图片[/bold green]\n")
                    save_flag = 1  # 保存标志更改

                # ------------------ 快捷键设置 ------------------
                if wait_key == ord(quit_key):  # 退出 ord：字符转ASCII码
                    break
                elif wait_key == ord(pause_key):
                    console.print("[bold blue]已暂停！按任意键继续。。。[/bold blue]")
                    cv2.waitKey(0)  # 暂停，按任意键继续
            del frame  # 释放数组资源
            gc.collect()  # 释放内存资源

        # ------------------ 输出信息与日志记录 ------------------
        if is_autoSaveFrame:
            # 帧保存信息（自动版）
            if frame_n_num > 0:
                frame_num = frame_n_num  # 每隔n帧保存一次
            frame_saveSize = file_size(frame_savePath)  # 计算保存文件的大小
            frameSaveMsg = f"[bold blue]自动版：[/bold blue]共计{frame_num} 帧，[bold blue]文件大小：[/bold blue]{frame_saveSize:.2f} MB，[bold blue]已保存在[/bold blue]{frame_savePath}\n"
            console.print(frameSaveMsg)
            rich_log(f"{frameSaveMsg}", logName, logMode)  # 记录帧保存信息
            date_time_frames(logTime, frame_num, frame_dirName, frame_saveDir)  # 记录时间与帧数
        elif is_handSaveFrame:
            # 帧保存信息（手动版）
            frame_saveSize = file_size(frame_savePath)  # 计算保存文件的大小
            frameSaveMsg = f"[bold blue]手动版：[/bold blue]共计{frame_hand_num} 帧，[bold blue]文件大小：[/bold blue]{frame_saveSize:.2f} MB，[bold blue]已保存在[/bold blue]{frame_savePath}\n"
            console.print(frameSaveMsg)
            rich_log(f"{frameSaveMsg}", logName, logMode)  # 记录帧保存信息
            date_time_frames(logTime, frame_hand_num, frame_dirName, frame_saveDir)  # 记录时间与帧数
        else:
            date_time_frames(logTime, 0, frame_dirName, frame_saveDir)  # 记录非帧保存状态

        # ------------------ 资源释放 ------------------
        cap.release()  # 释放缓存资源
        cv2.destroyAllWindows()  # 删除所有窗口

        # ------------------程序结束------------------
        console.rule(f"🔥 {OWS_VERSION} 程序结束！")
        e_time = time.time()  # 终止时间
        total_time = e_time - s_time  # 程序用时
        # 格式化时间格式，便于观察
        outTimeMsg = f"[bold blue]用时：[/bold blue]{time_format(total_time)}"
        console.print(outTimeMsg)  # 打印用时
        rich_log(f"{outTimeMsg}\n", logName, logMode)  # 记录用时

        # ------------------ 压缩文件 ------------------
        if is_compress and (is_autoSaveFrame or is_handSaveFrame):
            # 压缩信息
            compress_msg = webcam_compress(
                compressStyle,
                is_autoCompressName,
                compressName,
                frame_savePath,
                compressMode,
            )
            rich_log(f"{compress_msg}\n", logName, logMode)  # 记录用时

        # ------------------ 创建chart ------------------
        csv2chart("./date_time_frames.csv")  # 创建日期-帧数图

        # ------------------ 去除背景色 ------------------
        if is_rmbgColor:
            rmbgc_msg = rm_bg_color(frame_savePath, rmbgColorMode)
            rich_log(f"{rmbgc_msg}\n", logName, logMode)  # 记录用时

    else:
        # 连接设备失败
        console.print("[bold red]摄像头连接异常！[/bold red]")


def main(args):

    device_index = args.device
    quit_key = args.quit
    is_autoSaveFrame = args.is_autoSaveFrame
    is_handSaveFrame = args.is_handSaveFrame
    frame_saveDir = args.frame_saveDir
    frame_dirName = args.frame_dirName
    frame_nSave = args.frame_nSave
    frame_capKey = args.frame_capKey
    resize_frame = args.resize_frame
    is_resizeFrame = args.is_resizeFrame
    resizeRatio_frame = args.resizeRatio_frame
    frame_namePrefix = args.frame_namePrefix
    frame_saveStyle = args.frame_saveStyle
    jpg_quality = args.jpg_quality
    png_quality = args.png_quality
    pause_key = args.pause
    auto_frameNum = args.auto_frameNum

    # 日志
    logName = args.logName
    logMode = args.logMode

    # 压缩
    is_compress = args.is_compress
    compressStyle = args.compressStyle
    is_autoCompressName = args.is_autoCompressName
    compressName = args.compressName
    compressMode = args.compressMode

    # 去除背景色
    is_rmbgColor = args.is_rmbgColor
    rmbgColorMode = args.rmbgColorMode

    # 手动调整窗体大小
    is_resizeWindow = args.is_resizeWindow

    argsYaml(args)  # 脚本参数

    # 调用webcam opencv
    webcam_opencv(
        device_index,
        quit_key,
        pause_key,
        is_autoSaveFrame,
        frame_saveDir,
        frame_dirName,
        frame_nSave,
        auto_frameNum,
        is_handSaveFrame,
        frame_capKey,
        is_resizeFrame,
        resize_frame,
        resizeRatio_frame,
        frame_namePrefix,
        frame_saveStyle,
        jpg_quality,
        png_quality,
        logName,
        logMode,
        is_compress,
        compressStyle,
        is_autoCompressName,
        compressName,
        compressMode,
        is_rmbgColor,
        rmbgColorMode,
        is_resizeWindow,
    )


if __name__ == "__main__":
    args = parse_args()
    main(args)
