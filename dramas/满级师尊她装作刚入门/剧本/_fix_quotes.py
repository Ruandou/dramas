#!/usr/bin/env python3
"""Fix ALL ASCII double quotes used as Chinese emphasis marks in _gen_yaml.py"""
import re

with open('_gen_yaml.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern: a CJK/punctuation char followed by ASCII " then CJK word then ASCII "
# This catches both inside brackets and in visual descriptions
# Replace with Unicode single quotes
pattern = re.compile(r'([\u4e00-\u9fff\u300c\u300d\u2014\u2026\uff01\uff1f\u3002])\"([\u4e00-\u9fff]+)\"')

for _ in range(5):
    new_content = pattern.sub(r'\1\u2018\2\u2019', content)
    if new_content == content:
        break
    content = new_content

with open('_gen_yaml.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
