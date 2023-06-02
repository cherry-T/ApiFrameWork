__author__ = 'Tangcl'

# 所有测试用例的前置条件

import pytest
from common.my_log import MyLog
from common.http_request import HttpRequest
from common.do_info import Do_Info
import yaml
import time


mylog = MyLog()


@pytest.fixture(scope="function")
def get_token():
    authroizen = HttpRequest().get_token()
    if authroizen is not None or authroizen != "":
        setattr(Do_Info, 'Authroizen', authroizen)









