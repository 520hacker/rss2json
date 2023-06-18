## PYTHON编写的自动读取RSS并提供接口API的代码

使用python 编写一个web服务, 使用http端口5005，其功能是，请直接按照你的理解完成代码，不要在代码中保留TODO和省略号来替代未完成代码的情况，请完成它。请跳过解释过程，直接完成它并给我最终的代码。

请注意考虑这个代码可能需要运行在windows上，并尽可能的使用 try catch，将可能存在的异常信息print出来。

- 当前目录有文件rss.json

  - 内容是RSS地址集合

    ```json
    ["https://memos.qiangtu.com/u/1/rss.xml","https://memos.qiangtu.com/u/2/rss.xml"]
    ```

  - 程序初始化的时候读取这个rss.json文件并获取到RSS地址列表

- SQLITE数据库定义

  - SQLITE数据库文件 rss.db 

    - 应用启动后就发起一次检查数据库，没有则创建数据库和表结构

  - SQLITE数据库中需要有3个表，

    - rss 表用于存储rss 内容

      - id,自增主键
      - link,来自RSS item的link,具备唯一性
      - source_id,对应source 表的id字段
      - title,来自 RSS item的title
      - description,来自RSS item的description
      - **pubDate,timestamp,来自RSS item的pubDate,需要从RSS中的时间日期格式转换为timestamp.**
      - enclosure,来自RSS item的enclosure

    - source 表 用于存储被遍历过的rss地址

      - id,自增主键
      - rss, rss地址,具备唯一性

      - link,来自RSS channel的link
      - title,来自 RSS channel的title
      - description,来自RSS channel的description
      - **pubDate,timestamp,来自RSS channel的pubDate,需要从RSS中的时间日期格式转换为timestamp.**

    - log表用于存储每一次rss的请求，

    - 所有表都有自增id作为主键

- 遍历任务1：

  - 遍历这个RSS地址数组，读取所有的RSS内容，并保存到同目录下的SQLITE数据库
  - 当存在多个RSS地址的时候，使用多线程请求，每个线程请求不同的RSS地址，最大线程数5
  - 当RSS地址连接成功，在log表中记录时间和读取结果为'success',
    - print 连接成功的地址和成功信息到控制台
    - 并把rss的数据的link,title,description,pubDate,enclosure逐条转换格式后保存到到sqlite,
      - 在保存到sqlite的过程中，基于rss的link进行去重，其他字段可以为空,
      - 在RSS中pubDate是格式为‘Sat, 17 Jun 2023 04:07:30 +0000’的日期时间字段
        - 请转换pubDate为timestamp，如果转换失败则使用1天前的当前时间的timestamp值作为结果。
    - 如果对应的link已经存在则跳过当前这条rss更新
  - 当RSS地址连接失败
    - print 连接失败的地址和失败信息到控制台
    - 则直接在log表中记录失败的错误信息，然后马上跳过这条rss执行下一条。

- 遍历任务周期：

  - 应用启动后,检查完数据库之后，立刻发起一次遍历
  - 添加定期遍历RSS并保存到SQLITE数据库的部分代码，定期规则是每5分钟发起一次遍历任务1，如果当前有任务正在进行，则跳过本次发起
    - 使用变量 lockObject 来监控是否正有任务进行，
      - 默认false,
      - 当任务启动，则设置为 true, print 任务启动成功的信息到控制台 
      - 任务结束或者异常，则设置为false

- 提供5个HTTP访问接口

  - /rss 
    - 这是一个get接口
    - 用于读取SQLITE中对应的RSS内容，并统一格式后以JSON形式返回给前端
    - 这是一个列表API,  以pubDate倒序排序后返回，
    - 支持分页(默认每页50条)，搜索
      - 搜索功能是支持针对RSS的内容进行全文检索。
  - /author 
    - 这是一个get接口
    - 用于去SQLITE对应的source内容，并以JSON的形式返回给前端
    - 这是一个列表API，支持分页
  - /new 
    - 这是一个get接口
    - 参数为url={new rss address}，用于添加新的rss地址，已经存在的rss地址则直接返回"already exits" 的JSON格式错误信息
    - 添加了rss地址之后，程序会将新的rss地址更新到sqlite和待遍历列表和rss.json
    - 参数 key 为验证权限用
  - /remove
    - 这是一个get接口，
    - 参数为url={new rss address}，用于删除对应的rss地址，如果在删除之前rss只剩下一个地址，则返回"only 1 left" 的JSON格式错误信息
    - 参数 key 为验证权限用
  - /log
    - 这是一个get接口
    - 返回log表的日志数据，按照id倒序排列，支持分页

- 权限验证

  - 支持在程序启动的时候附加参数 admin_key ， 默认值odinSay，并将这个值指定为全局变量 admin_key
  - 当请求/new 和 /remove 的时候，需要附加参数 key ，用于跟 admin_key 进行比对，如果key!=admin_key ,则抛出权限验证失败错误。

  

