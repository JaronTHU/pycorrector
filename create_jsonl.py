#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
==========================================================
@author: Jaron Fei
@time: 2025/03/12 17:54:42
@contact: fjjth98@163.com
@description: 

claude-3-7-sonnet-20250219
gpt-4o-2024-08-06
gemini-2.0-pro
deepseek-v3-local
==========================================================
"""
import json
import os.path as osp


if __name__ == '__main__':

    with open(osp.join('中文错别字校对', 'paragraphs.txt'), 'r') as f:
        texts = f.read().split('\n')

    for model in [
        'gpt-4o-2024-08-06',
        'claude-3-7-sonnet-20250219',
        'gemini-2.0-pro',
        'deepseek-v3-local'
    ]:
        s = '\n'.join(
            json.dumps(
                dict(
                    custom_id=str(i),
                    method="POST",
                    url="/v1/chat/completions",
                    body=dict(
                        model=model,
                        messages=[
                            {
                                'role': 'user',
                                'content': '你是一个文本纠错专家，请纠正以下内容中的语法错误，并直接输出纠正后正确的内容，不要输出任何评论或分析。输入内容为：\n' + text
                            }
                        ]
                    )
                ), ensure_ascii=False
            ) for i, text in enumerate(texts)
        ) + '\n'
        with open(osp.join('中文错别字校对', model + '.jsonl'), 'w', encoding='utf-8') as f:
            f.write(s)
