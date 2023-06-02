__author__ = 'Tangcl'
__qq__ = '1334518618'

# 1.获取文件的绝对路径 os.path.realpath(__file__)
# 2.对路径进行分割os.path.split，第三次分割后，取元组第一个

import os


# 获取本文件 除上一层和本文件外的路径
real_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]

# 配置文件路径，使用join（）文件路径拼接
# 1.配置文件的路径 config/api.config
config_path = os.path.join(real_path, 'config', 'api.config')

# 2.测试数据文件路径
test_data = os.path.join(real_path, 'test_data', 'erp_testCase.xlsx')                 # crm ifpos的测试用例
promotion_data = os.path.join(real_path, 'test_data', 'promotion_testCase.xlsx')      # 促销活动的测试用例
create_promtion_data = os.path.join(real_path, 'test_data', 'create_promotion.xlsx')  # 创建促销活动的测试用例
shop_name_data = os.path.join(real_path, 'test_data', 'shopfees.xlsx')
oms_data = os.path.join(real_path, 'test_data', 'oms_testcase.xlsx')  # oms模块的测试用例
inv_data = os.path.join(real_path, 'test_data', 'inv_testcase.xlsx')  # 库存中心的测试用例

# 3.测试报告路径
test_report = os.path.join(real_path, 'test_result', 'report', 'api_testResult.html')
report_dir = os.path.join(real_path, 'test_result', 'report')

# 日志地址
logs_path = os.path.join(real_path, 'test_result', 'logs', 'logs.txt')
# 每天生成的log_path
logs_path_day = os.path.join(real_path, 'test_result', 'logs')

# 测试环境 数据库配置文件，如果切换其他环境，需要更改这里的路径
mysql_path = os.path.join(real_path, 'config', 'database', 'DB.config')
demo_mysql_path = os.path.join(real_path, 'config', 'database', 'DemoDB.config')

# 接口host的配置文件: 不同环境的host不同
api_host = os.path.join(real_path, 'config', 'hosts', 'environment.config')
demo_api_host = os.path.join(real_path, 'config', 'hosts', 'environment_demo.config')