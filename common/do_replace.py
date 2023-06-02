import datetime
import json
import string
import time

from common import project_path
from common.do_info import Do_Info
from common.do_mysql import DoMysql
from common.my_log import MyLog
from common.read_config import ConfigRead
from common.common_fun import CommunFun
from Common.data_manage import DataManage
from Common.data_manage import com_obj
from decimal import Decimal

# 处理带【'$xxx'】的数据
mylog = MyLog()
commonFun = CommunFun()


class DoReplace:
    def replace_url(self, url_data):
        '''
        为了适配在不同的环境下跑，接口Url中的grouid、ouid、shopid，实现为可替换
        目前有两种的替换方式，一种直接查询数据库，将grouid、ouid、shopid保存使用；一种直接在do_info传入对应的grouid、ouid、shopid
        两种方式的区别，do_info：可以手动配置目前测试数据较多的店铺
        :param url_data:
        :return:
        '''
        # 根据配置文件的config>environment.config，配置的url中的host地址进行替换
        if Do_Info.env == "test":
            config_url = eval(ConfigRead().read_config(project_path.api_host, 'TESTHOST', 'config'))
        else:
            config_url = eval(ConfigRead().read_config(project_path.demo_api_host, 'TESTHOST', 'config'))

        param_t = {"host": str(config_url['host']), "groupid": str(Do_Info.group_id), "ouid": str(Do_Info.ou_id),
                   "shopid": str(Do_Info.shop_id)}

        param =CommunFun().replace_string(param_source=url_data, param_dict=param_t)
        return param


if __name__ == '__main__':
    res = DoReplace().replace_url(url_data="")
    print(res)
