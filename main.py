import sys #导入这个模块用来关闭系统
import os
import time
from models import InventoryManager,BaseProduct,PerishableProduct,InsufficientStockError,UserManager
from utils import (validate_product_id,validate_password,quick_sort_inventory,
                   show_inventory_table,plot_inventory_chart,search_product,export_to_csv)
# 清屏函数
def clear_screen(wait=True):
    if wait:
        input("\n👉 按 Enter 键继续...")
    os.system('cls' if os.name == 'nt' else 'clear')
# 身份确认菜单
def auth_menu(auth_mgr):
    wait = False
    while True:
        clear_screen(wait)
        wait = True
        print("\n"+"*"*35)
        print("🔐 欢迎使用Luck007的仓库管理系统")
        print("1. 🔑 账号登录")
        print("2. 📝 注册普通员工账号")
        print("3. 👑 注册系统管理员账号 (需内部邀请码)")
        print("0. 🚪 退出程序")
        print("*"*35)

        choice = input("请选择操作（0-3）：").strip()

        if choice == "1":
            username = input("👤 请输入用户名: ").strip()
            password = input("🔑 请输入密  码: ").strip()
            success,role,msg = auth_mgr.login(username,password)
            if success:
                print(f"\n🎉 {msg} 欢迎回来，{username}！")
                return username,role
            else:
                print(f"❌ 登录失败: {msg}")
        elif choice in ["2","3"]:
            role = "employee" if choice == "2" else "admin"
            if role == "admin":
                code = input("请输入管理员邀请码：").strip()
                if code!="admin0402":
                    print("❌ 邀请码错误，拒绝注册管理员！")
                    continue

            username = input("请设置用户名：").strip()
            password = input("请设置密码（至少六位数必须包含数字和字母）").strip()

            if not validate_password(password):
                print("❌ 密码格式不符要求！必须包含字母和数字，且至少6位。")
                continue
            success,msg = auth_mgr.register(username,password)
            if success:
                print(f"✅ {msg} 请返回登录。")
            else:
                print(f"❌ {msg}")

        elif choice == "0":
            print("👋 感谢使用，再见！")
            sys.exit(0)
        else:
            print("❌ 输入无效，请重新选择！")


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
        name = input("商品名称：").strip()
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
            print(f"✅ 新商品 {name} 成功建档并入库！")
        except ValueError:
            print("❌ 价格或天数必须是数字！操作失败。")

def handle_outbound(manager):
    pid = input("请输入商品ID：").strip().upper()
    try:
        qty = int(input("请输入出库数量").strip())
        manager.outbound(pid,qty)
        print(f"✅ 成功出库 {qty} 件！")
    except ValueError:
        print("❌ 输入错误: 数量必须是整数。")
    except KeyError as e:
        print(f"❌ 错误: {e}")
    except InsufficientStockError as e:
        print(f"⚠️ 业务拦截: {e}")

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

    print("\n请选择排序依据：")
    print("1. 📦 按库存数量 (默认)")
    print("2. 💰 按商品单价")
    key_choice = input("请输入选项（1-2）:").strip()
    sort_key = "price" if key_choice == "2" else "quantity"

    print("\n请选择排序方式：")
    print("1. ⬆️ 升序 / 从小到大 (默认)")
    print("2. ⬇️ 降序 / 从大到小")
    order_choice = input("请输入选项（1-2）：").strip()
    reverse_order = True if order_choice == "2" else False

    sorted_products = quick_sort_inventory(products,key=sort_key,reverse=reverse_order)
    print(f"\n📊 当前库存（按 {'单价' if sort_key=='price' else '库存数量'}"
          f"{'降序' if reverse_order else '升序'}排列）：")
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
        print(f"[{log["time"]}] 操作人:{log["operator"]} | {log["action"]} - 商品:{log["pid"]} - 数量:{log['quantity']} - 状态:{log['status']}")


def main():
    auth_mgr = UserManager()
    current_user,role = auth_menu(auth_mgr)
    role_name="管理员" if role == "admin" else "普通员工"
    manager = InventoryManager(current_user=current_user)  # 实例化写好的管理器（自动读取JSON文件）
    wait = False
    while True:
        clear_screen(wait)
        wait = True
        print("\n"+"="*35)
        print(f"  仓库管理系统主菜单 | 登录用户：{current_user} [{role_name}]  ")
        print("="*35)
        print("1. ➕ 商品入库 (新增/补货)")
        print("2. ➖ 商品出库")
        print("3. 🔍 检索商品 (名称/ID)")
        print("4. 📋 查看库存总览 ")
        print("5. ⚠️ 系统智能预警 (缺货/临期)")
        print("6. 📊 生成库存可视化图表")
        if role == "admin":
            print("7. 🗑️ 商品下架删除 (仅限管理员)")
            print("8. 💾 导出库存到 CSV 文件 (仅限管理员)")
            print("9. 📜 查看操作日志 (仅限管理员)")
        print("0. 🚪 注销当前帐号并退出")
        print("="*35)

        choice = input("请输入操作编号（0-9）：").strip()
        if choice == "1":
            handle_inbound(manager)
        elif choice == "2":
            handle_outbound(manager)
        elif choice == "3":
            handle_search(manager)
        elif choice == "4":
            handle_view(manager)
        elif choice == "5":
            handle_warnings(manager)
        elif choice == "6":
            products = list(manager.inventory.values())
            plot_inventory_chart(products)
        elif choice in ["7","8","9"]:
            if role != "admin":
                print("⛔ 越权访问被拒绝！您当前的身份是【普通员工】，无权执行此操作。")
            else:
                if choice == "7":
                    handle_delete(manager)
                elif choice == "8":
                    handle_export(manager)
                elif choice == "9":
                    handle_logs(manager)

        elif choice == "0":
            print("💾 正在保存数据...")
            manager.save_data()
            print("👋 已安全注销，再见！")
            sys.exit(0)
        else:
            print("❌ 输入错误，请输入 0-9 之间的数字")

if __name__ == '__main__':
    main()