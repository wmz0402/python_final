import json    # 序列化
import time    # 记录日志
import os      # 设置文件历经

#定义文件夹名
DATE_DIR = "date"
# 定义库存数据文件路径
INVENTORY_FILE = "date/inventory.json"
# 定义日志数据文件路径
LOG_FILE = "date/log.json"

# 如果文件不存在自动创建
if not os.path.exists(DATE_DIR):
    os.mkdir(DATE_DIR)

# 定义异常类
class InsufficientStockError:
    pass

# 商品类
class BaseProduct:
    def __init__(self,pid,name,price,quantity):
        self.pid = pid
        self.name = name
        self.prize = float(price)
        self.quantity =int(quantity)

    def get_type(self):
        return "普通商品"

    def to_dict(self):        #将对象转化成字典
        return {"pid": self.pid, "name": self.name, "price": self.price, "quantity": self.quantity,
                "type": self.get_type()}

# 易腐产品
class PerishableProduct(BaseProduct):
    def __init__(self,pid,name,price,quantity,expiration_days):
        super().__init__(pid,name,price,quantity)      #调用父类的构造方法
        self.expiration_days = expiration_days

    def get_type(self):
        return f"易腐产品（保质期{self.expiration_days}天）"

    def to_dict(self):
        data = super().to_dict()
        data["expiration_days"] = self.expiration_days
        return data

# 库存管理器
class InventoryManager:
        def __init__(self):
            self.inventory = {}
            self.logs = []
            self.load_data()  #初始化时直接自动读取硬盘数据
           # 文件读取与异常处理
        def load_data(self):
            try:
                with open(INVENTORY_FILE, "r",encoding="UTF-8") as f:
                    data = json.load(f)   # 把JSON文本转成Python列
                    for item in data:
                        if "expiration_days" in item:
                            # 实例化为易腐商品子类
                            obj = PerishableProduct(item["pid"],item["name"],item["price"],
                                                    item["quantity"],item["expiration_days"])
                        else:
                            # 否则实例化为普通商品父类
                            obj = BaseProduct(item["pid"],item["name"],item["price"],item["quantity"])
                        self.inventory[item["pid"]] = obj # 存入库存字典
            except FileNotFoundError:     # 文件第一次没找到
                pass                       # 字节跳过不报错
            except json.JSONDecodeError:  # 如果文件被手动乱改导致格式错误
                print("⚠️ 警告：数据文件损坏，已初始化为空库存。")

            try:
                with open(LOG_FILE, "r",encoding="UTF-8") as f:
                    self.logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                self.logs = []
        # 文件的写入
        def save_data(self):
            with open(INVENTORY_FILE, "w",encoding="UTF-8") as f:
                data = [obj.to_dict() for obj in self.inventory]  # 把对象转化成字典列表
                json.dump(data, f, ensure_ascii=False, indent=4)  # 写入JSON文件，防止中文乱码

            with open(LOG_FILE, "w",encoding="UTF-8") as f:
                json.dump(self.logs, f, ensure_ascii=False, indent=4)

        def log_transaction(self,action,pid,qty,status):
            record = {
                "time":time.strftime("%Y-%m-%d %H:%M:%S"),
                "action":action,
                "pid":pid,
                "quantity":qty,
                "status":status
            }
            self.logs.append(record)
            self.save_data()

        def inbound(self,pid,qty):
            if pid in self.inventory:
                self.inventory[pid].quantity += qty
                self.log_transaction("入库",pid,qty,"成功")
                return True
            return False

        def outbound(self,pid,qty):
            if pid not in self.inventory:
                raise KeyError(f"商品ID{pid}不存在")

            if self.inventory[pid].quantity < qty:
                self.log_transaction("出库",pid,qty,"失败")
                raise InsufficientStockError(f"库存不足！当前{self.inventory[pid].name}仅剩{self.inventory[pid].quantity}件")

            self.inventory[pid].quantity -= qty
            self.log_transaction("出库",pid,qty,"成功")
            self.save_data()

        # 删除下架商品
        def delete_product(self,pid):
            if pid not in self.inventory:
                raise KeyError(f"商品ID{pid}不存在")
            if self.inventory[pid].quantity > 0:
                raise ValueError(f"无法下架！商品{self.inventory[pid].name}仍有库存{self.inventory[pid].quantity}件，请先完成出库")

            del self.inventory[pid]
            self.log_transaction("下架",pid,0,"完成")
            self.save_data()

        # 库存不足，临期预警
        def get_system_warnings(self):
            warnings = []
            for p in self.inventory.values():
                # 库存预警
                if p.quantity < 5:
                    warnings.append(f"🔴[库存紧张] {p.name}({p.pid}) 库存仅剩 {p.quantity} 件，"
                                    f"请及时补货！")
                # 临期预警
                if isinstance(p,PerishableProduct) and p.expiration_days <= 7:
                    warnings.append(f"🟡 [临期预警] {p.name}({p.pid}) 剩余保质期仅 {p.expiration_days} 天！")
            return warnings
























