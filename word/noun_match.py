import os
import json
import re

# -------- 配置 --------
wiki_root = "E:/wiki_zh"                    # wiki 语料库根目录 
folders_to_process = ["AA","AB","AC","AD","AE","AF","AG","AH","AI","AJ","AK","AL","AM"]

lexicon_files = [
    "corpus/word.txt"
]       # 候选词文件列表，也就是需要匹配的名词列表

sentence_root = "sentence"                  # 输出句子文件夹根目录
os.makedirs(sentence_root, exist_ok=True)

# 中文句子分割符
sentence_end = re.compile(r"([。！？；])")

# -------- 读取 noun 文件 --------
group_nouns = {}      # {group_name: set(nouns)}
group_matched = {}    # {group_name: set(matched nouns)}

for lex_file in lexicon_files:
    group_name = os.path.splitext(os.path.basename(lex_file))[0]  # li / nei / zhong
    nouns = set()
    with open(lex_file,"r",encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if w:
                nouns.add(w)
    group_nouns[group_name] = nouns
    group_matched[group_name] = set()
    # 输出文件夹
    os.makedirs(os.path.join(sentence_root, group_name), exist_ok=True)
    print(f"[{group_name}] 读取候选词数量: {len(nouns)}")

# -------- 遍历 wiki JSON 并匹配 --------
for folder in folders_to_process:
    folder_path = os.path.join(wiki_root, folder)
    if not os.path.isdir(folder_path):
        print(f"跳过不存在的文件夹: {folder_path}")
        continue

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        with open(file_path,"r",encoding="utf-8") as f:
            for line_num,line in enumerate(f,1):
                try:
                    data = json.loads(line)
                    title = data.get("title","").strip()
                    text = data.get("text","").replace("\n"," ").strip()
                    if not title or not text:
                        continue

                    # 遍历三组词
                    for group_name,nouns in group_nouns.items():
                        matched = [n for n in nouns if n in title]
                        if not matched:
                            continue

                        out_dir = os.path.join(sentence_root,group_name)

                        # 拆分句子
                        parts = sentence_end.split(text)
                        sentences = []
                        if len(parts) > 1:
                            for i in range(0,len(parts)-1,2):
                                s = parts[i].strip()+parts[i+1]
                                if len(s) > 1:
                                    sentences.append(s)
                        else:
                            if len(text) > 1:
                                sentences.append(text)

                        # 写入每个匹配词的 txt
                        for noun in matched:
                            group_matched[group_name].add(noun)
                            out_path = os.path.join(out_dir,f"{noun}.txt")
                            with open(out_path,"a",encoding="utf-8") as out_f:
                                for s in sentences:
                                    out_f.write(s+"\n")
                except Exception as e:
                    print(f"解析失败 {file_path} 第 {line_num} 行: {e}")
                    continue

# -------- 生成 none.txt --------
for group_name,all_nouns in group_nouns.items():
    matched = group_matched[group_name]
    failed = sorted(all_nouns - matched)
    none_path = os.path.join(sentence_root,group_name,"none.txt")
    with open(none_path,"w",encoding="utf-8") as f:
        for noun in failed:
            f.write(noun+"\n")
    print(f"[{group_name}] 未匹配词数量: {len(failed)} → none.txt")

print("全部完成：已生成按词分组的语料文件")
