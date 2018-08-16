"""
Author: Azazel
Email: azazel.zhao@live.cn

GitHub: https://github.com/AzazelX5/config
"""
import os
import codecs
import configparser

# from 你的项目名.settings import BASE_DIR, CONFIG_PATH  # django 项目专用

BASE_DIR = '项目路径'
CONFIG_PATH = '配置文件路径'
PROJECT_INIT = True # True or False

def __init():
    """
    初始化配置文件
    :return:
    """
    write('base', 'path', BASE_DIR)


def read(section=None, option=None, **kwargs):
    """
    读取配置文件方法
    :param section:
    :param option:
    :return:
    """
    if 'config_path' in kwargs.keys():
        config_path = kwargs['config_path']
    else:
        if PROJECT_INIT:
            __init()
        config_path = CONFIG_PATH

    cp = configparser.ConfigParser()
    cp.read(config_path, encoding="utf-8-sig")

    def __set_value(key, value):
        """
        设置配置文件值（路径 和 True or False 以及 __int, __float, __list）
        :param value:
        :return:
        """
        # 返回绝对路径
        if key[-6:] == '__path':
            base_path = cp['base']['path']

            return os.path.join(base_path, value)

        # 返回bool类似的  True
        elif 'true' == value.lower():
            return True
        # 返回bool类似的  False
        elif 'false' == value.lower():
            return False
        # 返回 int 类型
        elif key[-5:] == '__int':
            try:
                return int(value)
            except ValueError:
                a, b = value.split('.')
                if int(b[0]) >= 5:
                    return int(a) + 1
                else:
                    return int(a)
        # 返回　float 类型
        elif key[-7:] == '__float':
            return float(value)
        # 返回list
        elif key[-6:] == '__list':
            return list(map(str.strip, value.strip().split(',')))
        else:
            return value

    config_dict = {}
    # 取出配置文件所有内容
    if section is None and option is None:
        sections = cp.sections()
        for section in sections:
            sectioin_dict = {}
            options = cp.options(section)
            for option_obj in options:
                if '__' in option_obj:
                    option = option_obj.split('__')[0]
                else:
                    option = option_obj
                sectioin_dict[option] = __set_value(option_obj, cp[section][option_obj])

            config_dict[section] = sectioin_dict
    # 取出配置文件中所有section内容
    elif section is not None and option is None:
        options = cp.options(section)
        for option_obj in options:
            if '__' in option_obj:
                option = option_obj.split('__')[0]
            else:
                option = option_obj
            config_dict[option] = __set_value(option_obj, cp[section][option_obj])

    # 取出配置文件中具体的(section,option)的值
    else:
        try:
            config_dict = __set_value(option, cp[section][option])
        except KeyError:
            options = cp.options(section)
            for option_obj in options:
                if '{0}__'.format(option) in option_obj:
                    config_dict = __set_value(option_obj, cp[section][option_obj])

    return config_dict


def write(section, option, value, **kwargs):
    """
    写配置文件
    :param section:
    :param option:
    :param value:
    :param kwargs:
    :return:
    """
    if 'config_path' in kwargs.keys():
        config_path = kwargs['config_path']
    else:
        config_path = CONFIG_PATH

    cp = configparser.ConfigParser(comment_prefixes=(','), allow_no_value=True)
    cp.read(config_path, encoding="utf-8-sig")

    try:
        cp.add_section(section)
    except configparser.DuplicateSectionError:
        pass
    cp.set(section, option, value)

    cp.write(codecs.open(config_path, 'w', "utf-8"))

    __format_remark()


def __format_remark(config_path=CONFIG_PATH):
    """
    格式化注释，使其恢复原位置
    :param config_path:
    :return:
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        conf_list = f.readlines()

    _ = 0
    for line in conf_list:
        if line[0] == '#':
            if conf_list[_ + 1] == '\n' and conf_list[_ + 2].strip()[0] == '[' \
                    and conf_list[_ + 2].strip()[-1] == ']':
                del conf_list[_ + 1]
                conf_list.insert(_, '\n')
        _ += 1

    with open(config_path, 'w', encoding='utf-8') as f:
        for line in conf_list:
            f.write(line)


if __name__ == '__main__':
    pass
