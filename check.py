#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================
@author: Jaron
@time: 2025/03/08 16:06:04
@email: fjjth98@163.com
@description:
================================================
"""
import json
import os.path as osp
from argparse import ArgumentParser
from difflib import SequenceMatcher
from glob import glob
from subprocess import run

from pycorrector.gpt.gpt_corrector import GptCorrector


print('Load models...')
correctors = {
    'chinese-text-correction-7b': GptCorrector('checkpoints/chinese-text-correction-7b')
}


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

    # correct and save
    for name, corrector in correctors.items():
        print(f'Start {name} corrector...')
        problems = []
        for i in corrector.correct_batch(sentences):
            # filter out non-chinese error
            if len(i['errors']) > 0:
                problems.append(i)
        with open(osp.join(work_dir, f'{name}_problems.json'), 'w', encoding='utf-8') as f:
            json.dump(problems, f, indent=4, ensure_ascii=False)

        # visualize
        visualize_str = '\n'.join(visualize_diff(item['source'], item['target']) for item in problems) + '\n'
        with open(osp.join(work_dir, f'{name}_problems'), 'w', encoding='utf-8') as f:
            f.write(visualize_str)
