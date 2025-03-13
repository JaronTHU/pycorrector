#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
==========================================================
@author: Jaron Fei
@time: 2025/03/12 18:16:23
@contact: fjjth98@163.com
@description: 
==========================================================
"""
import json
import os.path as osp
from openai import OpenAI
from argparse import ArgumentParser
from difflib import SequenceMatcher
from time import sleep


API_KEY = "9ZqBH6dmS5fZ2FCZ158ppMYl@3808"
MODELS = [
    'gpt-4o-2024-08-06',
    # 'claude-3-7-sonnet-20250219',
    # 'gemini-2.0-pro',
    # 'deepseek-v3-local'
]
INTERVAL = 300


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
    return parser.parse_args()


if __name__ == '__main__':
    
    args = parse_args()
    work_dir = args.work_dir

    client = OpenAI(base_url='http://v2.open.venus.oa.com/llmproxy/v1', api_key=API_KEY)

    # input_files = {}
    # # upload files
    # for model in MODELS:
    #     with open(osp.join(work_dir, model + '.jsonl'), 'rb') as f:
    #         input_files[model] = client.files.create(
    #             file=f,
    #             purpose='batch'
    #         ).id
    # print(json.dumps(input_files, indent=4))
    # # create tasks
    # tasks = {}
    # for model, input_file_id in input_files.items():
    #     tasks[model] = client.batches.create(
    #         input_file_id=input_file_id,
    #         endpoint='/v1/chat/completions',
    #         completion_window='24h'
    #     ).id
    # print(json.dumps(tasks, indent=4))

    tasks = {'gpt-4o-2024-08-06': 'batch_4280d2ed3845d31d'}
    # check status and save results
    while len(tasks) > 0:
        for model, task in tasks.copy().items():
            task_info = client.batches.retrieve(task)
            if task_info.status == 'completed':
                with open(osp.join(work_dir, model + '_output.jsonl'), 'w') as f:
                    f.write(client.files.content(task_info.output_file_id).content.decode('utf-8'))
                # diff input with output
                with open(osp.join(work_dir, 'paragraphs.txt'), 'r') as f:
                    srcs = f.read().split('\n')
                diff = [None for _ in srcs]
                with open(osp.join(work_dir, model + '_output.jsonl'), 'r') as f:
                    for line in f:
                        tgt_info = json.loads(line)
                        custom_id = int(tgt_info['custom_id'])
                        src = srcs[custom_id]
                        tgt = tgt_info['response']['body']['choices'][0]['message']['content']
                        if src != tgt:
                            diff[custom_id] = visualize_diff(src, tgt)
                diff = dict.fromkeys(diff)
                diff.pop(None)
                with open(osp.join(work_dir, model + '_problems'), 'w', encoding='utf-8') as f:
                    f.write('\n'.join(diff) + '\n')
                tasks.pop(model)
            elif task_info.status in {'expired', 'failed', 'cancelled'}:
                print(f'{model}\t{task}\t{task_info.status}')
                tasks.pop(model)
            else:
                print(f'{model}\t{task}\t{task_info.status}')

        sleep(INTERVAL)
    
print(task)
