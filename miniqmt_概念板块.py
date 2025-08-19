import os
import json
from xtquant import xtdata

xtdata.enable_hello = False

# 下载最新板块分类信息（建议初始化时调用）
xtdata.download_sector_data()
# 获取所有板块名称
sectors = xtdata.get_sector_list()
if not os.path.exists('data'):
    os.makedirs('data')
path = 'data/qmt_概念板块.txt'
save_to_local = True
if save_to_local:
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sectors))

data = {s: xtdata.get_stock_list_in_sector(s) for s in sectors}

with open('data/qmt_概念板块.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('保存完毕！')
