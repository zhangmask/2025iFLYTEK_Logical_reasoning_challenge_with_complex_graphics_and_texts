# fix.py
import os
import csv
import chardet

FILE = 'output.csv'
TEMP = FILE + '.tmp'

# 1. 先用 chardet 猜编码
with open(FILE, 'rb') as f:
    raw = f.read()
src_enc = chardet.detect(raw)['encoding'] or 'gbk'
print(f'检测到源编码：{src_enc}')

# 2. 以 errors='ignore' 方式读取并强制转 UTF-8 无 BOM
with open(FILE, 'r', encoding=src_enc, errors='ignore') as f_in, \
     open(TEMP, 'w', newline='', encoding='utf-8') as f_out:
    writer = csv.writer(f_out)
    for row in csv.reader(f_in):
        writer.writerow(row)

os.replace(TEMP, FILE)
print(f'{FILE} 已修复为 UTF-8 无 BOM')