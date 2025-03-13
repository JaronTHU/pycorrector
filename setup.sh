#!/bin/bash
# *********************************************************
# * author: Jaron
# * time: 2025/03/08 16:06:36
# * email: fjjth98@163.com
# * description: 
# *********************************************************

# pycorrector
pip install -e .
pip install -U pip accelerate vllm==0.5.1
pip install /group/40048/jaronfei/wheels/flash_attn-2.7.4.post1+cu12torch2.3cxx11abiFALSE-cp310-cp310-linux_x86_64.whl 
pip uninstall -y tensorflow xformers

# download checkpoint
# HF_HUB_ENABLE_HF_TRANSFER=1 huggingface-cli download shibing624/chinese-text-correction-7b --local-dir checkpoints/chinese-text-correction-7b
