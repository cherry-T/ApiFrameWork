__author__ = 'tangcl'
import logging
import re
import os
from logging.handlers import TimedRotatingFileHandler
from common import project_path

#1：import  from..import  导入一个模块的时候，Python会先到当前目录下找
# --->找不到的情况 再去Python的环境变量的路径下去找

class MyLog:
    def my_log(self, level, msg):
        """
        自定义日志收集器，可以定义日志的输出级别，定制日志是否需要输出到控制台做调试
        输出的日志，可保存到相应的文件，在跑接口自动化时，作用明显
        level:日志级别
        msg: 日志信息
        """
        my_logger = logging.getLogger("logsMessage")
        # 设置日志的收集级别
        my_logger.setLevel("DEBUG")
        # 创造一个专属输出渠道  过滤 和排版
        # 设置日志的输出格式：时间+文件名称+具体的日志信息
        formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(filename)s-%(name)s-日志信息:%(message)s')

        # 日志可输出到日志和具体的文件
        # 1、 输出到控制台
        ch = logging.StreamHandler()
        # 设置输出级别  大写  ！！！！这里必须要设置，默认收集warning级别以上的错误（不设置收集不到info error的日志）
        ch.setLevel("DEBUG")
        ch.setFormatter(formatter)

        # 2、 输出到制定文件，将日志信息收集到文件
        # 3、 输出到文件拓展，每天生成一个文件，保存近5天的的log文件，防止文件过大的
        # interval 滚动周期， when="MIDNIGHT", interval=1 表示每天0点为更新点，每天生成一个文件,backupCount  表示日志保存个数
        # filename：要加上每天的日期拼接组成
        logs_path = os.path.join(project_path.logs_path_day, 'log')
        # 先将when改成Minutes,每隔2分钟，生成一个文件  interval=1,
        file_hander = TimedRotatingFileHandler(filename=logs_path, when='midnight')
        # 设置生成日志文件名的格式，以年-月-日来命名
        # suffix设置，会生成文件名为log.2020-02-25.log # 按时间S的 命名格式 %Y-%m-%d %H-%M-%S.log
        file_hander.suffix = "%Y-%m-%d.log"
        # extMatch是编译好正则表达式，用于匹配日志文件名后缀
        # 需要注意的是suffix和extMatch一定要匹配的上，如果不匹配，过期日志不会被删除。
        file_hander.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        file_hander.setFormatter(formatter)

        # 日志收集器添加一个渠道，分别将输出到控制台、输出到具体文件的日志收集器，添加到渠道
        my_logger.addHandler(ch)
        my_logger.addHandler(file_hander)

        # 传进日志级别，根据级别，输出对应的级别的日志信息
        if level == 'DEBUG':
            my_logger.debug(msg)
        elif level == 'INFO':
            my_logger.info(msg)
        elif level == 'WARNING':
            my_logger.warning(msg)
        elif level == 'ERROR':
            my_logger.error(msg)
        elif level == 'EXCEPTION':
            my_logger.exception(msg)
        elif level == 'CRITICAL':
            my_logger.critical(msg)

        # 渠道使用完，要移除渠道，否则，会输出重复的日志
        my_logger.removeHandler(ch)
        my_logger.removeHandler(file_hander)

    def debug(self, msg):
        """
        输出日志级别为debug的日志
        msg:日志信息
        """
        self.my_log("DEBGU", msg)

    def info(self, msg):
        """
        输出日志级别为info（普通日志）的日志
        msg:日志信息
        """
        self.my_log("INFO", msg)

    def warning(self, msg):
        """
        输出日志级别为warning（警告）的日志
        msg:日志信息
        """
        self.my_log("ERROR", msg)

    def error(self, msg):
        """
        输出日志级别为error（错误）的日志
        msg:日志信息
        """
        self.my_log("WARNING", msg)

    def exception(self, msg):
        """
        输出日志级别为warning（警告）的日志
        msg:日志信息
        """
        self.my_log("EXCEPTION", msg)

    def critical(self, msg):
        """
        输出日志级别为critical(致命级别)的日志
        msg:日志信息
        """
        self.my_log("CRITICAL", msg)

# if __name__ == '__main__':
    # my_logger= MyLog()
    # my_logger.debug("天啦噜，水滴同学没有见过日志！")
    # my_logger.info("小场面 ，不要慌！")      #print
    # my_logger.warning("这么巧，Monica陪着水滴没见过日志！")