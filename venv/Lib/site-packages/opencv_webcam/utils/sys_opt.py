# 系统管理
# 创建人：曾逸夫
# 创建时间：2022-03-10

import shutil
import sys

import psutil

ROOT_PATH = sys.path[0]  # 项目根目录

# -------- 计算单位 --------
kb = 1 << 10
mb = 1 << 20
gb = 1 << 30


# CPUs和RAM的信息
def cpus_ram():
    cpus = psutil.cpu_count()
    ram = psutil.virtual_memory().total
    ram = f"{ram / gb:.1f}"

    return cpus, ram


# 硬盘信息
def disk_msg():
    total, used, free = shutil.disk_usage(ROOT_PATH)
    total = f"{total / gb:.1f}"
    used = f"{used / gb:.1f}"
    free = f"{free / gb:.1f}"

    return total, used, free


# 预计保存图片数
def pre_saveImgs(save_imgSize):
    _, _, free = shutil.disk_usage(ROOT_PATH)  # 读取磁盘可用容量
    pre_imgNum = int(free / save_imgSize)  # 计算预计保存图片数

    return pre_imgNum
