# 去除背景色
# 创建人：曾逸夫
# 创建时间：2022-03-05

import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from rich.console import Console
from tqdm import tqdm

from opencv_webcam.utils.path_opt import increment_path
from opencv_webcam.utils.time_format import time_format

ROOT_PATH = Path(sys.path[0])  # 根目录
BAR_FORMAT = "{l_bar}{bar:20}{r_bar}{bar:-20b}"  # tqdm 进度条长度

console = Console()


# 去除背景色
def rm_bg_color(input_dir, rmbgColorMode):

    rmbgc_PATH = increment_path(ROOT_PATH / Path("remove_bgColor") / "rmbgc", exist_ok=False)  # 增量运行
    rmbgc_PATH.mkdir(parents=True, exist_ok=True)  # 创建目录

    imgs_list = os.listdir(input_dir)  # 获取图片集
    imgs_tqdm = tqdm(imgs_list, bar_format=BAR_FORMAT)  # 加载到tqdm

    rmbgc_startTime = time.time()
    for i in imgs_tqdm:
        imgs_tqdm.set_description(f"正在压缩：{i}")

        img_input_path = ROOT_PATH / input_dir / i  # 图片路径
        img = cv2.imread(str(img_input_path))  # 读取图片
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # RGB2HSV

        # 可以过滤掉大部分类型的背景色
        if rmbgColorMode == "green":
            # ------绿色HSV范围------
            COLOR_MIN_LIST = [35, 43, 46]
            COLOR_MAX_LIST = [77, 255, 255]
        elif rmbgColorMode == "blue":
            # ------蓝色HSV范围------
            COLOR_MIN_LIST = [78, 43, 46]
            COLOR_MAX_LIST = [124, 255, 255]

        bgc_min = np.array(COLOR_MIN_LIST)
        bgc_max = np.array(COLOR_MAX_LIST)

        bgc_mask = cv2.inRange(img_hsv, bgc_min, bgc_max)  # 确定背景色区域掩码
        bgc_mask_not = cv2.bitwise_not(bgc_mask)  # 确定非背景色区域掩码

        bgc_not_img = cv2.bitwise_and(img, img, mask=bgc_mask_not)  # 获取非背景色区域

        # ------重组图像------
        b, g, r = cv2.split(bgc_not_img)
        img_new = cv2.merge([b, g, r, bgc_mask_not])

        img_output_path = Path(f"{rmbgc_PATH}/{i}")  # 输出路径
        cv2.imwrite(str(img_output_path.with_suffix(".png")), img_new)  # 保存

    rmbgc_endTime = time.time()
    rmbgc_totalTime = rmbgc_endTime - rmbgc_startTime
    rmbgc_msg = f"[bold green]背景色去除成功！[/bold green][bold blue]用时：[/bold blue]{time_format(rmbgc_totalTime)}，[bold blue]已保存在[/bold blue]{rmbgc_PATH}"
    console.print(rmbgc_msg)
    return rmbgc_msg
