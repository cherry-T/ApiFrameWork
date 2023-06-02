# -*- coding: utf-8 -*-
import datetime
import random
from time import time
import jsonpath
import json
from common.my_log import MyLog
import hashlib
from hashlib import md5
from string import ascii_letters,digits,printable,punctuation
from itertools import permutations,product
from decimal import Decimal
from string import Template
from common.do_info import Do_Info
import re
import ast
import inspect
import string

mylog = MyLog()
# 定义公共类方法


class CommunFun:
    def create_memberId(self):
        '''
        生成0~9 的 9位随机数
        :return:
        '''
        member_id = str(random.randint(0, 99999999)).zfill(9)
        # print(member_id)
        return member_id

    def create_memberId(self, length):
        '''
        生成0~9 的 9位随机数
        :return:
        '''
        member_id = str(random.randint(0, 99999999)).zfill(length)
        # print(member_id)
        return member_id

    def create_mobile(self):
        '''
        随机生成手机号的种子seed
        :return:
        '''
        prelist = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
                   "147", "150", "151", "152", "153", "155", "156", "157", "158", "159",
                   "186", "187", "188", "189"]
        # 随机选择区号 + 字符拼接，随机从0~9的数字，循环8次，补充剩下的8位手机号码
        mobile = random.choice(prelist) + "".join(random.choice("0123456789") for i in range(8))
        # print(mobile)
        return mobile

    def create_random(self, start, end):
        id = random.randint(start, end)
        return id

    def create_unionid(self):
        '''
        随机的unionid 粉丝微信唯一标识(与开发逻辑代码不一样)
        生成28位随机的unionid 粉丝微信唯一标识(与开发逻辑代码不一样)
        拼团开团 和 加入团队的时候，会用到，目前接口没有校验unionid是否符合逻辑要求
        :return:
        '''
        seed = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        unionid = []
        for i in range(28):
            # 给定的随机种子里面，随机抽取，添加到列表
            unionid.append(random.choice(seed))
        # 将列表转化为字符串
        res = ''.join(unionid)
        # print(res)
        return res

    def create_bill_no(self):
        '''
        用于生成提交消费单的bill_no/sbill_No：可随机生成
        :return: 返回带当天年-月-日 + 加上三位随机数的消费单号
        '''
        today = datetime.date.today()
        if today.month < 10:
            month = '0'+str(today.month)
        else:
            month = str(today.month)
        if today.day < 10:
            day = '0'+str(today.day)
        else:
            day = str(today.day)
        # 获取当前日期格式： 20210603
        date = str(today.year) + month + day
        seed = '1234567890'
        bill_no = []
        for i in range(3):
            bill_no.append(random.choice(seed))
        res = date + ''.join(bill_no)
        # print(res)
        return res

    def create_bill_code(self):
        '''
        用于生成提交消费单的bill_no/sbill_No：可随机生成
        :return: 返回带当天年-月-日 + 加上三位随机数的消费单号
        '''
        today = datetime.date.today()
        if today.month < 10:
            month = '0'+str(today.month)
        else:
            month = str(today.month)
        if today.day < 10:
            day = '0'+str(today.day)
        else:
            day = str(today.day)
        # 获取当前日期格式： 20210603
        date = str(today.year) + month + day
        seed = '1234567890'
        bill_no = []
        for i in range(3):
            bill_no.append(random.choice(seed))
        res = date + '-' + ''.join(bill_no)
        # print(res)
        return res

    def get_value_from_json_by_jsonpath(self, jsonstr, path):
        '''
        从json串中，通过给定jsonpath的取值路径，取指定的值
        :param jsonstr: 接口的响应报文，或者是json格式的数据
        :param path: jsonpath的取值路径 （$..isSuccess）
        :return: 返回列表类型，通过下标取值
        '''
        # 看实际接口返回的对象，是不是json字符串
        # 加载json字符串为json对象
        if type(jsonstr) == str:
            jsonstr = json.loads(jsonstr)
        # 使用jsonpath模块的jsonpath方法提取信息
        try:
            result = jsonpath.jsonpath(jsonstr, path)
        except Exception as e:
            mylog.error("通过jsonpath提取接口返回的值出错，请检查{0}".format(e))
        # print(type(result))
        # print(result)
        return result

    def get_value_from_multiple_result(self, res_json, res_key, path):
        '''
        【循环遍历取多层的指定的jsonpath的值】
        接口返回结果，result包含多层时，分别取多层中的指定的key:如[result:0{res:""} 1{res:""}]
        如：零售促销，购买多个商品，涉及促销活动，促销接口会分别返回各个商品的result结果，拿到对应的payamount，返回比对结果
        :param res_json:  json
        :param res_key:   要取值最外层的key名
        :param path:  jsonpath路径
        :return: 返回多层取出的jsonpath的值的和，并返回字符串
        '''
        # 加载json字符串为json对象
        try:
            if type(res_json) == str:
                res_json = json.loads(res_json)
            sum_payment = 0
            for i in res_json[res_key]:
                # i为result返回的第一部分的内容
                pay_ment = jsonpath.jsonpath(i, path)
                # float(payment[0]): 计算机进行浮点运算时的浮点误差，改用decimal，decimal(只能传入int和str,不能传float)
                res_payment = Decimal(str(pay_ment[0]))
                sum_payment += res_payment
            sum_payment = CommunFun().decimal_round(sum_payment, '2')
            return str(sum_payment)
        except Exception as e:
            mylog.error("get_value_from_multiple_result_通过jsonpath多层遍历取值出错，请检查{0}".format(e))

    def exchange_to_md5(self, password):
        '''
        【md5加密】传入内容进行md5加密
        如：中台登录接口connect/token，需要md5加密后的密码
        :param password: 密码
        :return: 返回加密后的密码
        '''
        # 创建md5对象
        md_obj = hashlib.md5()
        # 传入信息进行加密，注意传入的信息必须进行encode编码，否则报错
        md_obj.update(password.encode("utf-8"))
        # 获取加密后的信息
        md_res = md_obj.hexdigest()
        return md_res

    def decrypt_md5(self, md5_value):
        '''
        通过给定的密码组成的部分，拿出来做md5转换，如果当前转换的md5等于传进来的md5,即返回密码明文
        密码较复杂时，比对的时间会比较长
        todo: 现在密码长度不固定，具体的密码输入的值不确定；看下密码长度能不能确定，还有输入的类型
        '''
        all_letter = ascii_letters+digits+punctuation  # 字母，换成数字
        # all_letter = ascii_letters+digits+'.,;'  # 字母，换成数字
        # all_letter = printable
        if len(md5_value) != 32:
            mylog.error("error")
        md5_value = md5_value.lower()
        for i in range(1, 10):   # 这里定义密码的长度,循环遍历，长度会不断增加到10，
            for item in permutations(all_letter, i):
                item = ''.join(item)
                # print('.', end='')
                # item = '123'
                if md5(item.encode()).hexdigest() == md5_value:
                    return item

    def decimal_round(self, number, len='2'):
        '''
        四舍五入方法，decimal模块的quantize()方法实现，rounding的模式不同，最后四舍五入的值不一样
        如:3902.145,如果不给定rounding,最后返回3902.14，指定raounding=ROUND_HALF_UP,最后返回3902.15
        python自带round默认四舍六入
        :param number: 数值
        :param len: 保留多少位小数,传到方法做decimal对应保留的小数位格式转换
        :return:
        '''
        if len == '1':
            len_model = '0.0'
        elif len == '2':
            len_model = '0.00'
        elif len == '3':
            len_model = '0.000'
        elif len == '4':
            len_model = '0.0000'
        else:
            len_model = '0.00'
        try:
            result = Decimal(number).quantize(Decimal(len_model), rounding="ROUND_HALF_UP")
            return result
        except Exception as e:
            mylog.exception("decimal_round_四舍五入方法出错，请检查{0}".format(e))

    def getdata_by_business(self, business_scenario, test_data):
        '''
        根据传进来的业务场景，筛选符合条件的数据，放到字典里面，返回使用
        :param business_scenario: 业务场景，和excel的function保持一致
        :param test_data: 测试数据
        :return:
        '''
        bus_data = []

        for i in test_data:
            if i["function"] == business_scenario:
                bus_sub_data = {}
                bus_sub_data['id'] = i["id"]
                bus_sub_data['module'] = i['module']
                bus_sub_data['function'] = i['function']
                bus_sub_data['title'] = i['title']
                bus_sub_data['http_method'] = i['http_method']
                bus_sub_data['url'] = i['url']
                bus_sub_data['parm'] = i['parm']
                bus_sub_data['assertType'] = i['assertType']
                bus_sub_data['ExpectedResult'] = i['ExpectedResult']
                # 将字典添加到列表
                bus_data.append(bus_sub_data)
        return bus_data

    def replace_by_stringTemple(self, param, temple):
        '''
        通过string模块的temple，模板替换参数
        :param param: 要替换的参数，temple模板默认带“$”的进行替换
        :param temple: 替换的模板，通常以字典传入
        :return:
        '''
        if param != "" and temple != "":
            try:
                # substitute: 参数没有全部替换，会发生异常；safe_substitute()安全替换，只替换存在的字典值
                result = Template(param).safe_substitute(temple)  # 安全替换，遇到需要替换的才替换，其他的不进行替换
            except Exception as e:
                mylog.exception("replace_by_stringTemple_模板替换参数失败,请检查{0}".format(e))
        else:
            mylog.exception("replace_by_stringTemple_模板替换参数，参数为空，请检查")
        return result

    def dynamic_create_dict(self, param):
        '''
        根据传入的数据，如果数据包含【$】,则取其key创建成新的字典，和replace_by_stringTemple一起使用，可动态替换参数
        :param param: 数据
        :return: 字典
        '''
        param_dict = {}
        if isinstance(param, str):
            param = eval(param)  # 将字符串转化成字典
            if isinstance(param, list):
                param = param[0]  # 如果参数是列表，直接取第一个参数[{"id":1}]
        for key, values in param.items():
            # 如果里面继续嵌套了字典,判断values值为列表，继续往下循环遍历字典
            pattern = "[{](.*?)[}]"
            try:
                if isinstance(values, list):
                    for i in values:
                        # print(i)
                        # print(type(i))
                        if isinstance(i, dict):
                            for ikey, ivalues in i.items():
                                if str(ivalues).find("$") != -1:
                                    key = CommunFun().re_matchReg_getdata(ivalues, pattern)
                                    key_v = key[0]
                                    param_dict[key_v] = ""
                        elif isinstance(i, str):
                            if str(i).find("$") != -1:
                                key = CommunFun().re_matchReg_getdata(str(i), pattern)
                                key_v = key[0]
                                param_dict[key_v] = ""
                elif isinstance(values, str) or isinstance(values, float) or isinstance(values,int):
                    # 先判断类型是否为字符(普通字符判断eval()字典的时候，经常报错，导致取不到要替换的字符)
                    if isinstance(values,float) or isinstance(values,int):
                        values = str(values)
                    if str(values).find("$") != -1:
                        key = CommunFun().re_matchReg_getdata(values, pattern)
                        for istr in range(len(key)):
                            key_v = key[istr]
                            param_dict[key_v] = ""
                elif isinstance(ast.literal_eval(values), dict):
                    # 判断values是字典，按字典取值，如果字典values值还嵌套了[{继续往下判断取值}]
                    values = eval(values)
                    for ikey, ivalues in values.items():
                        if isinstance(ivalues, list):
                            for s in ivalues:
                                if isinstance(s, dict):
                                    for skey, svalus in s.items():
                                        if str(svalus).find("$") != -1:
                                            key = CommunFun().re_matchReg_getdata(svalus, pattern)
                                            key_v = key[0]
                                            param_dict[key_v] = ""
                        else:
                            if str(ivalues).find("$") != -1:
                                key = CommunFun().re_matchReg_getdata(ivalues, pattern)
                                key_v = key[0]
                                param_dict[key_v] = ""
                else:
                    if str(values).find("$") != -1:
                        key = CommunFun().re_matchReg_getdata(values, pattern)
                        key_v = key[0]
                        param_dict[key_v] = ""
            except Exception as e:
                continue
                # mylog.info("pass:{0}".format(e))
        # print(param_dict)
        return param_dict

    def can_recharge_dict(self,param):
        '''
        判断传入的参数，是否可以在eval（）转换成对应类型：字典 list等，如果单个字符串eval()，会报无效语法
        方法主要为了不让异常抛出，可以继续执行下去
        '''
        try:
            eval(param)
            res = True
        except Exception as e:
            res = False
        return res

    def re_matchReg_getdata(self, param, pattern):
        '''
        通过正则表达式，提取需要的内容
        :param param: 传入的数据
        :param pattern: 正则表达式，提取数据的规则，[{](.*?)[}]：提取{}括号内的内容
        :return: 返回列表
        '''
        dict_res = self.can_recharge_dict(param)
        if dict_res:
            data = eval(param)
            # print(type(data))
            pattern = re.compile(pattern)
            list_result = []
            for i in data:
                try:
                    result = re.findall(pattern, str(data[i]))
                    # print(result[0])
                    # 每次根据正则匹配，会返回一个列表，如果有符合的，返回列表有值，否则，为空，判断长度为空时，不加到结果list
                    if result:
                        list_result.append(result[0])
                except Exception as e:
                    mylog.error("输出异常e:{0}".format(e))
        else:
            pattern = re.compile(pattern)
            list_result = re.findall(pattern, param)

        return list_result


    def re_matchReg_getdata_1222(self, param, pattern):
        '''
        通过正则表达式，提取需要的内容
        :param param: 传入的数据
        :param pattern: 正则表达式，提取数据的规则，[{](.*?)[}]：提取{}括号内的内容
        :return: 返回列表
        '''
        print(param)
        if isinstance(eval(param), str):
            pattern = re.compile(pattern)
            list_result = re.findall(pattern, param)
        elif isinstance(eval(param),dict):
            data = eval(param)
            # print(type(data))
            pattern = re.compile(pattern)
            list_result = []
            for i in data:
                try:
                    result = re.findall(pattern, str(data[i]))
                # print(result[0])
                # 每次根据正则匹配，会返回一个列表，如果有符合的，返回列表有值，否则，为空，判断长度为空时，不加到结果list
                    if result:
                        list_result.append(result[0])
                except Exception as e:
                    mylog.error("输出异常e:{0}".format(e))
        else:
            mylog.info("非字符和字典类型，不进行正则提取")
        return list_result

    def assert_qty_is_equal(self, expect_qty, qty):
        '''
        比较两个数是否相等
        '''
        try:
            assert int(expect_qty) == int(qty)
            res = True
        except Exception as e:
            mylog.info("assert_qty_is_equal_{0}和{1}不等_检查{2}".format(expect_qty, qty, e))
            res = False
        return res

    def create_shopnc_order_sn(self, order_sn, length: int):
        '''
        【生成商城订单号】 取当前系统最新订单的订单号（16位），取前14位进行自增（50000000444998），后2位用'01'补全
        :param order_sn: 商城的订单号：5000000044499801
        :param length: 长度，即需要返回多少个新的订单号
        :return: 返回列表[5000000044499901,5000000044500001...]
        '''
        order_sn = str(order_sn)[:-2]
        list_res = []

        for i in range(length):
            order_sn = int(order_sn) + 1
            new_order_sn = str(order_sn) + '01'
            list_res.append(int(new_order_sn))
        return list_res

    def create_shopnc_pay_sn(self, pay_sn, memberid, length: int):
        '''
        【生成商城支付单号】 取当前系统最新订单的订单号（18位），取前15位进行自增（50000000444998），后3位为用户id的后三位
        :param order_sn: 商城的支付订单号：430702210717278358（前面15位规则不详，暂且自增）
        :param length: 长度，即需要返回多少个新的订单号
        :return: 返回列表[5000000044499901,5000000044500001...]
        '''
        pay_sn = str(pay_sn)[:-3]
        last_thrid_mebid = str(memberid)[-3:]
        list_res = []

        for i in range(length):
            pay_sn = int(pay_sn) + 1
            new_pay_sn = str(pay_sn) + last_thrid_mebid
            list_res.append(int(new_pay_sn))
        return list_res

    def get_function_name(self):
        '''
        【获取当前执行的函数的名称】 test里面调用get_funciton_name,获取的是当前执行方法的名字
        inspect.stack()[0][3]:当前方法名、inspect.stack()[1][3]:调用方法名
        :return: 返回函数的名称，inspect.stack()返回列表，列表子项为元祖形式
        '''
        function_name = inspect.stack()[1][3]
        # function_name = inspect.stack()[0][3]
        return function_name

    def change_dit_into_int(self, parm):
        '''
        【将bit类型的数据转化成int】
         bit类型数据[b'\x00'], 转化成int的[0]
        :param parm: 需要转化的bit类型的数据
        :return: int
        '''
        res = ord(parm)
        return res

    def get_time_now(self):
        '''
        【返回当前的时间，具体到年月日 时分秒】
        :return:
        '''
        res = datetime.datetime.now()
        return res

    def get_date(self):
        '''
        【返回当前的日期】具体的年-月-日
        :return:
        '''
        res = datetime.date.today()
        return res

    def replace_string(self, param_source, param_dict: dict):
        '''
        【动态替换字符串参数】替换原理：通过string模板，判断带[$]为需要替换的值，传入和带[$]名称一样的实际替换的值，替换带[$]的参数
        如 param_source: {"id": ${id}, "class": "一班"}  param_dict: {"id":1} 最终替换结果= {"id": 1, "class": "一班"}
        :param param_source: 原始的带$的字符串，即需动态替换的参数
        :param param_dict:  进行替换的数据，字典类型
        :return:
        '''
        param_temple = string.Template(str(param_source))
        param = param_temple.safe_substitute(param_dict)  # 可传入单个指定的key的值/传入dict
        return param

if __name__ == '__main__':
    # res = CommunFun().dynamic_create_dict([{"id":"${send_coupon_id}","ouId":"${ouid}"}])
    # res = CommunFun().create_memberId(length=10)
    # res = CommunFun().create_memberId(length=10)
    # test = CommunFun().create_shopnc_pay_sn(length=1, pay_sn=430702210717278358, memberid='22200358')
    # test = CommunFun().exchange_to_md5('1')   # b'\x00'
    test1 = {"id": "${id}", "class": "一班"}
    data = {"id": 1}
    test = CommunFun().replace_string(param_source=test1, param_dict=data)
    print(test)
    # res = test + '358'
    # import time
    # time1 = time.time()
    # res2 = str(time1) + '358'
    # print(res)
    # print(res2)






