

已知有一个api接口返回的json结构是这样的

{
  "data": [
    {
      "id": 67,
      "rowStatus": "NORMAL",
      "creatorId": 1,
      "createdTs": 1679750917,
      "updatedTs": 1686655326,
      "content": "#TODO [📌学习计划]\n- [ ] [C++ 相关](https://trilium.learn.xzgljiang.com/share/cpp-todo)\n- [ ] Linux 底层原理\n- [ ] shell 编程 (10%)",
      "visibility": "PUBLIC",
      "pinned": false,
      "creatorName": "xzgl",
      "resourceList": []
    },
    {
      "id": 66,
      "rowStatus": "NORMAL",
      "creatorId": 1,
      "createdTs": 1679750901,
      "updatedTs": 1680275129,
      "content": "#相册 玲芽之旅，新海诚，真不错",
      "visibility": "PUBLIC",
      "pinned": false,
      "creatorName": "xzgl",
      "resourceList": [
        {
          "id": 24,
          "creatorId": 1,
          "createdTs": 1680275129,
          "updatedTs": 1680275129,
          "filename": "铃芽之旅观影 (3).jpeg",
          "internalPath": "",
          "externalLink": "https://misc.cos.xzgljiang.com/memos/2023/03/31铃芽之旅观影 (3).jpeg",
          "type": "image/jpeg",
          "size": 0,
          "publicId": "c2381d70-9ff2-d514-88eb-9a2cd8001202",
          "linkedMemoAmount": 1
        },
        {
          "id": 25,
          "creatorId": 1,
          "createdTs": 1680275129,
          "updatedTs": 1680275129,
          "filename": "铃芽之旅观影 (2).jpeg",
          "internalPath": "",
          "externalLink": "https://misc.cos.xzgljiang.com/memos/2023/03/31铃芽之旅观影 (2).jpeg",
          "type": "image/jpeg",
          "size": 0,
          "publicId": "8e7f2268-bfd1-9f26-966d-20653fca5a2a",
          "linkedMemoAmount": 1
        },
        {
          "id": 26,
          "creatorId": 1,
          "createdTs": 1680275129,
          "updatedTs": 1680275129,
          "filename": "铃芽之旅观影 (1).jpeg",
          "internalPath": "",
          "externalLink": "https://misc.cos.xzgljiang.com/memos/2023/03/31铃芽之旅观影 (1).jpeg",
          "type": "image/jpeg",
          "size": 0,
          "publicId": "1405a5f4-ace4-43ad-163d-9e513711ccaf",
          "linkedMemoAmount": 1
        }
      ]
    }
  ]
}

写一个python代码，读取这个接口地址 假设为http://domain/api, 收集以下数据   id,updatedTs,content,creatorName,resourceList ; 其中 resourceList 需要收集一下字段 type,externalLink  
对于数据处理有以下要求
- content 是markdown 格式的数据，需要转换成html
- resourceList  是数组，需要转成json字符串