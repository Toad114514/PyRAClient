import logging, os
from logging.handlers import RotatingFileHandler

def setup_logger():
    # 1. 创建全局唯一的 Logger 实例
    logger = logging.getLogger("PyRAClient")
    logger.setLevel(logging.INFO)  # 总阀门：允许抓取最高精度的 DEBUG 级信息

    # 2. 定义高可读性的标准日志格式
    # [时间] [级别] (线程名) 触发位置: 消息内容
    log_format = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] (%(threadName)s) %(filename)s:%(lineno)d: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 3. 🎯 管道 A：控制台实时输出（发给坐在显示器前狂按 F5 调试的你）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # 调试期全开，芝麻绿豆大的事都打印
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # 4. 🎯 管道 B：本地文件循环滚动输出（专门收集好发给用户，用来提 Bug 撕逼）
    # 单个日志文件最大 5MB，超过后自动切片，最多保留 3 个备份（app.log, app.log.1, app.log.2）
    log_file_path = "debug.log"
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)  # 稳健级别：文件里只存核心业务和报错，防止刷盲目数据把盘撑爆
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    logger.info("Welcome to using PyRAClient!")
    logger.info("日志记录启动")
    return logger

log = setup_logger()