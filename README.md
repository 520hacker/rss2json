## RSS2JSON:自动读取RSS并提供接口API返回JSON

### 程序说明

这个需求是来自于使用了MEMOS之后，有互相关注且订阅RSS作为广场的需求。本程序是为类似RSS广场之类的应用程序提供API支持的，其功能是将更新到的RSS转换为json返回出来。

![](https://memosfile.qiangtu.com/picgo/assets/2023/06/18202306_18014611.png)

PS:本程序主要代码由GPT创建, 有bug是正常的，反馈请联系https://t.me/Odinluo

----

### 安装依赖

要一次性安装所有依赖项，您可以使用以下命令：

```bash
pip install feedparser argparse requests flask
```

这将安装所有列出的依赖项，包括`os`、`json`、`sqlite3`、`threading`、`time`、`feedparser`、`calendar`、`argparse`、`requests`和`flask`。

### 运行程序

```shell
python app.py --admin_key password
```

### 访问

- http://您的ip地址:5005/

### 我部署的例子（小霸王环境，请怜惜）

- https://rsssquare.qiangtu.com/api/rss

----

### API 说明

- /rss  GET，返回收集到的rss的json数据
  - page 数字，默认值1
  - per_page 数字，默认值50
  - search 搜索关键字
  - source 依据来源rss地址进行筛选
- /log GET，返回收集行为的日志的json数据
  - page 数字，默认值1
  - per_page 数字，默认值50
- /author GET，返回收集到的rss地址源清单
  - page 数字，默认值1
  - per_page 数字，默认值50
- /new GET，添加新的RSS地址
  - url 要添加的rss的网址
  - avatar 要添加的rss的用户头像，可以不传
  - key 你启动的时候指定的秘钥
- /remove GET，删除已经有的RSS地址
  - url 要删除的rss的网址
  - key 你启动的时候指定的秘钥

----

### 安装为docker容器

#### 如果您选择自己编译

使用以下命令构建Docker镜像：

```bash
docker build -t rss2json .
```

最后，可以使用以下命令运行Docker容器：

```bash
docker run -e ADMIN_KEY=<your_admin_key> -p 5005:5005 rss2json
```

其中`<your_admin_key>`是您的实际管理员密钥。

#### 如果您只是想安装一下，你可以使用我的版本

 我提交的版本： odinluo/rss2json:latest

如果您是群晖安装的话，您可以这么操作：

- 选择一个目录来保存对应的文件，比如 /docker/rss2json 。
- 下载映像odinluo/rss2json:latest
- 基于这个映像创建容器,命名随意，我这里用的rss2json
  - 设置环境变量
    - ADMIN_KEY 值 {你的密码}
  - 映射路径
    - /app/rss.json  /docker/rss2json/rss.json ( 文件里面你可以初始化指定一些rss的地址)
  - 设置端口
    - 5005 (您的外部暴露端口):5005 ( 内部固定端口)
- 启动容器
  - http://ip:5005/

----

### 最近更新

2023/06/20

- 添加了一个10秒超时

2023/06/19

- 按照功能对Py文件进行了分割，主要是chatGPT也读不了太大的文件。
- 按照林木木的建议，从MEMOS的API读取了站点的自定义头像。
- 优化了代码，修复了部分BUG

2023/06/18 父亲节快乐

- 发布了基础的py工程 

- 把合体的工程分离了 
- 按照林木木的建议，从MEMOS的API直接读取了更多的信息 
- 分离了log.db - 继续更新了docker镜像

----



## RSS2JSON: Automatically Retrieve RSS and Provide API Interface to Return JSON

### Program Description

This requirement is for applications similar to RSS squares that have mutual attention and subscribe to RSS after using MEMOS. This program provides API support for applications like RSS squares, and its function is to convert updated RSS into JSON and return it.

PS: The main code of this program was created by GPT. It is normal to have bugs. Please contact https://t.me/Odinluo for feedback.

----

### Install Dependencies

To install all the dependencies at once, you can use the following command:

```bash
pip install feedparser argparse requests flask
```

This will install all the dependencies listed, including `os`, `json`, `sqlite3`, `threading`, `time`, `feedparser`, `calendar`, `argparse`, `requests`, and `flask`.

### Running the Program

```shell
python app.py --admin_key password
```

### Access

- http://your-ip-address:5005/

### The example I deployed (a fragile environment, please be kind).

- https://2504.qiangtu.com:8087/

----

### API Documentation

- /rss GET, returns the collected RSS data in JSON format
  - page number, default 1
  - per_page number, default 50
  - search search keyword
  - source filter by rss address
- /log GET, returns the collected logs data in JSON format
  - page number, default 1
  - per_page number, default 50
- /author GET, returns the list of collected RSS source addresses
  - page number, default 1
  - per_page number, default 50
- /new GET, adds a new RSS address
  - url the URL of the RSS to be added
  - avatar optional, the avatar for rss author
  - key the admin key specified when starting the program
- /remove GET, removes an existing RSS address
  - url the URL of the RSS to be removed
  - key the admin key specified when starting the program

----

### Installing as a Docker Container

#### If you choose to build it yourself

Use the following command to build the Docker image:

```bash
docker build -t rss2json .
```

Finally, you can run the Docker container with the following command:

```bash
docker run -e ADMIN_KEY=<your_admin_key> -p 5005:5005 rss2json
```

Where `<your_admin_key>` is your actual admin key.

#### If you just want to install it, you can use my version

The version I submitted is: odinluo/rss2json:latest

If you are installing it on Synology NAS, you can follow these steps:

- Choose a directory to store the corresponding files, such as /docker/rss2json.
- Download the image odinluo/rss2json:latest.
- Create a container based on this image, naming it as you like. In my case, I used rss2json.
  - Set environment variables
    - ADMIN_KEY value {your_password}
  - Map paths
    - /app/rss.json  /docker/rss2json/rss.json (You can specify some RSS addresses in the file)
  - Set ports
    - 5005 (Your exposed port):5005 (internal fixed port)
- Start the container
  - http://ip:5005/

----