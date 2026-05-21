import os
import jieba.posseg as pseg
from collections import defaultdict
import re

# ---------- 配置 ----------
sentence_dir = "sentence/output"         # 需要判断的词语
trigger1_path = "lexicon/triggers_num.txt"     # 触发词：动量词、时量词
trigger2_path = "lexicon/triggers_verb.txt"    # 触发词：特定事件动词
output_path = "result.txt"               # 输出文件：事件名词结果
progress_path = "score.txt"              # 输出文件：每个词事件性分数结果
window_size = 2                                # 窗口大小，判断事件性时考虑的上下文窗口大小
event_threshold = 0.1                          # 事件性分数阈值，当事件性分数大于该阈值，则认为是事件名词

# ---------- 加载触发词 ----------
def load_triggers(*files):
    triggers = set()
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    triggers.add(line)
    return triggers

triggers = load_triggers(trigger1_path, trigger2_path)

# ---------- 数字+量词正则 ----------
num_words = [w for w in triggers if w in (
    "次 回 遍 趟 下 顿 番 遭 场 阵 通 气 世纪 年 月 星期 日 天 时 分 秒".split()
)]
num_pattern = re.compile(r"(\d+|[一二三四五六七八九十百千万亿]+)(" + "|".join(num_words) + ")")

# ---------- 统计单个词语的事件性 ----------
def judge_event_noun(word, sentences):
    noun_freq = 0
    cooc_freq = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # 分词 + 词性标注
        words_flags = list(pseg.cut(sentence))
        words = [w.word for w in words_flags]
        
        # 遍历每个词
        for i, (w, flag) in enumerate(words_flags):
            if w == word:
                noun_freq += 1
                
                # 检查窗口
                start = max(0, i - window_size)
                end = min(len(words), i + window_size + 1)
                window_words = words[start:end]
                
                has_trigger = any(t in window_words for t in triggers)
                if not has_trigger:
                    for ww in window_words:
                        if num_pattern.search(ww):
                            has_trigger = True
                            break
                
                if has_trigger:
                    cooc_freq += 1
    
    if noun_freq == 0:
        return 0.0
    
    alpha = 0.01
    score = cooc_freq / (noun_freq + alpha)
    return score

# ---------- 遍历文件 ----------
event_nouns = []
progress_data = []

# 获取所有txt文件
txt_files = [f for f in os.listdir(sentence_dir) if f.endswith(".txt")]

print(f"找到 {len(txt_files)} 个文件")

for filename in txt_files:
    # 提取词名（去掉.txt后缀）
    word = filename[:-4]
    
    file_path = os.path.join(sentence_dir, filename)
    
    # 读取句子
    with open(file_path, "r", encoding="utf-8") as f:
        sentences = f.readlines()
    
    # 判断事件性
    score = judge_event_noun(word, sentences)
    
    print(f"{word}: 事件性分数 = {score:.4f}")
    
    # 记录进度数据
    progress_data.append((word, score))
    
    # 超过阈值则认为是事件名词
    if score >= event_threshold:
        event_nouns.append(word)

# ---------- 保存结果 ----------
# 保存事件名词结果
with open(output_path, "w", encoding="utf-8") as f:
    for word in event_nouns:
        f.write(word + "\n")

# 保存进度数据
with open(progress_path, "w", encoding="utf-8") as f:
    f.write("词语\t事件性分数\n")
    for word, score in progress_data:
        f.write(f"{word}\t{score:.4f}\n")

print(f"\n处理完成！")
print(f"共找到 {len(event_nouns)} 个事件名词")
print(f"事件名词结果已保存到 {output_path}")
print(f"进度数据已保存到 {progress_path}")
print(f"共处理了 {len(progress_data)} 个词语")
