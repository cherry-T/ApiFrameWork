# -*- coding: utf-8 -*-

import pytest
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"    # 部署到jenkins要加上这个，否则日志输出会报错

# 使用pytest执行用例，如果之前有使用unittest的话，要将引用的unittest去掉，不然还是会去走unittest配置的内容，然后在执行pytest的内容
# pytest 的重运行机制
# --reruns num(重运行次数)，--reruns-delay time(重运行间隔时间) : '--reruns=3', '--reruns-delay=2', ==='--reruns', '3',

#  "--html=OutPut\\report\\report.html",
#  "-q", "TestCase/test_promotion.py"，指定文件执行
# "-v", "TestCase/test_promotion.py" 指定文件，可以加::标明具体的类
# "-v"/"-q":可能会影响到用例收集，将部分用例删掉
# --lf: 只执行失败的用例 "--lf", 不是全部跑和设置失败重跑，不要加上--lf，不然有些用例会被deleted
# -x：出现一条测试用例失败就退出测试。在调试阶段非常有用，当测试用例失败时，应该先调试通过，而不是继续执行测试用例。
# -s：显示程序中的 print/logging 输出
# "-n=auto"、--tests-per-worker =1： 多线程执行用例，根据cpu核心数选择进程数  pip install pytest-parallel

pytest.main(["TestCase/test_api.py", "-m", "test_ifpos", '--lf',
             '--report=pytest_report.html', '--title=测试报告', '--tester=tangcl',
             '--desc==测试报告详细描述', "--junitxml=test_result\\allurereport\\report.xml",
             "--alluredir=test_result\\allurereport\\allure_results"
             ])



