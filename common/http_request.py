import datetime

import requests
from common.my_log import MyLog
from common.common_fun import CommunFun
from common.do_info import Do_Info
from common.read_config import ConfigRead
from common import project_path
import string
from Common.data_manage import com_obj
from common.do_replace import DoReplace
from common.do_mysql import DoMysql
from Common.data_manage import DataManage
from requests.adapters import HTTPAdapter
import time
import json

# 设计http_request方法，根据接口的请求类型来调用相应的处理，如果是get方式就调用get,这样设计的好处代码结构更清晰有层次，也更容易维护。

logger = MyLog()
communFun = CommunFun()

class HttpRequest:
    # 先注释，后面再看看要不要创建初始化函数，每次都要提供url和param
    # def __init__(self, url, param):
    #     self.url = url
    #     self.param = param
    def http_request_normal(self, url, parm, http_method, cookies, header=None):
        """
        不需要传入模块，区分传进参数的类型
        url:请求的地址
        param:请求的参数
        http_method:请求的方式
        cookies:是否需要cookies
         """
        function_name = communFun.get_function_name()
        if http_method.upper() == 'POST':
            try:
                logger.info("{2}_进行post请求，url为：{0},接口传入参数为：{1}".format(url, parm, function_name))
                res = requests.post(url, headers=header, data=parm, cookies=cookies)
            except requests.RequestException as e:
                logger.error("{1}_post请求出现了异常:{0}".format(e, function_name))
        elif http_method.upper() == "GET":
            try:
                logger.info("{2}_进行get请求，url为{0},接口传入参数为{1}".format(url, parm, function_name))
                res = requests.get(url, headers=header, data=parm, cookies=cookies)
            except requests.RequestException as e:
                logger.error("{1}_get请求出现了异常:{0}".format(e, function_name))
        elif http_method.upper() == "PUT":  # 用于修改
            try:
                logger.info("{2}_进行put请求，url为{0},接口传入参数为{1}".format(url, parm, function_name))
                res = requests.put(url, parm, cookies=cookies, headers=header)
            except requests.RequestException as e:
                logger.error("put请求出现了异常:{0}".format(e))
        logger.info("http请求的结果是:{0}".format(res.json()))
        res.close()
        return res

    def http_request(self, module, url, parm, http_method, headers, cookies=None):
        '''
        postman: boay使用 raw选择json的，要用json=parm传入参数
        发起的http请求，需要传入请求头，headers
        url: 请求url
        module:请求的模块,传入模块，crm请求参数直接带format:json，发起发起是无需指定；ifpos：传入参数没有指定json,需要通过json=parm，明确使用json作为参数
        parm:请求的参数
        '''
        function_name = communFun.get_function_name()
        method = http_method.upper()
        # 发起http请求，需要传入请求头headers
        try:
            logger.info("{2}_进行{3}请求，url为：{0},接口传入参数为：{1}".format(url, parm, function_name, method))
            if method == "POST":
                #  ifpos接口，前端传入已经是dict格式的数据，不过请求还是会报错，发起请求时，声明参数为json类型
                #  看看crm对接商城的接口，不能使用json=parm的方式进行请求，无需增加这个
                if module.upper() == 'CRM':
                    res = requests.post(url, headers=headers, data=parm, cookies=cookies)
                elif module.upper() == 'IFPOS':
                    res = requests.post(url, headers=headers, json=parm, cookies=cookies)
                else:
                    res = requests.post(url, headers=headers, data=parm, cookies=cookies)
            elif method == "GET":
                res = requests.get(url, parm, cookies=cookies, headers=headers)
            elif method == "PUT":
                res = requests.put(url, parm, cookies=cookies, headers=headers)
            else:
                res = requests.delete(url, headers=headers)
            res.close()
            logger.info("{0}_接口_返回：{1}".format(url, res.json()))
        except requests.RequestException as e:
            logger.error("{1}_{2}_请求出现了异常:{0}".format(e, function_name, method))
        finally:
            return res

    def send_request_json_data(self, url, parm, http_method, type="JSON", cookies=None, headers=None):
        '''
        postman: boay使用 raw选择json的，要用json=parm传入参数
        发起的http请求，需要传入请求头，headers
        url: 请求url
        module:请求的模块,传入模块，crm请求参数直接带format:json，发起发起是无需指定；ifpos：传入参数没有指定json,需要通过json=parm，明确使用json作为参数
        parm:请求的参数
        '''
        function_name = communFun.get_function_name()
        # 发起http请求，需要传入请求头headers
        if http_method.upper() == "POST":
            try:
                #  ifpos接口，前端传入已经是dict格式的数据，不过请求还是会报错，发起请求时，声明参数为json类型
                logger.info('{2}_发起post请求，url为：{0}，接口传入的参数：{1}'.format(url, parm, function_name))
                if type == 'JSON':
                    res = requests.post(url, headers=headers, json=parm, cookies=cookies)
                else:
                    res = requests.post(url, headers=headers, data=parm, cookies=cookies)
                # 请求完成后，关闭连接(若对同一个request高频率发起时，可能会出现Max retries exceeded with url)
                res.close()
            except Exception as e:
                logger.error("{1}_post请求_出现异常:{0}".format(e, function_name))
        elif http_method.upper() == "PUT":
            try:
                logger.info('{2}_发起put请求，url为：{0}，接口传入的参数：{1}'.format(url, parm, function_name))
                if type == 'JSON':
                    res = requests.put(url, headers=headers, json=parm, cookies=cookies)
                else:
                    res = requests.put(url, headers=headers, data=parm, cookies=cookies)
                res.close()
            except Exception as e:
                logger.error("{1}_put请求_出现异常:{0}".format(e, function_name))
        elif http_method.upper() == "DELETE":
            try:
                logger.info('{2}_发起_delete_请求，url为：{0}，接口传入的参数：{1}'.format(url, parm, function_name))
                res = requests.delete(url, headers=headers)
                res.close()
            except Exception as e:
                logger.error("{1}_发起_delete_请求_出现异常:{0}".format(e, function_name))
        else:
            try:
                logger.info('{2}_发起get请求，url为{0}，接口传入的参数{1}'.format(url, parm, function_name))
                res = requests.get(url, json=parm, cookies=cookies, headers=headers)
                res.close()
            except requests.RequestException as e:
                logger.error("{1}_get请求_出现异常:{0}".format(e, function_name))
        return res

    def http_request_session(self, url, parm, http_method, cookies, headers):
        '''
        通过session发起请求，将发起请求的session保存下来，保持在同一个会话上，用于下一个请求使用，
        :param url: 请求地址
        :param parm: 接口入参参数
        :param http_method: 请求方法 post get 后面有其他再补充
        :param cookies: 可为空
        :param headers: 可为空
        :return:
        '''
        # 创建requests的session 对象
        sess = requests.session()
        if http_method.upper() == 'POST':
            try:
                logger.info("正在使用sesion对象，发起post请求，url为{0},接口传入参数：{1}".format(url, parm))
                res = sess.post(url, parm, cookies=cookies, headers=headers)
            except requests.RequestException as e:
                logger.error("使用session对象，发起post请求出错，报错信息{0}".format(e))
        elif http_method.upper() == 'GET':
            try:
                logger.info("正在使用sesion对象，发起get请求，url为{0},接口传入参数：{1}".format(url, parm))
                res = sess.get(url, cookies=cookies, headers=headers)
            except requests.RequestException as e:
                logger.error("使用session对象，发起get请求出错，报错信息{0}".format(e))
        return res

    def http_request_with_mutipart(self, url, files, http_method, headers=None):
        '''
        定义发起上传文件的接口调用方法，或者接口参数通过multipart/form-data的数据
        1. 请求头格式（看情况是否加上）："Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary11qh303cOdtOvkS3"
        2. 传入参数格式：
        formdata_file = {
        'client_id':(None, 'HKERP2.0'),
        'client_secret':(None, 'ClientKey'),
        'grant_type':(None, 'password'),
        'username':(None, 'testtcl@test01.com'),
        'password':(None, 'e10adc3949ba59abbe56e057f20f883e'),
    }
        :param url:
        :param files:
        :param http_method:
        :param cookies:
        :param headers:
        :return:
        '''
        function_name = communFun.get_function_name()

        # 超时重试
        s = requests.session()
        s.mount("http://", HTTPAdapter(max_retries=3))
        s.mount("https://", HTTPAdapter(max_retries=3))

        if http_method.upper() == "POST":
            try:
                logger.info("{2}_发送POST请求，url为：{0}，接口传入参数：{1}".format(url, files, function_name))
                res = requests.post(url, files=files, headers=headers, timeout=(5, 7))   # todo: 后面调试一下，加上超时时间
                # 将连接关闭
                res.close()
            except requests.RequestException as e:
                logger.error("{1}_发送POST请求，出现异常{0}".format(e, function_name))
        elif http_method.upper() == "GET":
            try:
                logger.info("{1}_发送GET请求，url为：{0}".format(url, function_name))
                res = requests.get(url, files=files, headers=headers)
                res.close()
            except requests.RequestException as e:
                logger.error("{1}_发送GET请求，出现异常{0}".format(e, function_name))
        return res

    def get_token(self):
        '''
        【获取登录的token】调用中台登录接口，获取登录token接口，将接口返回的内容返回，传递给下一个接口使用
        :return: 返回asscess_token的形式[tokenl类型 空格 token值]
        token值：Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkZFNDJCOTg0NDFDMTQ4NDdCQTJENDU2MzkxRThBMDc3QjVFN0MzNTkiLCJ0
        '''
        if Do_Info.env == "test":
            config_url = eval(ConfigRead().read_config(project_path.api_host, 'TESTHOST', 'config'))
        else:
            config_url = eval(ConfigRead().read_config(project_path.demo_api_host, 'TESTHOST', 'config'))

        # 通过md5加密过的密码
        md_pwd = CommunFun().exchange_to_md5(str(config_url["login_pwd"]))
        # 通过form_data传入参数
        formdata_file = {
            'client_id': (None, 'HKERP2.0'),
            'client_secret': (None, 'ClientKey'),
            'grant_type': (None, 'password'),
            'username': (None, str(config_url["login_username"])),
            'password': (None, md_pwd),
            'host': (None, 'https://test-erp.hengkangit.com/#/login')
        }
        res = HttpRequest().http_request_with_mutipart(url=str(config_url["login_token"]), http_method="POST",
                                                       files=formdata_file)
        if res.status_code == 200:
            expires_in = res.json()["expires_in"]
            token_effective_time = int(time.time()) + expires_in   # 调试将这个过期时间改小
            # token_effective_time = int(time.time()) + 0    # 手动调试将这个过期时间改成0
            res_token = res.json()["access_token"]
            token_type = res.json()["token_type"]
            result = token_type + " " + res_token
            DataManage().add_data_obj({"login_token_effective_time": token_effective_time})
        else:
            logger.info("token接口登录失败，获取token失败，请检查{0}".format(res.json()))
            result = False
        return result

    def get_token(self, username, pwd):
        '''
        调用中台登录接口，获取token接口，将接口返回的内容返回，传递给下一个接口使用
        :return: 返回asscess_token的形式[tokenl类型 空格 token值]
        token值：Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkZFNDJCOTg0NDFDMTQ4NDdCQTJENDU2MzkxRThBMDc3QjVFN0MzNTkiLCJ0
        '''
        if Do_Info.env == "test":
            config_url = eval(ConfigRead().read_config(project_path.api_host, 'TESTHOST', 'config'))
        else:
            config_url = eval(ConfigRead().read_config(project_path.demo_api_host, 'TESTHOST', 'config'))

        # 通过md5加密过的密码
        # md_pwd = CommunFun().exchange_to_md5(str(pwd))
        # 通过form_data传入参数
        formdata_file = {
            'client_id': (None, 'HKERP2.0'),
            'client_secret': (None, 'ClientKey'),
            'grant_type': (None, 'password'),
            'username': (None, username),
            'password': (None, pwd),
            'host': (None, 'https://test-erp.hengkangit.com/#/login')
        }
        res = HttpRequest().http_request_with_mutipart(url=str(config_url["login_token"]), http_method="POST",
                                                       files=formdata_file)
        if res.status_code == 200:
            expires_in = res.json()["expires_in"]
            token_effective_time = int(time.time()) + expires_in  # 调试将这个过期时间改小
            # token_effective_time = int(time.time()) + 0    # 手动调试将这个过期时间改成0
            res_token = res.json()["access_token"]
            token_type = res.json()["token_type"]
            result = token_type + " " + res_token
            DataManage().add_data_obj({"login_token_effective_time": token_effective_time})
        else:
            logger.info("token接口登录失败，获取token失败，请检查{0}".format(res.json()))
            result = False
        return result

    def appid_token(self):
        '''
        【获取APPID的鉴权token】默认取配置文件配置的APPID、SecretKey，生成鉴权的token,用于提供给接口，向中台传输数据
        :return: 返回类型为BEARER的header
        '''
        if not hasattr(com_obj, "appid_header"):
            if Do_Info.env == "test":
                config_url = eval(ConfigRead().read_config(project_path.api_host, 'TESTHOST', 'config'))
            else:
                config_url = eval(ConfigRead().read_config(project_path.demo_api_host, 'TESTHOST', 'config'))

            # 通过form_data传入参数
            formdata_file = {
                'appid': (None, config_url["appid"]),
                'secretkey': (None, config_url["secretkey"]),
            }
            res = HttpRequest().http_request_with_mutipart(url=str(config_url["login_token"]), http_method="POST",
                                                           files=formdata_file)
            if res.status_code == 200:
                res_token = res.json()["access_token"]
                token_type = res.json()["token_type"]
                result = token_type + " " + res_token

                header = {"Authorization": result, "Content-Type": "application/json;charset=utf-8"}
                DataManage().add_data_obj({"appid_header": header})
            else:
                logger.info("获取AppId_token失败，请检查{0}".format(res.json()))
                header = False
        else:
            logger.info("AppId_token_header存在_无需重新发起")
            header = com_obj.appid_header
        return header

    def token_is_exist(self, type="memu", module=None):
        '''
        param module: 查找用户登录时，需要查找有指定菜单的用户，进行登录，不传入默认取当前集团和组织下的
        默认先将密码改成1，调用完之后，再将密码改回1
        判断当前是否存在token，如无，则传入账号、密码，调用token接口，生成token,返回header
        '''
        test = com_obj
        if not hasattr(com_obj, "token"):
            # 20220301： 更改查找登录用户，直接取租户数据库的登录用户标识，来登录
            if type == "menu":
                # 查找有此菜单的用户
                user = DoMysql('BAS').get_permission_user(groupid=str(Do_Info.group_id), ouid=str(Do_Info.ou_id),
                                                          module_name=module)
            else:
                # 有此菜单，且有菜单审核权限的用户
                user = DoMysql('BAS').get_had_memu_and_audit_user(groupid=str(Do_Info.group_id), ouid=str(Do_Info.ou_id),
                                                                  module_name=module)

            username = user["identity_code"]
            user_pwd = user["password"]

            # 密码为1的密文
            pwd_1 = "AQAAAAEAACcQAAAAEGyBeIAPPleNIJqZg4cdQbrigosaGTZGzRixwYlLpwduZsY2X9xeWHjZpvETmM1Xqw=="
            DoMysql('BAS').update_user_pwd(userid=user["user_id"], pwd=pwd_1)

            # 对应密码是1的md5明文
            pwd = "c4ca4238a0b923820dcc509a6f75849b"
            token = HttpRequest().get_token(username=username, pwd=pwd)
            DataManage().add_data_obj({"token": token, "displayname": user["display_name"], "userid": user["user_id"]})

            header = {"Authorization": com_obj.token, "Content-Type": "application/json;charset=utf-8"}
            DataManage().add_data_obj({"header": header})
            # 登录成功后，将密码还原为原来的密码
            DoMysql('BAS').update_user_pwd(userid=user["user_id"], pwd=user_pwd)

        else:
            logger.info("token_is_exist_header存在_无需重新发起")
            header = com_obj.header
        return header

    def token_is_effictive(self, type="memu", module=None):
        '''
        【判断当前token是否有效】会判断是否有token的有效时间，若无，则调起生成token接口，若有，则和当前时间比较，若大于token有效时间，则重新获取token
        :param type: 查询用户的类型
        :param module: 具体的菜单
        :return:
        '''
        # com_obj.login_token_effective_time = 1651129017  调试将有效时间改成过期
        now_time = int(time.time())
        if not hasattr(com_obj, "login_token_effective_time"):
            self.token_is_exist(type=type, module=module)
        else:
            # 判断当前时间是否大于token的有效时间
            if now_time > com_obj.login_token_effective_time:
                delattr(com_obj, "token")  # 如果token过期，将过期的token值删掉，重新调起token方法
                self.token_is_exist(type=type, module=module)
            else:
                logger.info("{0}_当前token有效".format(communFun.get_function_name()))

    def auditproduct(self, header):
        '''
        中台审核商品档案的接口的方法
        '''
        # 商品审核的id
        url_s = "https://$host/basicdata/api/services/app/ProductManagement/AuditCheck"
        url = DoReplace().replace_url(url_s)
        param_source = [{"id": "${productid}", "ouId": "${ouid}"}]
        param_t = string.Template(str(param_source))
        param = param_t.safe_substitute(productid=com_obj.create_productid, ouid=Do_Info.ou_id)
        response = self.send_request_json_data(url=url, http_method="POST", parm=eval(param), headers=header)
        # 取返回的内容，判断商品审核是否成功，返回success=TRUE,即为审核通过
        res = CommunFun().get_value_from_json_by_jsonpath(response.json(), "$..success")
        return res

    def auditactivity(self, header):
        '''
        中台审核商品档案的接口的方法
        '''
        # 商品审核的id
        send_url = ["https://$host/market/api/services/app/BundlePomotionManagementAppservice/Send",
                    "https://$host/market/api/services/app/BundlePomotionManagementAppservice/Audit"]
        time = datetime.datetime.now()
        send_parm_s = {"ouId": Do_Info.ou_id, "id": "${create_activityid}", "moduleUrl": "bundledPromotion",
                       "checkResult": 1, "checkNote": "", "createdBy": "${userid}", "checkTime": str(time)}
        param_t = string.Template(str(send_parm_s))
        param = param_t.safe_substitute(create_activityid=com_obj.create_activityid, userid=com_obj.userid)
        # 分别存储送审活动和审核活动的接口，进行送审和审核的操作
        for i in range(len(send_url)):
            url = DoReplace().replace_url(send_url[i])
            response = self.send_request_json_data(url=url, http_method="POST", parm=eval(param), headers=header)
            # 取返回的内容，判断商品审核是否成功，返回success=TRUE,即为审核通过
            logger.info("促销活动审核返回的响应报文_{0}".format(response.json()))
            res = CommunFun().get_value_from_json_by_jsonpath(response.json(), "$..success")
        return res

    def sendrequest_and_assert(self, url, param, method, header, expected_result, assert_type):
        '''
        将发送请求和校验接口返回结果的放到一个方法里面
        '''
        function_name = communFun.get_function_name()
        actualResult = ""
        try:
            res = self.send_request_json_data(url=url, http_method=method, parm=param, headers=header)
            if method.upper() == "PUT":
                res_json = res.text
            else:
                res_json = res.json()
            logger.info("{1}_接口返回的结果是:{0}".format(res_json, function_name))
            assert_res = communFun.get_value_from_json_by_jsonpath(res_json, assert_type)
            actualResult = str(assert_res)
        except Exception as e:
            logger.exception("{1}_接口_发起请求报错_{0}".format(e, function_name))
        try:
            assert str(expected_result) in actualResult
            testresult = 'PASS'
            logger.info('预期结果为：{0},与实际结果是：{1},比对结果：{2}'.format(expected_result, actualResult, testresult))
        except Exception as e:
            testresult = 'Failed'
            logger.error('预期结果：{0},与实际结果{1}, 比对出现了异常, 比对结果{2}'.format(expected_result, actualResult, testresult))
            raise e
        return actualResult, testresult, res


if __name__ == '__main__':
    HttpRequest().token_is_effictive(module="网络订单")
    # time1 = int(time.time())   # 1651129017
    # time2 = time1 + 7200
    # time3 = int(time.time())
    # if time3 > time2:
    #     print('超出时间')
    # else:
    #     print("没有超出时间")
    # print(time1)
    # print(time2)
    # print(time3)
