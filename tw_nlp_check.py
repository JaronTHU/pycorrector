#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
==========================================================
@author: Jaron Fei
@time: 2025/03/12 15:38:59
@contact: fjjth98@163.com
@description: 
==========================================================
"""
import json
import os.path as osp
from argparse import ArgumentParser
from difflib import SequenceMatcher
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from tqdm import tqdm

from glob import glob
from subprocess import run


def visualize_diff(str1, str2):
    matcher = SequenceMatcher(None, str1, str2)
    # 构建结果字符串
    result = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result.append(str1[i1:i2])
        elif tag == 'delete':
            result.append(f"\033[91m{str1[i1:i2]}\033[0m")
        elif tag == 'insert':
            result.append(f"\033[92m{str2[j1:j2]}\033[0m") 
        elif tag == 'replace':
            result.append(f"\033[91m{str1[i1:i2]}\033[0m")
            result.append(f"\033[92m{str2[j1:j2]}\033[0m")
    return ''.join(result)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('work_dir', type=str)
    parser.add_argument('-b', '--batch_size', type=int, default=128)
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    work_dir = args.work_dir
    batch_size = args.batch_size
    run(['sudo', 'chmod', '777', work_dir])

    # check pdf
    txt_file = glob(osp.join(work_dir, '*.txt'))[0]

    # split sentences
    with open(txt_file, 'r', encoding='utf-8') as f:
        sentences = f.read().split('\n')
    print(f'Split text to {len(sentences)} sentences.')
    
    # load model
    path = '/group/40048/jaronfei/models/ChineseErrorCorrector2-7B'
    tokenizer = AutoTokenizer.from_pretrained(path)
    sampling_params = SamplingParams(seed=42,max_tokens=512)
    llm = LLM(model=path)

    # check
    problems = []
    split_idx = list(range(0, len(sentences), batch_size)) + [len(sentences)]
    for start, end in tqdm(zip(split_idx[:-1], split_idx[1:]), total=len(split_idx) - 1):
        messages = [
            [
                {"role": "user", "content": "你是一个文本纠错专家，纠正输入句子中的语法错误，并输出正确的句子，输入句子为：" + s}
            ] for s in sentences[start:end]
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # generate outputs
        outputs = llm.generate(text, sampling_params)

        # collect error
        for src, tgt in zip(sentences[start:end], outputs):
            tgt = tgt.outputs[0].text
            if src != tgt:
                problems.append(dict(
                    source=src,
                    target=tgt
                ))
    # save
    with open(osp.join(work_dir, 'tw_nlp_problems.json'), 'w', encoding='utf-8') as f:
        json.dump(problems, f, indent=4, ensure_ascii=False)

    # visualize
    visualize_str = '\n'.join(visualize_diff(item['source'], item['target']) for item in problems) + '\n'
    with open(osp.join(work_dir, 'tw_nlp_problems'), 'w', encoding='utf-8') as f:
        f.write(visualize_str)
