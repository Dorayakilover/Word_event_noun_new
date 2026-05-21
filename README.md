# Word_event_noun_new
## 课程项目 事件名词判断，基于wiki_zh
```text
文件结构：
├── corpus/                  # 词语目录（无句子）
│   └── word.txt           # 经过名词提取的词汇文件
├── lexicon/                 # 词库目录
│   └── triggers_num.txt     # 事件触发词表（动量词、时量词）
│   └── triggers_verb.txt     # 事件触发词表（特定事件动词）
├── sentence/                     # 语料库目录
│   └── output                   # 名词语料库目录
├── result/                      # 运行结果目录
│   └── result.txt            # 事件名词提取结果
│   └── score.txt             # 事件名词的事件性分数统计
├── noun_match.py            # Step1 名词匹配（在维基百科wiki语料中匹配名词并摘录句子） 
└── judge_event_nouns.py     # Step2 事件性名词判断（使用jieba分词和触发词匹配）
```
