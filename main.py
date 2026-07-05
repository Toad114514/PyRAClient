import os, sys
from PyRACLib.log import log
os.environ["QT_LOGGING_RULES"] = "qt.network.interface=false;qt.network.ssl=false"

version="v0.1"

helpstr=f"""
PyRAClient - 在电脑上运行的 Python RetroAchievements 客户端
版本 {version}

用法：
  main.py [--option]

参数：
  --frontend <id> 使用特定前端启动，默认为 qt
  --help | -h 打印帮助信息
  --version | -v 打印版本信息

可选前端：
  qt/qt5/gui - 使用 PyQt5 搭建的前端
  tqt/tqt3 - 使用 Trinity Desktop Environment 生态的 PytQt3 搭建的前端，关于此技术栈的详情请查看：链接后面放
  rich/term/tui - 使用 Rich 搭建的前端，如果使用不支持显示图片的终端则不显示图片 
  web - 通过浏览器访问的前端，未完成，而且当前也不知道选哪个技术栈
注意：以上可选前端选择运行时必须需要先安装对应的前端包才能运行，否则会出现 ImportError 错误！

本项目使用 MIT Lisence 许可证协议。
项目由 toadXtech64 (Toad114514) 开发
"""

frontend = ""

def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    log.critical(
        "\nExcept was Happend!!!!!!!!! 狗哥说他不会叫我去找ai，狗哥是78。 ", 
        exc_info=(exc_type, exc_value, exc_traceback)
    )

sys.excepthook = global_exception_handler

if __name__ == "__main__":
    log.info("主脚本 main.py 启动")
    param = sys.argv[1:]
    if len(param) > 0:
        if "--version" in param or "-v" in param:
            print(version)
            exit()
        if "--help" in param or "-h" in param:
            print(helpstr)
            exit()
        if "--frontend" in param or "-f" in param:
            frontend = sys.argv[2]
    
    log.info(f"frontendId: {frontend}")
    match frontend:
        case "qt" | "qt5" | "gui" | "":
            log.info(f"Selected PyQt5 frontend")
            from PyQt5.QtWidgets import QApplication
            
            if QApplication.instance() is None:
                app = QApplication(sys.argv)
            from frontend.qt.main import Client
            main = Client()
            sys.exit(app.exec_())
        case "tqt" | "tqt3":
            print("没开发。。")
        case _:
            print("错误的前端 Id 参数。")
            