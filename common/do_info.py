__author__ = 'Tangcl'
__qq__ = '1334518618'

from openpyxl import load_workbook
from common import project_path


class Do_Info:
    # 根据配置的env，取不同的配置数据，包括hosts、登录账号、数据库信息
    # todo: test为测试环境 demo为演示环境，影响到接口取域名和数据库取对应的地址
    env = "test"
    # groupid 通过反射保存回来 将查询到的groupid,ouid,shopid,反射到这里保存，同一次可使用
    # ------测试环境的集团和组织 [ifpos、crm、 oms模块的用例]-----
    # group_id = 3
    # ou_id = 9
    # shop_id = 8543  # 254店铺资料配置的crm2.0接口对应的shop_id是8543
    # shop_id = 5138
    # --- 演示环境的集团和组织 【促销计算接口】的集团-----
    # group_id = 29
    # ou_id = 750
    # shop_id = None
    # ----测试环境， 【促销计算接口】的集团 自动化促销活动-----
    group_id = 63
    ou_id = 2500
    shop_id = None
    # ---测试环境 新的业务组织，进行初始化数据，包括商品和整单活动、【库存相关的用例inv】
    # group_id = 63
    # ou_id = 5763
    # shop_id = None

    # 小程序商城绑定的会员的手机号
    shopnc_member_phone = "xxxxx"

    # 会员卡号
    card_code = None
    # cookie、token 通过反射保存回来
    COOKIE = None
    TOKEN = None
    Authroizen = None

    coupon_id = None
    send_coupon_id = None
    # 新增卡券的coupinkeycode
    couponKeycode = None



