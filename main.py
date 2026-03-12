import sys #导入这个模块用来关闭系统
from models import InventoryManager,BaseProduct,PerishableProduct,InsufficientStockError
from utils import (validate_product_id,quick_sort_inventory,
                   show_inventory_table,plot_inventory_chart,search_product,export_to_csv)

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
            handle_search(manager)
        elif choice == "4":
            handle_view(manager)
        elif choice == "5":
            handle_warnings(manager)
        elif choice == "6":
            products = list(manager.inventory.values())
            plot_inventory_chart(products)
        elif choice == "7":
            handle_delete(manager)
        elif choice == "8":
            handle_export(manager)
        elif choice == "9":
            handle_logs(manager)
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
        show_inventory_table(results)
    else:
        print("🈳 未找到匹配的商品。")

def handle_view(manager):
    products = list(manager.inventory.values())
    if not products:
        print("🈳 当前仓库为空。")
        return
    sorted_products = quick_sort_inventory(products,key="quantity")
    show_inventory_table(sorted_products)

def handle_warnings(manager):
    warnings = manager.get_system_warnings()
    if not warnings:
        print("✅ 当前系统状态良好，暂无预警。")
    else:
        print("\n=== 📢 系统预警 ===")
        for w in warnings:
            print(w)
        print("=================")

def handle_delete(manager):
    pid = input("请输入要下架的商品ID：").strip().upper()
    try:
        manager.delete_product(pid)
        print(f"✅ 商品 {pid} 已成功下架并删除。")
    except (KeyError,ValueError) as e:
        print(f"❌ 删除失败: {e}")

def handle_export(manager):
    products = list(manager.inventory.values())
    if export_to_csv(products):
        print("✅ 库存数据已成功导出到 data/inventory_export.csv")
    else:
        print("🈳 仓库为空，无需导出。")


def handle_logs(manager):
    if not manager.logs:
        print("🈳 暂无日志记录。")
        return
    print("\n--- 近期操作日志 ---")
    for log in manager.logs[-10:]:
        print(f"[{log["time"]}] {log["action"]} - 商品:{log["pid"]} - 数量:{log['quantity']} - 状态:{log['status']}")

if __name__ == '__main__':
    main()