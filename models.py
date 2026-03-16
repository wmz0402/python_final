import json    # 序列化
import time    # 记录日志
import os      # 设置文件历经
from utils import hash_password

#定义文件夹名
DATA_DIR = "data"
# 定义库存数据文件路径
INVENTORY_FILE = "data/inventory.json"
# 定义日志数据文件路径
LOG_FILE = "data/log.json"
# 储存用户信息
USERS_FILE = "data/users.json"

# 如果文件不存在自动创建
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 定义异常类
class InsufficientStockError(Exception):
    pass

# 用户与权限管理
class UserManager:
    def __init__(self):
        self.users = {}
        self.load_users()

        if not self.users:
            self.register("admin","admin0402","admin")

    def load_users(self):
        try:
            with open(USERS_FILE,"r",encoding="UTF-8") as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}

    def save_users(self):
        with open(USERS_FILE,"w",encoding="UTF-8") as f:
            json.dump(self.users,f,ensure_ascii=False,indent=4)

    def register(self,username,password,role="employee"):
        if username in self.users:
            return False,"用户名已存在！"
        self.users[username] = {
            "password":hash_password(password),
            "role":role,
        }
        self.save_users()
        return True,"注册成功！"

    def login(self,username,password):
        if username not in self.users:
            return False,None,"用户不存在！"
        if self.users[username]["password"] != hash_password(password):
            return False,None,"密码错误！"
        return True,self.users[username]["role"],"登陆成功！"

# 商品类
class BaseProduct:
    def __init__(self,pid,name,price,quantity):
        self.pid = pid
        self.name = name
        self.price = float(price)
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
        def __init__(self,current_user = "System"):
            self.inventory = {}
            self.logs = []
            self.current_user = current_user # 记录当前登录用户
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
                data =[obj.to_dict() for obj in self.inventory.values()]  # 把对象转化成字典列表
                json.dump(data, f, ensure_ascii=False, indent=4)  # 写入JSON文件，防止中文乱码

            with open(LOG_FILE, "w",encoding="UTF-8") as f:
                json.dump(self.logs, f, ensure_ascii=False, indent=4)

        def log_transaction(self,action,pid,qty,status):
            record = {
                "time":time.strftime("%Y-%m-%d %H:%M:%S"),
                "operator":self.current_user,
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
                raise InsufficientStockError(f"库存不足！当前{self.inventory[pid].name}"
                                             f"仅剩{self.inventory[pid].quantity}件")

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
            self.log_transaction("下架删除",pid,0,"成功")
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
























