# 字体管理
# 创建人：曾逸夫
# 创建时间：2022-01-27

import os
import sys
from pathlib import Path

import wget
from rich.console import Console

ROOT_PATH = sys.path[0]  # 项目根目录

fonts_list = ["SimSun.ttc", "TimesNewRoman.ttf"]  # 字体列表
fonts_suffix = ["ttc", "ttf", "otf"]  # 字体后缀

data_url_dict = {
    "SimSun.ttc": "https://gitee.com/CV_Lab/opencv_webcam/attach_files/959173/download/SimSun.ttc",
    "TimesNewRoman.ttf": "https://gitee.com/CV_Lab/opencv_webcam/attach_files/959172/download/TimesNewRoman.ttf",}

console = Console()


# 创建字体库
def add_fronts(font_diff):

    global font_name

    for k, v in data_url_dict.items():
        if k in font_diff:
            font_name = v.split("/")[-1]  # 字体名称
            Path(f"{ROOT_PATH}/fonts").mkdir(parents=True, exist_ok=True)  # 创建目录

            file_path = f"{ROOT_PATH}/fonts/{font_name}"  # 字体路径

            try:
                # 下载字体文件
                wget.download(v, file_path)
            except Exception as e:
                print("路径错误！程序结束！")
                print(e)
                sys.exit()
            else:
                print()
                console.print(f"{font_name} [bold green]字体文件下载完成！[/bold green] 已保存至：{file_path}")


# 判断字体文件
def is_fonts(fonts_dir):
    if os.path.isdir(fonts_dir):
        # 如果字体库存在
        f_list = os.listdir(fonts_dir)  # 本地字体库

        font_diff = list(set(fonts_list).difference(set(f_list)))

        if font_diff != []:
            # 字体不存在
            console.print("[bold red]字体不存在，正在加载。。。[/bold red]")
            add_fronts(font_diff)  # 创建字体库
        else:
            console.print(f"{fonts_list}[bold green]字体已存在！[/bold green]")
    else:
        # 字体库不存在，创建字体库
        console.print("[bold red]字体库不存在，正在创建。。。[/bold red]")
        add_fronts(fonts_list)  # 创建字体库


# 字体颜色（Bash Shell版）
def fonts_color():
    # 字体颜色
    pre_colorFlag = {
        "BLUE": "\033[94m",
        "GREEN": "\033[92m",
        "RED": "\033[91m",
        "YELLOW": "\033[93m",
        "BOLD": "\033[1m",
        "PURPLE": "\033[95m",
        "CYAN": "\033[96m",
        "DARKCYAN": "\033[36m",
        "UNDERLINE": "\033[4m",}

    end_colorFlag = "\033[0m"  # 结尾标志符

    return pre_colorFlag, end_colorFlag


# info warning字体颜色设置
def info_warning(msg):
    pre_colorFlag, end_colorFlag = fonts_color()
    info, success, warning = (
        pre_colorFlag["BLUE"] + pre_colorFlag["BOLD"],
        pre_colorFlag["GREEN"] + pre_colorFlag["BOLD"],
        pre_colorFlag["RED"] + pre_colorFlag["BOLD"],
    )

    info_msg = f"{info}{msg}{end_colorFlag}"
    success_msg = f"{success}{msg}{end_colorFlag}"
    warning_msg = f"{warning}{msg}{end_colorFlag}"

    return [info_msg, success_msg, warning_msg]
