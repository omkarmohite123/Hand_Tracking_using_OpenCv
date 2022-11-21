# 作图
# 创建人：曾逸夫
# 创建时间：2022-01-27

import csv
import os
import sys
import time

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MaxNLocator
from rich.console import Console

from opencv_webcam.utils.time_format import time_format

OWS_VERSION = "OpenCV Webcam Script v0.9"  # 项目名称与版本号
ROOT_PATH = sys.path[0]  # 项目根目录

# --------------------- 颜色列表 ---------------------
COLOR_LIST = [
    "#f96801",
    "#800000",
    "#FFCC00",
    "#808000",
    "#00FF80",
    "#008080",
    "#000080",
    "#4B0080",
    "#FF7F50",
    "#CC5500",
    "#B87333",
    "#CC7722",
    "#704214",
    "#50C878",
    "#DE3163",
    "#003153",]

# --------------------- 字体库 ---------------------
SimSun_path = f"{ROOT_PATH}/fonts/SimSun.ttc"  # 宋体文件路径
TimesNesRoman_path = f"{ROOT_PATH}/fonts/TimesNewRoman.ttf"  # 新罗马字体文件路径
# 宋体
SimSun = font_manager.FontProperties(fname=SimSun_path, size=12)
# 新罗马字体
TimesNesRoman = font_manager.FontProperties(fname=TimesNesRoman_path, size=12)

console = Console()


# 创建折线图
def createLineChart(frames_y, date_list, time_list, fdn_list, fsd_list):
    chart_startTime = time.time()  # 作图开始时间

    # --------------------- 作图开始 ---------------------
    fdn_list_cls = list(set(fdn_list))  # 去重
    fdn_list_cls.sort(key=fdn_list.index)  # 顺序
    for i in range(len(fdn_list_cls)):
        tmp_time = []  # 临时时间列表，记录每个类
        tmp_frames = []  # 临时帧数列表，记录每个类
        tmp_fsd = []  # 临时数据集名称
        for j in range(len(fdn_list)):
            if fdn_list[j] == fdn_list_cls[i]:
                # 每个类别的时间和帧数
                tmp_time.append(time_list[j])  # 时间
                tmp_frames.append(frames_y[j])  # 帧数
                tmp_fsd.append(fsd_list[j])  # 帧数

        plt.figure(figsize=(8, 4))  # 画布尺寸
        plt.cla()  # 清除axes

        # Using categorical units to plot a list of strings that are all parsable as floats or dates. If these strings should be plotted as numbers, cast to the appropriate data type before plotting.
        plt.set_loglevel("WARNING")

        # 设置线型
        plt.plot(
            tmp_time,
            tmp_frames,
            color=COLOR_LIST[i],
            marker="o",
            label=f"{fdn_list_cls[i]}",
            markerfacecolor=COLOR_LIST[i],
            markersize=5,
        )

        ax = plt.gca()  # 获取当前的Axes对象
        plt.ylim(ymin=0)  # 纵坐标限定
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))  # 纵坐标设置为整数
        ax.spines["right"].set_color("none")  # 消除有边框
        ax.spines["top"].set_color("none")  # 消除上边框
        plt.grid(axis="y", ls="--")  # 横向网格线

        # 显示点值
        for a, b, c in zip(tmp_time, tmp_frames, tmp_fsd):
            # 显示帧数
            plt.text(
                a,
                b,
                f"{b}",
                ha="center",
                va="bottom",
                fontsize=10.5,
                fontproperties=TimesNesRoman,
            )
            # 显示数据集名称
            # plt.text(a, b, f'{c}', ha='center', va='top',
            #          fontsize=10.5, fontproperties=TimesNesRoman)

        # --------------------- 标题、横纵轴、图例等 ---------------------
        # 标题
        plt.title(OWS_VERSION, fontsize=12, fontproperties=TimesNesRoman)
        # 横轴标签，时间
        plt.xlabel(date_list[i], fontsize=12, fontproperties=TimesNesRoman)
        # 纵轴标签，帧数
        plt.ylabel("帧数", fontsize=12, fontproperties=SimSun)
        # 横轴刻度
        plt.xticks(fontproperties=TimesNesRoman, rotation=45, fontsize=12)
        # 纵轴刻度
        plt.yticks(fontproperties=TimesNesRoman, fontsize=12)
        # 图例
        plt.legend(prop=SimSun, fontsize=12, loc="best")

        # --------------------- chart保存信息 ---------------------
        # 创建DateFrames目录，以日期为子目录
        os.makedirs(f"{ROOT_PATH}/DateFrames/{date_list[i]}", exist_ok=True)
        # 图片路径，以类别为图片名称
        date_frames_chart_path = (f"{ROOT_PATH}/DateFrames/{date_list[i]}/{fdn_list_cls[i]}.png")
        # 保存图像
        plt.savefig(date_frames_chart_path, dpi=300, bbox_inches="tight")

        # --------------------- 作图结束 ---------------------
        chart_endTime = time.time()  # 作图结束时间
        chart_totalTime = chart_endTime - chart_startTime  # 作图用时
        console.print(f"[bold green]日期-帧数图创建成功！[/bold green][bold blue]用时：[/bold blue]{time_format(chart_totalTime)}，"
                      f"[bold blue]已保存在[/bold blue]{date_frames_chart_path}，[bold blue]总帧数：[/bold blue]{sum(frames_y)}")
    plt.close()  # 关闭窗口


# csv2chart
def csv2chart(csv_path):
    f = open(csv_path)  # 读取csv
    f_list = list(csv.reader(f))  # csv2list

    d_list = []  # 日期列表
    t_list = []  # 时间列表
    frames_list = []  # 帧数列表
    fdn_list = []  # 类别列表
    fsd_list = []  # 数据集名称列表

    tmp_date = f_list[0][0].split(" ")[0]  # 临时日期
    for i in range(len(f_list)):
        date_item = f_list[i][0].split(" ")[0]  # 日期
        time_item = f_list[i][0].split(" ")[1]  # 时间

        if tmp_date != date_item:
            createLineChart(frames_list, d_list, t_list, fdn_list, fsd_list)  # 创建日期-帧数图
            tmp_date = date_item  # 替换
            # ----------- 清空列表 -----------
            d_list = []  # 日期列表
            t_list = []  # 时间列表
            frames_list = []  # 帧数列表
            fdn_list = []  # 类别列表
            fsd_list = []  # 数据集名称列表

        d_list.append(date_item)  # 日期
        t_list.append(time_item)  # 时间
        frames_list.append(int(f_list[i][1]))  # 帧数
        fdn_list.append(f_list[i][2])  # 类别
        fsd_list.append(f_list[i][3])  # 数据集名称

        if i == len(f_list) - 1:
            # 最后一组
            createLineChart(frames_list, d_list, t_list, fdn_list, fsd_list)  # 创建日期-帧数图
