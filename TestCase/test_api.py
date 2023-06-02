import pytest
from ddt import ddt, data
from unittestreport import ddt, list_data
from common.do_excel import DoExcel
from common.http_request import HttpRequest
from common import project_path
from common.my_log import MyLog
from common.do_info import Do_Info
from common.PreconditionsFun import PreconditionsFun
from common.common_fun import CommunFun
from common.do_replace import DoReplace

preconditionsFun = PreconditionsFun()
communFun = CommunFun()
mylog = MyLog()

# 全局变量,有些接口需要有cookie才可以继续进行操作
COOKIE = None
TOKEN = None
header = None


class TestApi:

    apiconfig = 'APICONFIG'
    test_data = DoExcel(project_path.test_data, apiconfig).get_data()

    @pytest.mark.test_ifpos
    @pytest.mark.parametrize("data_item", test_data)
    def test_api(self, data_item):
        """
        测试用例编写：方法名一定要写test_开头 ，后面测试用例收集才可以识别
        :param data_item: 测试数据，通过数据驱动ddt加载
        :return:
        """
        # 开始执行接口
        mylog.info('正在运行第{0}条用例_{1}模块_{2}功能：{3}'.format(data_item['id'], data_item['module'],
                                                                data_item['function'], data_item['title']))

        # 20211223：把替换参数逻辑放到这里，传入参数，然后进行替换
        param = DoReplace().replace_parm(replaceparm=str(data_item), title=data_item['title'], module=data_item['module'])
        # 用例执行前的前置条件
        preconditionsFun.preconditionFun(data_item['title'], param)

        try:
            # parm=eval(data_item['parm']  更新改parm=eval(param)
            res = HttpRequest().http_request(module=data_item['module'], url=data_item['url'], parm=eval(param),
                                             http_method=data_item['http_method'], cookies=Do_Info.COOKIE,
                                             headers=header)
        except Exception as e:
            mylog.error("发起请求报错{0}".format(e))
        mylog.info("接口返回的结果是:{0}".format(res.json()))

        actualResult = ""
        testresult = ""
        # 断言assertEqual(预期，实际)
        try:
            if(str(data_item['assertType'])) == '0':
                # 全部比对 比对类型为0，完全比对
                actualResult = str(res.json())
                assert str(data_item['ExpectedResult']) == actualResult
            else:
                # 其他类型，为部分断言，直接把要取值的value，通过jsonpath，进行取值
                # 通过jsonpath，提取指定的值
                res = communFun.get_value_from_json_by_jsonpath(res.json(), data_item['assertType'])
                actualResult = str(res[0])
                assert str(data_item['ExpectedResult']) in actualResult
            testresult = 'PASS'
            mylog.info('预期结果为：{0},与实际结果是：{1},比对结果：{2}'.format(data_item['ExpectedResult'], actualResult, testresult))
        except AssertionError as e:
            testresult = 'Failed'
            mylog.error('预期结果与实际结果比对出现了异常，挂起{0}'.format(e))
            # 要挂起错误，不然报告统计不了，全部都是通过
            raise e
        finally:
            # 无论是否通过，写回结果
            # 要根据具体的接口进行回调填入，module名称要与excel的sheet_name一样,excel打开状态无法回写
            try:
                mylog.info("开始回写测试数据回excel")
                DoExcel(project_path.test_data, "APICONFIG").write_back(data_item['module'], data_item['id']+1,
                                                                        actualResult, testresult)
                PreconditionsFun().postconditionFun(data_item['title'], data_item['parm'])
            except Exception as e:
                mylog.error("回写测试结果出现了问题，请检查{0}".format(e))
                raise e








