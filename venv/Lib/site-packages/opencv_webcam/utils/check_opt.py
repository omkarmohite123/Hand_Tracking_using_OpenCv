# 检查管理
# 创建人：曾逸夫
# 创建时间：2022-04-16

import os
import sys
from collections import Counter
from pathlib import Path

import pkg_resources as pkg
from pip._internal import main
from rich.console import Console

console = Console()

FILE = Path(__file__).resolve()
ROOT_PATH = FILE.parents[1]

def check_requirements(
    # 参考：https://github.com/ultralytics/yolov5/blob/master/utils/general.py
    requirements=f"{ROOT_PATH}/requirements.txt",
    exclude=[],
    install=True,
):
    if isinstance(requirements, (str, Path)):
        file = Path(requirements)
        assert file.exists(), f"{file.resolve()} not found, check failed."
        with file.open() as f:
            requirements = [f"{x.name}{x.specifier}" for x in pkg.parse_requirements(f) if x.name not in exclude]
    else:  # list or tuple of packages
        requirements = [x for x in requirements if x not in exclude]

    for r in requirements:
        try:
            pkg.require(r)
        except Exception:  # DistributionNotFound or VersionConflict if requirements not met
            s = f"{r} 是OWS所需要的依赖，但是没有被发现。"
            if install:
                try:
                    console.print(f"[bold red]{s}[/bold red][bold green]正在安装。。。[/bold green]")
                    # os.system(f"pip install {r}") # shell指令安装
                    main(["install", r])
                except Exception as e:
                    console.print(f"[bold red]{e}[/bold red]")
            else:
                console.print(f"[bold red]{s}请安装并重新运行指令。[/bold red]")


# 快捷键冲突判断
def check_hotkey(keyList):
    key_dict = dict(Counter(keyList))  # 快捷键统计

    # 判断快捷键是否冲突
    repeat_key = [key for key, value in key_dict.items() if value > 1]

    if repeat_key != []:
        console.print("[bold red]快捷键冲突! 程序结束！[/bold red]")
        sys.exit()  # 结束程序
