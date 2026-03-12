import re
import csv
import matplotlib.pyplot as plt   #画图
from prettytable import PrettyTable   # 美化表格
import matplotlib as mpl    # 防止中文乱码

# 设置中文汉字，防止图标乱码
mpl.rcParams['font.sans-serif'] = ['SimHei']     #默认字体为黑体
mpl.rcParams['axes.unicode_minus'] = False    # 解决保存图像是负号显示为方块的问题

# 验证产品的编码是否符合要求·
def validate_product_id(pid):
    pattern = r"^P\d{3}$"
    return bool(re.match(pattern,pid))

# 查找产品
def search_product(products,keyword):
    result = []     # 用于储存查找到的产品
    pattern = re.compile(keyword,re.IGNORECASE)  # 将关键字编译为正则对象 忽略大小写
    for p in products:
        if pattern.search(p.name) or keyword.upper() == p.pid:
            result.append(p)
    return result
#按指定键（数量或价格）对库存进行升序排列
def quick_sort_inventory(items,key="quantity"):
    if len(items) <= 1:
        return items
    pivot = items[len(items)//2]

    def get_val(obj):
        return getattr(obj,key)

    left = [x for x in items if get_val(x) < get_val(pivot)]
    



























