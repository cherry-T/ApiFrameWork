# 读取配置文件，
# 1.需要引入配置文件模块 configparser 2.新建configparser()对象，引用ConfigParser()
# 3. 读取 read(配置文件名字，格式有中文需要转换为utf-8)
# 4. 获取里面的session、option 的值


import configparser


class ConfigRead:
    # 根据session ,读取option的值
    def read_config(self, file_name, session_name, option_name):
        '''
        读取配置文件中的值
        :param file_name: 具体的文件路径》文件名
        :param session_name: 配置文件中会话名
        :param option_name: 配置文件中具体的属性名
        :return:
        '''
        config = configparser.ConfigParser()
        config.read(file_name, encoding='utf-8')
        # 继续读取配置文件的session \option  获取具体选项的值
        res = config.get(session_name, option_name)
        return res


if __name__ == '__main__':
    res = ConfigRead().read_config('D:/work/apiAuto/erp_api_Auto_work/config/api.config',
                                   'MULTIPLEAPTCONFIG', 'sheetlist')
    # res =con.read_config()
    print(res)

