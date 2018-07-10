# coding:utf-8
import ConfigParser
import os
import ast
import re
import _winreg
import codecs
import collections


# 示例数据
# {u'env': {u'anipipe_tools_loc': {'value': 'D:\\ffff'},
#           u'shader_dirs': {'value': 'C:\\fff\\shader;c:\\ff\\shader;D:\\ffff\\shader'},
#           u'test_loc': {'value': 'C:\\fff'},
#           u'test_loc_script': {'value': 'C:\\fff\\script'}},
#  u'version': {u'maya': {'value': 2015}, u'nuke': {'value': 9.1}},
#  u'video': {u'fps': {'value': 24},
#             u'height': {'value': 858},
#             u'width': {'value': 2015}}}

# 获取window桌面路径
def get_desktop():
    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                          r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    return _winreg.QueryValueEx(key, "Desktop")[0]


# 展开值,比如%FF%
def expand_env_value(envValueString, dataBase=os.environ):
    values = [e for e in envValueString.split(";") if e]
    replacedValues = []
    for value in values:
        finds = re.findall("\%([a-zA-Z_]+)\%", value)
        if finds:
            # remove duplicate
            finds = list(set(finds))
            # need Expand
            data = {}
            for find in finds:
                if dataBase.get(find, None):
                    if dataBase[find].split(";").__len__() > 1:
                        raise Exception("Can not Expand Value:no idea to how to expand This env[{}]".format(find))
                    else:
                        data[find] = dataBase[find]
                else:
                    raise Exception("Can not Expand Value:This env[{}] not exist".format(find))
            # replace
            for origin, target in data.items():
                replacedValues.append(value.replace("%{}%".format(origin), target))
        else:
            replacedValues.append(value)
    return ';'.join(replacedValues)


# 读取配置文件，转换为字典
# 读入为有序字典
def read_ini_to_dict(fileHandle):
    p = ConfigParser.ConfigParser()
    p.readfp(fileHandle)
    data = collections.OrderedDict()
    sections = p.sections()
    for s in sections:
        temp = collections.OrderedDict()
        for k, v in p.items(s):
            try:
                value = ast.literal_eval(v)
            except Exception:
                raise Exception(
                    "ini file has wrong type value:\n(not support set type)\n[key:{},value:{}]".format(k, v))
            else:
                temp[k] = value
        data[s] = temp
    return data


# 写入配置文件，
# 须知这里需要的字典应该是有序字典
def write_int_from_dict(fileHandle, data=None):
    if data:
        default = data.get("DEFAULT", None)
        if default:
            config = ConfigParser.ConfigParser(default)
        else:
            config = ConfigParser.ConfigParser()
        data.pop("DEFAULT", None)
        for section, section_dict in data.items():
            config.add_section(section)
            # 假如有需要expand的值，只在当前section中找
            # 获取环境
            # 下面的v是字典
            # 格式化下section_dict
            section_dict_formated = {k: v["value"] for k, v in section_dict.items()}
            env_database = dict(os.environ, **section_dict_formated)
            for key, value in section_dict.items():
                # expand first
                # value 是个字典
                if isinstance(value["value"], basestring):
                    value["value"] = expand_env_value(value["value"], env_database)
                config.set(section, key, value, )
        config.write(fileHandle)


class SectionObject(object):
    def __init__(self, name=None):
        super(SectionObject, self).__init__()
        self._name = None
        if isinstance(name, basestring):
            self._name = name
        # self._option_data = {}
        # 不再依赖这个_option_data
        # 去重有序列表
        self._option_objects = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, basestring):
            self._name = name
        else:
            raise TypeError("You need a string type data.")

    def update_option(self, option_object):
        self._process_option(option_object, 'u')

    def remove_option(self, option_object):
        self._process_option(option_object, "r")

    def _process_option(self, option_object, mode="u"):
        # 两种模式 u/r
        if isinstance(option_object, OptionObject) and option_object.isVaild():
            if isinstance(mode, basestring) and mode.lower() in ("u", "r"):
                # 参数正确

                if mode.lower() == 'u':
                    # 更新数据
                    if option_object not in self._option_objects:
                        # 评估数据
                        same_data_option_object = self._find_option(option_object.key)
                        if same_data_option_object:
                            # 说明数据重复，需要更新
                            # 先删除原先的obj
                            self._option_objects.pop(self._option_objects.index(same_data_option_object))
                            # 添加
                            self._option_objects.append(option_object)
                        else:
                            # 说明数据不重复，需要添加
                            self._option_objects.append(option_object)
                    else:
                        # obj内数据上次添加时和这次添加不一致,以这次的数据重新评估
                        # 先移除
                        self._option_objects.pop(self._option_objects.index(option_object))
                        # 评估数据
                        same_data_option_object = self._find_option(option_object.key)
                        if same_data_option_object:
                            # 说明数据重复，需要更新
                            # 先删除原先的obj
                            self._option_objects.pop(self._option_objects.index(same_data_option_object))
                            # 添加
                            self._option_objects.append(option_object)
                        else:
                            # 说明数据不重复，需要添加
                            self._option_objects.append(option_object)

                if mode.lower() == "r":
                    # 删除数据
                    # 对象在??
                    if option_object in self._option_objects:
                        self._option_objects.pop(self._option_objects.index(option_object))
                    elif option_object.key in self._option_status():
                        # 数据可能在
                        obj = self._find_option(option_object.key)
                        self._option_objects.pop(self._option_objects.index(obj))

            else:
                raise ValueError("the value of model is wrong:\nsupported:(\"a\",\"r\")\n{}".format(mode))
        else:
            raise TypeError("{} is not OptionObject".format(option_object))

    def _option_status(self):
        temp_dict = collections.OrderedDict()
        for o in self._option_objects:
            temp_dict[o.key] = o.value
        return temp_dict

    def _find_option(self, key):
        temp = self._option_status()
        return temp[key] if key in temp else None

    def to_formatted_dict(self):
        formatted_option_dict = collections.OrderedDict()
        for k, v in self._option_status().items():
            formatted_option_dict[k] = {"value": v}

        return collections.OrderedDict([(self.name, formatted_option_dict)])


class OptionObject(object):
    __support__ = (tuple, list, str, unicode, int, float,)

    def __init__(self, key=None, value=None):
        super(OptionObject, self).__init__()
        self._key = None
        self._value = None
        # 准备初始化数据
        if isinstance(key, basestring):
            self._key = key
            if type(value) in self.__support__:
                self._value = value

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        if isinstance(key, basestring):
            self._key = key
        else:
            raise TypeError("You need a string type data.")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if type(value) in self.__support__:
            self._value = value
        else:
            raise TypeError("You need a  type data.in {}".format(self.__support__))

    def isVaild(self):
        if self._key is not None and self._value is not None:
            return True
        else:
            return False

    def to_dict(self):
        return {self.key: self.value}
