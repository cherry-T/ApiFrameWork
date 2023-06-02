# -*- coding: utf-8 -*-
# @Time: 2022/8/11 13:54
# @Author: tangcl
# @Desc:  文件用于
import pymysql
import random
from commons.log_print import LogPrint

logger = LogPrint().logger
# todo: 数据库的配置信息，是从测试环境中获取，然后进行连接数据库，操作数据库
# todo: 中台数据库，地址相同，只有数据库名称不同


class DoMysql:
    instance = None

    def __init__(self, database: dict):
        '''
        【初始化函数】必须传入database，来判断读取配置文件那个数据库的配置信息
        :param database: 操作的数据库，如CRM:hk_erp2_crm  BAS:hk_erp2_bas
        return: 返回数据库的配置信息
        '''
        # self.sql_config = eval(ConfigRead().read_config(project_path.mysql_path, database, 'config'))
        self.sql_config = database

    def __new__(cls, *args, **kwargs):
        '''
        【重写__new__：设计单例模式，不用重复创建实例，减少内存资源浪费】
        '''
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

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
                logger.info("数据库连接失败，第{0}次尝试重连...，错误信息：{1}".format(init_connect_count, e))
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
            logger.error("数据库关闭失败：{0}".format(e))

    def edit_data(self, sql):
        """
        sql:操作的sql语句
        更新数据库操作，包含更新、增加、删除
       """
        result = 1
        try:
            self.connect_dbserver()
            logger.info("更新sql的语句：" + sql)
            self.cursor.execute(sql)
            # 注意的是，如果是对数据库做了修改、删除、增加的操作，那么一定要commit提交，查询和创建表不需要提交
            self.db.commit()
        # 如果操作失败，报出操作异常，且游标进行回滚
        except Exception as e:
            print("更新数据库出错：", e)
            result = 0
            self.db.rollback()
        finally:
            self.close_cursor()
        return result

    def get_one(self, sql):
        """
        【查询单条数据】
        sql:查询的sql
        return: 返回一条类型为元祖的数据
        """
        try:
            self.connect_dbserver()
            self.cursor.execute(sql)
            logger.info("执行的sql:{0}".format(sql))

            result = self.cursor.fetchone()
            logger.info("查询单条数据_返回的结果_{0}".format(result))
        except Exception as e:
            logger.error("查询sql出现异常:{0}".format(e))
            result = 0
        finally:
            self.close_cursor()
        return result

    def get_data_return_dict(self, sql):
        '''
        【查询符合要求的数据，并以键值对的字典形式返回】结合zip,将对应列名和值压缩成字典
        :param sql:
        :return: 返回列表（列表中嵌套字典）list[dict{}]， 可以通过列名/key，进行取值
        '''
        try:
            self.connect_dbserver()
            self.cursor.execute(sql)
            res = self.cursor.fetchall()  # 返回的是数组的类型

            coloums = []
            for column in self.cursor.description:
                coloums.append(column[0])

            sub_resdata = []
            for row in res:
                # 将列名和具体每列的值压缩为dict类型
                res_data = dict(zip(coloums, row))
                sub_resdata.append(res_data)
        except Exception as e:
            logger.exception("查询数据出错，请检查{0}".format(e))
            sub_resdata = 0
        finally:
            self.close_cursor()
        return sub_resdata

    def get_random_dict_data(self, sql):
        '''
        【随机返回查询的数据，格式为字典】
        查询出所有符合要求的数据，返回的是list[dict]，字典类型的值，给定随机数范围，随机返回一个数据
        :param sql:查询的sql
        :return:返回字典，根据列名/key进行取值
        '''
        try:
            result_data = self.get_data_return_dict(sql)
            logger.info("执行的sql_{0}:".format(sql))
            max_len = (len(result_data))
            if max_len == 0:
                logger.error("查询sql查询无记录:{0}".format(sql))
                res = max_len
            elif max_len == 1:
                random_id = 0
                res = result_data[random_id]
                logger.info("获取到查询数据的第{0}条，数据为:{1}".format(random_id, res))
            else:
                # 查询到的sql数量3条，返回的列表，从0开始，长度相对-1
                max_len = (len(result_data)-1)

                # 随机抽取符合要求中的一条数据
                random_id = random.randint(0, max_len)
                res = result_data[random_id]
                logger.info("获取到查询数据的第{0}条，数据为:{1}".format(random_id, res))
        except Exception as e:
            logger.error("查询数据_{0}_出现异常{1}".format(sql, e))
            raise e
        return res

    def get_permission_user(self, groupid, is_permission=True, ouid=None, module_name=None):
        '''
        【查找有权限的用户】传入具体的模块，根据模块查找由此模块或菜单权限的用户
        param :传入module_name：中台菜单模块的名称，如订单、零售等，查询具有此菜单名称的用户
        param is_permission: 是否有权限，True代表权限 False：则无权限
        identity_code: 查询到这个参数就是登录的账号
        '''
        sql = "select d.user_id,g.identity_code,e.user_code,a.role_id,c.role_code,e.group_id,f.group_code,e.ou_id," \
              " e.display_name, e.password, a.id, a.moudle_id,b.module_name,a.is_browse from " \
              " hk_erp2_bas.sys_browse_permissions a,hk_erp2_bas.sys_modules b,hk_erp2_bas.scy_role c," \
              " hk_erp2_bas.scy_user_role d,hk_erp2_bas.scy_user e,hk_erp2_bas.bas_group f, " \
              " hk_erp2_tenant.glo_user_identity g where a.moudle_id=b.id and a.role_id=c.id and d.role_id=c.id " \
              " and d.user_id=e.id and  e.group_id=f.id and e.id=g.scy_user_id and b.status=1 and e.status=1  " \
              " and g.status=1 and e.user_type=1 and b.is_deleted=0  and c.is_deleted=0 and e.is_deleted=0 " \
              " and f.is_deleted=0 and e.group_id='" + str(groupid) + "'"
        if ouid is not None:
            sql = sql + " and e.ou_id='" + str(ouid) + "'"
        if module_name is not None:
            sql = sql + " and b.module_name='" + str(module_name) + "'"

        if is_permission:
            sql = sql + " and a.is_browse=1 limit 100 "
        else:
            sql = sql + " and a.is_browse=0 limit 100 "

        res = self.get_random_dict_data(sql=sql)
        return res

    def get_login_user(self, param=None):
        '''
        【查找可以登录中台的用户】：后期可以根据需要，进行拓展，其中identity_code为登录账号
        :param: param：传进来的参数
        :return:
        '''
        select_sql = "SELECT g.identity_code,t.group_id,c.group_code,c.group_fullname as group_name,t.ou_id, d.ou_name," \
                     " d.ou_fullname, e.ou_fullpath_name as bas_ouname,e.ou_parentid,t.id as user_id, t.user_code," \
                     " f.url as login_group, t.phone_number,t.password,t.modified_by," \
                     " a.role_id, b.display_name from hk_erp2_bas.scy_user t, hk_erp2_bas.scy_user_role a, " \
                     " hk_erp2_bas.scy_role b,hk_erp2_bas.bas_group c, hk_erp2_bas.bas_ou d," \
                     " hk_erp2_bas.bas_business e,hk_erp2_tenant.bas_group f,hk_erp2_tenant.glo_user_identity g," \
                     " hk_erp2_tenant.glo_tenant h,hk_erp2_bas.bas_mbou i where t.id = a.user_id and a.role_id=b.id " \
                     " and e.ou_id=t.ou_id and t.group_id = c.id and t.ou_id = d.id and t.group_id=f.id" \
                     " and h.group_id=t.group_id and i.ou_id=d.id and i.status=1 and h.status=1 and " \
                     " t.id = g.scy_user_id and c.is_deleted= '0' and d.is_deleted='0' and t.is_deleted = '0' " \
                     " and b.is_deleted='0' and t.status=1 and t.user_type='1' and g.status=1 and t.employee_id=0 " \
                     " and t.is_app=0 and t.effective_start!='3000-12-31 00:00:00' "
                     # " and t.user_code='tangcl' "  # 20211214 先固定查找这个用户
        if param is not None:
            if isinstance(param, dict):
                if "scenario" in param:
                    if param["scenario"] == "first_login_pos":
                        # 零售模块：没有设置过pos设置的用户
                        select_sql = select_sql + " and t.modified_by not in(SELECT d.modified_by from " \
                                                  " hk_erp2_sd.sd_pos_config d  where d.is_deleted=0)"
                elif "group_id" in param:
                    select_sql = select_sql + " and t.group_id='"+param["group_id"]+"'"
                elif "ou_id" in param:
                    select_sql = select_sql + " and t.ou_id='"+param["ou_id"]+"'"
                else:
                    logger.exception("get_login_user_传入的参数非字典类型，请检查")

        select_sql = select_sql + " limit 50"

        res = self.get_random_dict_data(select_sql)
        return res

    def get_bas_shop(self, groupid, ouid=None, shopname=None):
        '''
        【查找启用且未删除的店铺的基本信息】
        :param groupid: 集团
        :param ouid: 组织
        :return: 返回符合要求的数据，并以字典形式返回
        '''
        select_sql = "select t.shop_name,t.shop_fullname,t.id as shop_id,t.op_area_id from hk_erp2_bas.bas_shop t " \
                     " where t.group_id='"+str(groupid)+"' and t.status=1 and t.is_deleted=0 "
        if ouid is not None:
            select_sql = select_sql + " and t.ou_id='"+str(ouid)+"' "
        if shopname is not None:
            select_sql = select_sql + " and t.shop_name like '%"+shopname+"%' "

        res = self.get_random_dict_data(sql=select_sql)
        return res

    def update_member_status(self, cardcode, scene="正常"):
        '''
        [根据传入场景更新会员状态]
        :param cardcode: 会员卡号/会员手机号
        :param scene: 场景：正常、挂失
        :return:
        '''
        if scene == "挂失":
            status = '2'
        elif scene == "冻结":
            status = '3'
        elif scene == "停用":
            status = '4'
        elif scene == "过期":
            status = '6'
        else:
            # 其他场景，更新为正常
            status = '1'

        sql = "update hk_erp2_crm.crm_member t set t.status='"+status+"' WHERE t.card_code='"+str(cardcode)+"' or " \
              " t.moblie='"+str(cardcode)+"'"
        res = self.edit_data(sql)
        return res

    def get_member_integral(self, crm_id):
        '''
        【获得指定会员的积分】
        :param crm_id: crm会员id
        '''
        select_sql = "select b.integral,b.integral_total from hk_erp2_crm.crm_member_integral b where b.member_id='"+str(crm_id)+"'"
        res = self.get_random_dict_data(select_sql)
        return res

    def get_member_by_cardcode(self, cardcode):
        '''
        【通过会员卡号获取会员信息】
        '''
        sql = "select t.id,t.card_code,t.moblie,t.phone,t.member_name,t.idcard_no,t.grade_id from hk_erp2_crm.crm_member" \
              " t where t.card_code='"+str(cardcode)+"' or t.moblie='"+ str(cardcode)+"'"
        res = self.get_random_dict_data(sql)
        return res

    def get_member_info(self, group_id, ou_id):
        '''
        [根据集团和组织查询会员信息]
        '''
        sql = "select t.id,t.card_code,t.moblie,t.phone,t.member_name,t.idcard_no,t.grade_id from " \
              " hk_erp2_crm.crm_member t where t.group_id='"+str(group_id)+"' and t.ou_id='"+str(ou_id)+"' "\
              " and t.status=1 and t.is_deleted=0"
        res = self.get_random_dict_data(sql)
        return res

    def get_member_growth(self, crm_id):
        '''
        【查询会员成长值】
         :param crm_id: crm会员id
        '''
        sql = "SELECT t.growth_value,t.growth_value_total from hk_erp2_crm.crm_member_growth t where " \
              " t.member_id='"+str(crm_id)+"'"
        res = self.get_random_dict_data(sql)
        return res

    def update_user_pwd(self, userid, pwd):
        '''
        [更新登录用户密码]
        :param userid: hk_erp2_bas.scy_user:表的用户id
        :param pwd: 密码的密文
        :return:
        '''
        sql = "update hk_erp2_bas.scy_user t set t.password='"+pwd+"' where t.id='"+str(userid)+"'"

        res = self.edit_data(sql)
        if res == 1:
            logger.info("还原用户密码成功".format(userid))
        else:
            logger.exception("还原用户密码失败".format(userid))

    def update_user_fixedpwd(self, userid):
        '''
        [更新用户密码为123]
        :param userid: hk_erp2_bas.scy_user:表的用户id
        :return:
        '''
        sql = "update hk_erp2_bas.scy_user t set  " \
              " t.password='AQAAAAEAACcQAAAAEK6Yn+EugVJumIIDtUNZk0NCg6SeOpueFyWbCkCjzDgRonH5d2yrxZKAGorhTzlVFw==' " \
              " where t.id='"+str(userid)+"'"

        res = self.edit_data(sql)
        if res == 1:
            logger.info("更新用户{0}，密码为123".format(userid))
        else:
            logger.exception("更新用户{0}，密码为123失败".format(userid))
        return res

    def get_skucode_is_mapping(self, groupid, ouid, shopid, online_sku_code):
        '''
        【传入指定的商品编码，查询是否已关联，已做了商品对应】
        :param groupid:  集团
        :param ouid: 组织
        :param shopid: 店铺
        :param online_sku_code: 商家编码
        :return:
        '''
        sql = "select t.online_sku_id,t.is_mapping from hk_erp2_oms.oms_product_mapping t where " \
              " t.group_id='"+str(groupid)+"' and t.ou_id='"+str(ouid)+"' and t.shop_id='"+str(shopid)+"' " \
              " and t.is_deleted=0 and t.online_sku_code='"+str(online_sku_code)+"' and t.is_mapping=1 and t.online_sku_id!=''"
        res = self.get_random_dict_data(sql=sql)
        return res


if __name__ == '__main__':
    sql = "select * from kdt_test.element_properties t"
    res = DoMysql('KDT').get_random_dict_data(sql)
    print(res)