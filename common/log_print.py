# -*- coding: utf-8 -*-
# @Time: 2022/8/3 11:47
# @Author: tangcl
# @Desc:  文件用于
__author__ = 'tangcl'

import logging
import colorlog
import re
import os
from logging.handlers import TimedRotatingFileHandler
# from cloghandler import ConcurrentRotatingFileHandler
from common import project_path
from faker.factory import logger as fakerlog
from comtypes import logger as comtypeslog

# faker 屏蔽debug一下的log,否则会将faker的日志全打印出来
fakerlog.setLevel(logging.WARNING)
comtypeslog.setLevel(logging.WARNING)

'''
封装生成日志的类： 
1、设置logger收集DEBUG级别，分别输出到控制台和日志文件(定时生成)
2、直接判断当前logger是否有处理器handler，如果没有，创建处理器
3、将通过logger.info，进行调用，否则，获取到的filename为当前log封装的地址，不是调用文件的地址
    common_fun：调用：       
    from Common.log_print import LogPrint
    LogPrint().logger.info("log print test")
4、 设置定时生成文件，凌晨生成，要有程序执行mylog，启动调用才会生成一个新的日期的文件；20220803日志到18点，此后没有调起mylog，不会生成文件；
    第二天调起mylog，生成一个0803的文件，同时新的log会写到新的文件
5、 日志内容输出格式： 包含调起文件名称，调用的方法，即行号
'''


class LogPrint:

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel("DEBUG")

        # == 1、将现有的handlers移除，后面再创建 ==
        while self.logger.hasHandlers():
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)

        self.log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }

        self.color_fmt = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s [%(filename)s:%(funcName)s:%(lineno)s] [%(levelname)s]: %(message)s',
            log_colors=self.log_colors_config)

        # -日志信息
        self.formatter = logging.Formatter(
            '%(asctime)s [%(filename)s:%(funcName)s:%(lineno)s] [%(levelname)s]: %(message)s')

        self.logger.addHandler(self.get_console_handler())
        self.logger.addHandler(self.get_file_handler())

        # 二次分装info，获取到的filename为当前log文件名，非调用文件名，所以要通过logger.info来输出日志，打印的文件名才正确
        # 如果出现erp_api_auto_work的日志文件，没有写入最新的日志，查看是否写到了Erp2_selenium_project日志，可能因为handler没关闭，所以直接写到了这里

    def get_console_handler(self):
        '''输出到控制台'''
        # ch = logging.StreamHandler(sys.stdout) # 设置了sys.stdout 控制台不输出日志
        # ch = logging.StreamHandler()
        # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
        ch = logging.StreamHandler()
        ch.setFormatter(self.color_fmt)
        return ch

    # def get_current_file_handler(self):
    #     ''' 暂时没用：多线程日志轮转日志处理器 20221228注释：导入ConcurrentRotatingFileHandler报错 '''
    #     logs_path = os.path.join(project_path.logs_path_day, 'log')
    #     file_handler = ConcurrentRotatingFileHandler(filename=logs_path, mode="a", maxBytes=512*1024, backupCount=5)
    #     file_handler.setFormatter(self.formatter)
    #     return file_handler

    def get_file_handler(self):
        '''根据时间轮转 生成日志 '''
        logs_path = os.path.join(project_path.logs_path_day, 'log')
        # , encoding="utf-8"
        file_hander = TimedRotatingFileHandler(filename=logs_path, when='midnight', backupCount=7)

        # suffix和extMatch要与设置的when匹配，若设置为日，则传入的正则suffix应该是日："%Y-%m-%d.log"
        file_hander.suffix = "%Y-%m-%d.log"

        # suffix和extMatch一定要匹配的上，如果不匹配，过期日志不会被删除。 re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        file_hander.extMatch = r"^\d{4}-\d{2}-\d{2}.log$"
        file_hander.extMatch = re.compile(file_hander.extMatch)
        file_hander.setFormatter(self.formatter)

        return file_hander


logger = LogPrint().logger