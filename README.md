# config
python3 处理配置文件脚本

> 想必很多人在使用python的configparser模块处理配置文件时遇到了很多的坑和一些不方便的地方，比如在写配置文件是不会保留注释，再比如读取出来的值都是str类型的
>
> 基于以上问题，我对configparser做了简单的包装，使其在使用时更加方便，更改如下：
>> 1. 写配置文件会保留之前的注释
>> 2. 按照指定类型的数据读取配置文件中的值
>> 3. 在项目中，通过配置可以自动将相对路径转化为绝对路径
>> 4. 处理中文的读和写

下面是具体的使用方法：

## 使用方法
```
全局配置：
    BASE_DIR：项目根目录
    CONFIG_PATH：配置文件路径
    PROJECT_INIT: 是否启用项目中相对路径转换为绝对路径功能
    (后面详细介绍怎么使用)

读： read(section=None, option=None, **kwargs):
        １．参数为空则读取　CONFIG_PATH　配置文件中所有的内容，返回字典类型。
        ２．section：读取指定　section　中所有的内容，返回字典类型。
        ３．section，option: 读取指定 section 中　指定　option 的值，返回具体类型的值。
        ４．**kwargs: 不定参数，可以读取指定　config_path　= '<path>.cfg' 路径的配置文件。没有则使用全局的配置文件路径。
        
写： write(section, option, value, **kwargs):
        １．无 section 或 option 会新生成，存在则只改变value。
        ２．**kwargs: 不定参数，可以写指定　config_path　= '<path>.cfg' 路径的配置文件。没有则使用全局的配置文件路径。
```
注：配置文件格式
```
# 注释
[section]
option = value
```

## 功能说明
### 一、写配置文件保留之前的注释
这里只说一下我的实现方法：
> 首先，在实例化configparser时使用以下参数：
> ```
> cp = configparser.ConfigParser(comment_prefixes=(','), allow_no_value=True)
> ```
> comment_prefixes: 该参数声明注释是以','开头的，默认值为('#', ','), 这里只使用','，因为我不习惯用','来注释；习惯用','注释的朋友可以更改此处的值为('#')或者置空
>
> allow_no_value: 该参数作用是是否容许没有value, 默认为False, 就是说必须要有value; 在这里设置为True，容许没有value
>> 以上两项配置总体来说就是：以'#'开头的内容将不会被识别为注释，而是section下的一个option, 这里用这种取巧的方法保留下注释。
>>
>> 再说一下configparser是怎么写配置文件的：它是先将所有内容读出来，写入新内容或更改以前存在的值后再将更改后的内容保存到文件；所以在读取时就将注释内容过滤，那保存时肯定就不会保存下原来的注释；通过以上两个参数在读取时将‘注释’保存下来，那么写入时也将会写入文件。这就是我保存注释的思路。
>> 
>> 但是，这样做存在一个问题，就是 [section] 上一行的注释会被当做是上一个 [section] 的 option, 在保存时会出现下面这种格式：
>> ```
>> (这是原格式)                             (这是写入新内容后的格式)
>> [section-01]                            [section-01]
>> option = value                          option = value
>>                                         # 注释
>> # 注释
>> [section-02]                            [section-02]
>> option = value                          option = value
>>                                         new_option = value
>> ```
>> 这不是我们想要的结果，我们的本意是给[section-02]加注释，写入后虽然不影响使用和理解，也可以手动再改回来。但身为程序员，能用代码实现的事情为啥还需要手动，况且我还有一点小强迫症。幸运的是configparser在写入操作后会将配置文件全部格式化的整整齐齐的，就如上面的形式，多个[section]之间只会出现一个换行，既然有规律，还这么整齐，那么，。。。就有了以下方法：
>> ```
>> def __format_remark(config_path=CONFIG_PATH):
>>     """
>>     格式化注释，使其恢复原位置
>>     :param config_path:
>>     :return:
>>     """
>>     with open(config_path, 'r', encoding='utf-8') as f:
>>         conf_list = f.readlines()
>> 
>>     _ = 0
>>     for line in conf_list:
>>         if line[0] == '#':
>>             if conf_list[_ + 1] == '\n' and conf_list[_ + 2].strip()[0] == '[' \
>>                     and conf_list[_ + 2].strip()[-1] == ']':
>>                 del conf_list[_ + 1]
>>                 conf_list.insert(_, '\n')
>>         _ += 1
>> 
>>     with open(config_path, 'w', encoding='utf-8') as f:
>>         for line in conf_list:
>>             f.write(line)
>> ```
>> 既然是配置文件，那最好的方法当然是按行读取了。这里我用的方法就是将写入后的配置文件按行读取成一个列表，遍历列表找到注释的地方，判断符合情况的注释修改其在列表中的位置，最后在将修改后的内容保存到文件中。这样就实现了将注释的位置复原。对于大文件，这样做的效率很低，但配置文件一般不会很大，如果特别大的配置文件的话，那我选择sqlite。手动滑稽 <_< ... 。 这样写入操作后调用一下此方法得到的配置文件如下：
>> ```
>> (这是原格式)                             (这是写入新内容后的格式)
>> [section-01]                            [section-01]
>> option = value                          option = value
>>                                         
>> # 注释                                   # 注释
>> [section-02]                            [section-02]
>> option = value                          option = value
>>                                         new_option = value
>> ```
>> 这才是我们需要的结果，ok, 搞定，收工。。。 不对，还有其他使用方法，且听我一一道来。。。

### 二、按指定类型的数据读取配置文件中的值
这里是受到Django ORM查询方法的启发，比如以下方法：
```
article_list = models.Article.objects.filter(date__range=['2018-08-01', '2018-08-15'])
```
会查询到'2018-08-01' - '2018-08-15' 之间所有的文章，这里是通过在字段后面加'__funs'实现的。

如果我有这样一个配置文件：
```
[test]
width__int = 100
height__float = 50.85
language__list = python, java, c, go, php
status = True
```
那么我可不可以根据option后面的 '__type' 指定的类型直接取到该类型的值呢，答案是肯定的。在我包装的read方法中会在取出值后检测后面的类型，尝试将值装换为该类型。前提是要给出正确的配置文件。有几点说明如下：
> ```
> Ａ: bool类型的值会自动转换(无需在option后加__bool)，不要求大小写(true, True 都会转换为bool类型的　'True', False　同)。
> Ｂ: option　中如果最后５位为　__int 则会将值转换为 int　类型 。
> C: option　中如果最后7位为　__float 则会将值转换为 float　类型。
> D: option　中如果最后６位为　__list 则会将值转换为 list　类型。
>     注：所有value用‘,’ 分割开，且必须为英文状态下的','。各值之间的空格会自动去除，如：
>     [program]
>     language__list = python　　　, java, 　　　　　c, 　go, php
> 
>    取到的list 为：　['python', 'java', 'c', 'go', 'php']
> 
> 注：option　中如果出现　__* ，在读取时调用read方法　忽略 __*　内容，会自动读取到正确的值，如
>     [test]
>     width__int = 500
>     top__float = 200.567
> 
>     读取时直接调用：　read('test', 'width'), read('test', 'top') 会将值自动转换为‘__’后指定的类型
> ```
### 三、在项目中，通过配置可以自动将相对路径转化为绝对路径
对于同一个项目而言，路径的值可以写为相对与本项目的路径，在读取时会自动转换为相应的绝对路径，但有如下几点要求：
```
A: 全局变量必须设置如下：
    BASE_DIR：项目根目录
    CONFIG_PATH：配置文件路径
    PROJECT_INIT: True
    
    例：在Django项目中的setting文件中，设置配置文件路径为：
        CONFIG_PATH = os.path.join(BASE_DIR, '你的配置文件在项目中的相对路径')
        
        然后在本脚本中导入这两个值即可。
    
    总的来说：就是需要两个路径，这里可以自由设置，路径对就行。

B: option中最后６位必须包含 ’__path‘ 字符串，如：
    [log]
    web__path = log/*.log

C: 会自动在指定的全局配置文件中加入以下内容：
    [base]
    path = <项目路径>
```

