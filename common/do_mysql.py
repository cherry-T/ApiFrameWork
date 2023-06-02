import string
import time

from common import project_path
from common .read_config import ConfigRead
from common.my_log import MyLog
from common.common_fun import CommunFun
from common.do_info import Do_Info
import random
import pandas as pd
import pymysql
from Common.data_manage import DataManage
from Common.data_manage import com_obj

# 2021031:封装数据库常用的查询，更新（增加、更新、删除方法）
mylog = MyLog()


class DoMysql:
    def __init__(self, database):
        '''
        【初始化函数】必须传入database，来判断读取配置文件那个数据库的配置信息
        :param database: 操作的数据库，如CRM:hk_erp2_crm  BAS:hk_erp2_bas
        return: 返回数据库的配置信息
        '''
        if Do_Info.env == "test":
            self.sql_config = eval(ConfigRead().read_config(project_path.mysql_path, database, 'config'))
        else:
            self.sql_config = eval(ConfigRead().read_config(project_path.demo_mysql_path, database, 'config'))

    def do_mysql(self, sql):
        '''
        调试使用，其他暂未使用
        '''
        print(self.sql_config)
        conn = pymysql.connect(**self.sql_config)  #连接数据
        # 创建游标 操作数据库
        cursor = conn.cursor()
        # 查询  修改成可变的sql语句
        cursor.execute(sql)
        # 获取结果  fetchone()获取单条,返回元组   fetchall()获取多条 ，返回嵌套在列表里的元组   若出错 更改获取数据方式
        res = cursor.fetchall()
        # 关掉游标
        cursor.close()
        # 关闭数据库连接
        cursor.close()
        return res

    def connect_dbserver(self):
        """
        【连接数据库】加上重连机制，出现连接数据库失败的情况，会进行10次的重试，重试连接上之后，退出循环，不在连接
        （20210805换了alsz-polardb-database.mysql.polardb.rds.aliyuncs.com库后，会出现连接数据库超时）
        """
        retry_count = 10
        init_connect_count = 1
        connect_res = True
        while connect_res and init_connect_count < retry_count:
            try:
                self.db = pymysql.connect(**self.sql_config)
                self.cursor = self.db.cursor()
                # 连接上退出循环，连接不上继续重连
                connect_res = False
            except pymysql.Error as e:
                mylog.info("数据库连接失败，第{0}次尝试重连...，错误信息：{1}".format(init_connect_count, e))
                init_connect_count += 1

    def close_cursor(self):
        """
        【关闭数据库连接】关闭游标，关闭数据库（一直不释放，可能会导致数据库服务器占用过高）
         """
        try:
            self.cursor.close()
            # 关闭数据库
            self.db.close()
        except pymysql.Error as e:
            mylog.error("数据库关闭失败：{0}".format(e))

    def get_one(self, sql):
        """
        【查询单条数据】
        sql:查询的sql
        return: 返回一条类型为元祖的数据
        """
        function_name = CommunFun().get_function_name()
        try:
            self.connect_dbserver()
            self.cursor.execute(sql)
            mylog.info("{1}_执行的sql:{0}".format(sql, function_name))

            result = self.cursor.fetchone()
            mylog.info("{1}_查询单条数据_返回的结果_{0}".format(result, function_name))
        except Exception as e:
            mylog.error("{1}_查询sql出现异常:{0}".format(e, function_name))
        finally:
            self.close_cursor()
        return result

    def get_all_data(self, sql):
        '''
        【查询符合要求的数据】
        return: 返回的是元组类型的数据
        '''
        try:
            self.connect_dbserver()
            mylog.info("执行的sql:{0}".format(sql))
            self.cursor.execute(sql)
            # 返回的是元组，可根据需要只查询对应的参数来取参使用
            result = self.cursor.fetchall()
        except Exception as e:
            mylog.error("查询sql出现异常:{0}".format(e))
        finally:
            # 关闭游标，关闭数据库
            self.close_cursor()
        return result

    def get_radom_data(self, sql, function=None):
        '''
        【随机返回查询的数据】查询出所有符合要求的数据，根据查询到tuple的长度，给定随机数范围，随机返回一个数据
        :param sql:查询的sql
        :return: 返回tuple，通过下标进行取值
        '''
        current_function_name = CommunFun().get_function_name()
        try:
            if function is not None:
                mylog.info("{0}_查询数据返回随机结果_sql_{1}".format(function, sql))
            else:
                mylog.info("{0}_查询数据返回随机结果_sql_{1}".format(current_function_name, sql))

            result_data = self.get_all_data(sql)
            max_len = (len(result_data))
            if max_len == 0:
                mylog.error("{0}_根据sql查询无记录".format(current_function_name))
                res = 0
            elif max_len == 1:
                random_id = 0
                res = result_data[random_id]
            else:
                # 查询到的sql数量3条，返回的列表，从0开始，长度相对-1
                max_len = (len(result_data)-1)
                random_id = CommunFun().create_random(0, max_len)
                res = result_data[random_id]
                mylog.info("{2}_获取到查询数据的第{0}条，数据为:{1}".format(random_id, res, current_function_name))
        except Exception as e:
            mylog.error("{1}_查询数据并随机抽取数据出现异常{0}".format(e, current_function_name))
        return res

    def get_data_return_dict(self, sql):
        '''
        【查询符合要求的数据，并以键值对的字典形式返回】结合zip,将对应列名和值压缩成字典
        :param sql:
        :return: 返回列表（列表中嵌套字典）， 可以通过列名/key，进行取值
        '''
        current_function_name = CommunFun().get_function_name()
        try:
            self.connect_dbserver()
            self.cursor.execute(sql)
            res = self.cursor.fetchall()  # 返回的是数组的类型

            # 查出当前查询的列名，保存到coloums
            coloums = [column[0] for column in self.cursor.description]

            # 定义一个数组，用来保存每一组的数组，格式为字典形式{"name":"database","age":18}
            sub_resdata = []
            for row in res:
                # res(1,2,3,4)是数组类型将每行的结果和列名压缩在一起，并转换为字典
                res_data = dict(zip(coloums, row))
                sub_resdata.append(res_data)
        except Exception as e:
            mylog.exception("{1}_查询数据出错，请检查{0}".format(e, current_function_name))
        finally:
            self.close_cursor()
        return sub_resdata

    def get_radom_dict_data(self, sql, function=None):
        '''
        【随机返回查询的数据，格式为字典】
        查询出所有符合要求的数据，返回的是list[dict]，字典类型的值，给定随机数范围，随机返回一个数据
        :param sql:查询的sql
        :param function: 具体哪个查询方法调用get_radom_dict_data
        :return:返回字典，根据列名/key进行取值
        '''
        function_name = CommunFun().get_function_name()
        try:
            if function is not None:
                function_name = function
            else:
                function_name = function_name
            mylog.info("{0}_执行的sql_{1}:".format(function_name, sql))

            result_data = self.get_data_return_dict(sql)
            max_len = (len(result_data))
            if max_len == 0:
                mylog.error("{1}_查询sql查询无记录:{0}".format(sql, function_name))
                res = max_len
            elif max_len == 1:
                random_id = 0
                res = result_data[random_id]
                mylog.info("{2}_获取到查询数据的第{0}条，数据为:{1}".format(random_id, res, function_name))
            else:
                # 查询到的sql数量3条，返回的列表，从0开始，长度相对-1
                max_len = (len(result_data)-1)
                random_id = CommunFun().create_random(0, max_len)
                res = result_data[random_id]
                mylog.info("{2}_获取到查询数据的第{0}条，数据为:{1}".format(random_id, res, function_name))
        except Exception as e:
            mylog.error("{2}_查询数据_{0}_出现异常{1}".format(sql, e, function_name))
            raise e
        return res

    def edit_data(self, sql, function=None):
        """
        【编辑数据】更新数据库操作，包含更新、增加、删除
        sql:操作的sql语句
       """
        result = 1
        current_function_name = CommunFun().get_function_name()  # 当前方法的名称
        try:
            self.connect_dbserver()
            if function is not None:
                mylog.info("{0}_更新数据_执行sql_{1}".format(function, sql))
            else:
                mylog.info("{1}_执行sql_{0}".format(sql, current_function_name))
            self.cursor.execute(sql)
            # 注意的是，如果是对数据库做了修改、删除、增加的操作，那么一定要commit提交，查询和创建表不需要提交
            self.db.commit()
        # 如果操作失败，报出操作异常，且游标进行回滚
        except Exception as e:
            mylog.error("{0}_更新数据库出错：{1}".format(current_function_name, e))
            result = 0
            self.db.rollback()
        finally:
            self.close_cursor()
        return result

    def update_isdelete(self, memberid, isdelete=0):
        '''
        更新用户
        :param memberid: 会员id，isdelete=0,默认是0，即未删除，传入1，即更新为已删除
        :return:
        '''
        if isdelete == 0:
            update_sql = "update user t set t.is_deleted=0 where t.id='"+memberid+"'"
        else:
            update_sql = "update user t set t.is_deleted=1 where t.id='" + memberid + "'"
        res = self.edit_data(update_sql)
        current_function_name = CommunFun().get_function_name()
        if res == 1:
            if isdelete == 0:
                mylog.info("{0}_更新用户为未删除状态".format(current_function_name))
            else:
                mylog.info("{0}_更新用户为删除状态".format(current_function_name))
        else:
            res = 0
            mylog.error("{0}_更新用户为未删除状态失败".format(current_function_name))
        return res

    def get_user(self, groupid, ouid, is_manual=False):
        '''
        【查询是否为手工新增的其它出库单】
        :param groupid:
        :param ouid:
        :param is_manual:
        :return:
        '''
        sql = "select t.id,t.bill_code,t.sbill_no,t.out_stock_id,t.qty from user t where " \
              "t.group_id='"+str(groupid)+"' and t.out_ou_id='"+str(ouid)+"'"

        if is_manual:
            sql = sql + " and t.no !='' "  # 有其它申请出库单的单号
        else:
            sql = sql + " and t.no ='' "

        sql = sql + " order by t.created_time desc limit 5"

        res = self.get_radom_dict_data(sql=sql, function=CommunFun().get_function_name())
        return res

if __name__ == '__main__':
    res = DoMysql('OMS').get_oms_all_channel_order_info(trans_code="5000000044785601")
    print(res)










