import sys #导入这个模块用来关闭系统
from idlelib.debugger_r import restart_subprocess_debugger
from typing import is_protocol

from models import InventoryManager,BaseProduct,PerishableProduct,InsufficientStockError
from utils import *

def main():
    manager = InventoryManager()  # 实例化写好的管理器（自动读取JSON文件）
    while True:
        print("\n"+"="*35)
        print("  欢迎使用仓库进销存管理系统  ")
        print("1. ➕ 商品入库 (新增/补货)")
        print("2. ➖ 商品出库")
        print("3. 🔍 检索商品 (名称/ID)")
        print("4. 📋 查看库存总览 (按库存排序)")
        print("5. ⚠️ 系统智能预警 (缺货/临期)")
        print("6. 📊 生成库存可视化图表")
        print("7. 🗑️ 商品下架删除")
        print("8. 💾 导出库存到 CSV 文件")
        print("9. 📜 查看操作日志")
        print("0. 🚪 退出系统")
        print("="*35)

        choice = input("请输入操作编号（0-9）：").strip()
        if choice == "1":
            handle_inbound(manager)
        elif choice == "2":
            handle_search(manager)
        elif choice == "3":

        elif choice == "4":

        elif choice == "5":

        elif choice == "6":

        elif choice == "7":

        elif choice == "8":

        elif choice == "9":

        elif choice == "0":
            print("💾 正在保存数据...")
            manager.save_data()
            print("👋 感谢使用，再见！")
            sys.exit(0)
        else:
            print("❌ 输入错误，请输入 0-9 之间的数字")

def handle_inbound(manager):
    pid = input("请输入产品ID（格式如P001）：").strip().upper()
    if not validate_product_id(pid):
        print("❌ 商品ID格式不正确！必须为 'P' 开头加3位数字。")
        return

    try:
        qty = int(input("请输入入库数量：").strip())
        if qty <= 0:
            raise ValueError("数量必须大于零")
    except ValueError as e:
        print(f"❌ 输入错误: {e}")
        return

    if manager.inbound(pid,qty):
        print(f"✅ {pid} 成功补货 {qty} 件！")
    else:
        print("🆕 这是一个新商品，请输入详细信息。")
        name = input("商品名称").strip()
        try:
            price = float(input("商品单价：").strip())
            is_perishable = input("是否为易腐商品？（y/n）:").strip().lower()
            if is_perishable == "y":
                days = int(input("请输入保质期（天）").strip())
                new_product = PerishableProduct(pid,name,price,qty,days)
            else:
                new_product = BaseProduct(pid,name,price,qty)

            manager.inventory[pid] = new_product
            manager.log_transaction("新增入库",pid,qty,"成功")
            manager.save_data()
            print(f"✅ 新商品 {name} 成功入库！")
        except ValueError:
            print("❌ 价格或天数必须是数字！操作失败。")

def handle_search(manager):
    keyword = input("请输入要搜索的关键字（商品ID或名称）：").strip()
    products = list(manager.inventory.values())
    results = search_product(products,keyword)
    if results:
        print(f"\n🔍 找到 {len(results)} 条匹配记录：")
