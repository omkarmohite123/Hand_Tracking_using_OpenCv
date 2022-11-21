# 文件压缩
# 创建人：曾逸夫
# 创建时间：2022-01-19

import os
import sys
import tarfile
import time
import zipfile
from pathlib import Path

from rich.console import Console
from tqdm import tqdm

from opencv_webcam.utils.path_opt import increment_path
from opencv_webcam.utils.time_format import time_format

COMPRESS_SUFFIX = ["zip", "tar"]  # 压缩文件格式
ROOT_PATH = sys.path[0]  # 项目根目录
BAR_FORMAT = "{l_bar}{bar:20}{r_bar}{bar:-20b}"  # tqdm 进度条长度

console = Console()


# 判断压缩文件格式
def is_compressFile(compressStyle):
    if compressStyle not in COMPRESS_SUFFIX:
        print(f"{compressStyle}：不正确！程序退出！")
        sys.exit()


# webcam帧压缩
def webcam_compress(compressStyle, is_autoCompressName, compressName, preCompressFilePath, compressMode):
    # ----------- 减少压缩目录深度 -----------
    preCompressFilePath = str(preCompressFilePath).split("/")
    preCompressFilePath = f"{preCompressFilePath[-2]}/{preCompressFilePath[-1]}"

    # 帧压缩文件保存路径管理
    COMPRESS_PATH = increment_path(Path(f"{ROOT_PATH}/CompressFrames") / "compress", exist_ok=False)  # 增量运行
    COMPRESS_PATH.mkdir(parents=True, exist_ok=True)  # 创建目录

    if is_autoCompressName:
        # 自动命名
        compressNameTmp = preCompressFilePath.split("/")[-1]  # 获取帧目录名称
        # 自动命名压缩文件名称
        compressName = f"{COMPRESS_PATH}/{compressNameTmp}.{compressStyle}"
    else:
        # 自定义命名
        compressName = f"{COMPRESS_PATH}/{compressName}.{compressStyle}"

    file_list = os.listdir(preCompressFilePath)  # 获取目录下的文件名称
    file_tqdm = tqdm(file_list, bar_format=BAR_FORMAT)  # 获取进度条

    # ---------- 压缩开始 ----------
    compress_startTime = time.time()  # 压缩开始时间
    if compressStyle == COMPRESS_SUFFIX[0]:
        # zip压缩
        compress_file = zipfile.ZipFile(compressName, compressMode)
        for i in file_tqdm:
            file_tqdm.set_description(f"正在压缩：{i}")
            compressing_file = f"{preCompressFilePath}/{i}"
            compress_file.write(compressing_file, compress_type=zipfile.ZIP_DEFLATED)  # 写入zip文件
    elif compressStyle == COMPRESS_SUFFIX[1]:
        # tar压缩
        compress_file = tarfile.open(compressName, compressMode)
        for i in file_tqdm:
            file_tqdm.set_description(f"正在压缩：{i}")  # 加入打印压缩信息
            compressing_file = f"{preCompressFilePath}/{i}"  # 压缩文件
            compress_file.add(compressing_file)  # 写入tar文件

    # ---------- 压缩结束 ----------
    compress_file.close()
    compress_endTime = time.time()  # 压缩结束时间
    compress_totalTime = compress_endTime - compress_startTime  # 压缩用时
    # 压缩消息
    compress_msg = f"[bold green]文件压缩成功！[/bold green][bold blue]用时：[/bold blue]{time_format(compress_totalTime)}，[bold blue]已保存在：[/bold blue]{compressName}"
    console.print(compress_msg)
    return compress_msg
