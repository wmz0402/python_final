import re
import csv
import hashlib
import matplotlib.pyplot as plt   #画图
from prettytable import PrettyTable   # 美化表格
import matplotlib as mpl    # 防止中文乱码

# 设置中文汉字，防止图标乱码
mpl.rcParams['font.sans-serif'] = ['SimHei']     #默认字体为黑体
mpl.rcParams['axes.unicode_minus'] = False    # 解决保存图像是负号显示为方块的问题

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# 进行加密操作
def validate_password(password):
    # 至少六位，包含字母和数字
    pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$"
    return bool(re.match(pattern,password))

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
    middle = [x for x in items if get_val(x) == get_val(pivot)]
    right = [x for x in items if get_val(x) > get_val(pivot)]

    return quick_sort_inventory(left,key) + middle + quick_sort_inventory(right,key)

def show_inventory_table(products):
    # 打印表格
    table = PrettyTable(["商品ID","名称","单价","库存数量","商品类型"])
    for p in products:
        table.add_row([p.pid,p.name,p.price,p.quantity,p.get_type()])
    print(table)

def plot_inventory_chart(products):
    if not products:
        print("暂无数据可供可视化。")
        return

    names = [p.name for p in products]
    quantities = [p.quantity for p in products]

    plt.figure(figsize=(10,6))      # 用来设置图的大小
    plt.bar(names,quantities,color="skyblue")    # 确认x，y轴的内容并给柱体选择颜色
    plt.title("当前仓库商品库存分布图")   # 标题
    plt.xlabel("商品名称")             # x轴文字说明
    plt.ylabel("库存数量")             # y轴文字说明
    plt.xticks(rotation=45)           # 使字体倾斜45°
    plt.tight_layout()                # 自动调整布局防止文字被裁掉
    plt.show()                        # 展示最终效果


# 将库存数据转化为csv的形式
def export_to_csv(products,filename="data/inventory_export.csv"):
    if not products:
        return False

    with open(filename,mode="w",encoding="utf-8-sig",newline="") as f:     # -sig使excel能够识别中文防止乱码 new是紧凑不留白
        writer = csv.writer(f)
        writer.writerow(["商品ID","商品名称","单价","库存数量","产品类型"])
        for p in products:
            writer.writerow([p.pid,p.name,p.price,p.quantity,p.get_type()])
    return True



























