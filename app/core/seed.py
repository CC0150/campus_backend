from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.shop import Shop
from app.models.dish import Dish
from app.models.user import User


# ═══════════════════════════════════════════════════════════
# 8 大美食专栏 × 每栏 2 家店铺 = 16 家店铺
# 店铺名包含分类关键词（前 2 字），确保金刚区点击筛选生效
# ═══════════════════════════════════════════════════════════

SHOP_SEEDS = [
    # ────── 1. 精品正餐（2 家）─────────────────────
    Shop(
        id="1",
        name="精品·西苑手工面馆",
        rating=4.8,
        sales=980,
        min_order=12.0,
        delivery_fee=2.0,
        delivery_time=25,
        notice="本店所有面食纯手工制作，请耐心等待",
        image="https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=128&h=128&fit=crop&crop=center",
        tags=["校园老字号", "准时达", "精品正餐"],
        discount="满20减5",
        bulletin="🔥 老北京炸酱面 月售1000+份！",
    ),
    Shop(
        id="2",
        name="精品·东门湘味小炒",
        rating=4.5,
        sales=960,
        min_order=15.0,
        delivery_fee=3.0,
        delivery_time=30,
        notice="正宗湘味，辣度可调",
        image="https://images.unsplash.com/photo-1544025162-d76694265947?w=128&h=128&fit=crop&crop=center",
        tags=["校园老字号", "下饭神器", "精品正餐"],
        discount="满30减8",
        bulletin="🌶 辣椒炒肉 + 米饭 仅售 13 元",
    ),

    # ────── 2. 原豆咖啡（2 家）─────────────────────
    Shop(
        id="3",
        name="原豆·瑞幸咖啡校园店",
        rating=4.7,
        sales=990,
        min_order=9.0,
        delivery_fee=1.0,
        delivery_time=15,
        notice="专业咖啡，现磨现送",
        image="https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=128&h=128&fit=crop&crop=center",
        tags=["人气爆款", "准时达", "原豆咖啡"],
        discount="首杯立减5元",
        bulletin="☕ 生椰拿铁 校园爆款！",
    ),
    Shop(
        id="4",
        name="原豆·星巴克咖啡服务站",
        rating=4.9,
        sales=970,
        min_order=15.0,
        delivery_fee=1.0,
        delivery_time=18,
        notice="星巴克品质，校园直达",
        image="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=128&h=128&fit=crop&crop=center",
        tags=["品质精选", "准时达", "原豆咖啡"],
        discount="满30减6",
        bulletin="🌟 星冰乐系列全新上线！",
    ),

    # ────── 3. 甜品冰淇淋（2 家）───────────────────
    Shop(
        id="5",
        name="甜品·DQ冰雪皇后校园店",
        rating=4.8,
        sales=990,
        min_order=10.0,
        delivery_fee=2.0,
        delivery_time=20,
        notice="暴风雪倒杯不洒，冰凉爽滑",
        image="https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=128&h=128&fit=crop&crop=center",
        tags=["人气爆款", "夏季必选", "甜品冰淇淋"],
        discount="第二杯半价",
        bulletin="🍦 暴风雪系列 全新口味上线！",
    ),
    Shop(
        id="6",
        name="甜品·鲜芋仙台式甜水铺",
        rating=4.6,
        sales=920,
        min_order=12.0,
        delivery_fee=2.0,
        delivery_time=22,
        notice="手工芋圆，台湾古早味",
        image="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=128&h=128&fit=crop&crop=center",
        tags=["品质精选", "健康甜品", "甜品冰淇淋"],
        discount="满25减4",
        bulletin="🍡 招牌芋圆4号 限时特惠！",
    ),

    # ────── 4. 西式快餐（2 家）─────────────────────
    Shop(
        id="7",
        name="西式·麦德堡校园汉堡店",
        rating=4.4,
        sales=990,
        min_order=12.0,
        delivery_fee=2.0,
        delivery_time=20,
        notice="经典汉堡，现点现做",
        image="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=128&h=128&fit=crop&crop=center",
        tags=["人气爆款", "准时达", "西式快餐"],
        discount="满25减5",
        bulletin="🍔 巨无霸套餐 限时特价19.9！",
    ),
    Shop(
        id="8",
        name="西式·必胜客披萨校园站",
        rating=4.6,
        sales=980,
        min_order=20.0,
        delivery_fee=3.0,
        delivery_time=28,
        notice="手工拍制披萨，芝士拉丝",
        image="https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=128&h=128&fit=crop&crop=center",
        tags=["品质精选", "聚餐首选", "西式快餐"],
        discount="满50减12",
        bulletin="🍕 超级至尊披萨 全新升级！",
    ),

    # ────── 5. 麻辣烫/锅（2 家）───────────────────
    Shop(
        id="9",
        name="麻辣·杨国福麻辣烫校园店",
        rating=4.5,
        sales=990,
        min_order=10.0,
        delivery_fee=2.0,
        delivery_time=22,
        notice="骨汤熬制，自由搭配",
        image="https://images.unsplash.com/photo-1563379926898-05f4575a45d8?w=128&h=128&fit=crop&crop=center",
        tags=["校园老字号", "下饭神器", "麻辣烫锅"],
        discount="满20减4",
        bulletin="🔥 新品番茄骨汤底 限时上线！",
    ),
    Shop(
        id="10",
        name="麻辣·转转小火锅工坊",
        rating=4.3,
        sales=940,
        min_order=15.0,
        delivery_fee=3.0,
        delivery_time=30,
        notice="一人一锅，干净卫生",
        image="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=128&h=128&fit=crop&crop=center",
        tags=["特色美食", "聚餐首选", "麻辣烫锅"],
        discount="满30减6",
        bulletin="🍲 牛油麻辣锅底 今日特惠！",
    ),

    # ────── 6. 暖胃靓汤（2 家）─────────────────────
    Shop(
        id="11",
        name="暖胃·老火靓汤炖品世家",
        rating=4.7,
        sales=880,
        min_order=10.0,
        delivery_fee=2.0,
        delivery_time=25,
        notice="文火慢炖四小时，汤浓味鲜",
        image="https://images.unsplash.com/photo-1547592166-23ac45744acd?w=128&h=128&fit=crop&crop=center",
        tags=["品质精选", "健康养生", "暖胃靓汤"],
        discount="满20减4",
        bulletin="🍲 花旗参炖竹丝鸡 滋补上线！",
    ),
    Shop(
        id="12",
        name="暖胃·阿婆牛杂汤粉馆",
        rating=4.5,
        sales=970,
        min_order=8.0,
        delivery_fee=1.0,
        delivery_time=20,
        notice="岭南传统牛杂，汤底浓郁",
        image="https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=128&h=128&fit=crop&crop=center",
        tags=["校园老字号", "人气爆款", "暖胃靓汤"],
        discount="满15减3",
        bulletin="🐂 招牌萝卜牛杂 今日特价！",
    ),

    # ────── 7. 下午茶点（2 家）─────────────────────
    Shop(
        id="13",
        name="下午茶·奶茶星球 Bubble Planet",
        rating=4.9,
        sales=990,
        min_order=8.0,
        delivery_fee=1.0,
        delivery_time=15,
        notice="现做现送，冰爽直达",
        image="https://images.unsplash.com/photo-1559496417-e7f25cb247f3?w=128&h=128&fit=crop&crop=center",
        tags=["人气爆款", "准时达", "下午茶点"],
        discount="第二杯半价",
        bulletin="🧋 杨枝甘露 全场最佳！",
    ),
    Shop(
        id="14",
        name="下午茶·好利来烘焙工坊",
        rating=4.6,
        sales=950,
        min_order=10.0,
        delivery_fee=2.0,
        delivery_time=22,
        notice="精选原料，每日现烤",
        image="https://images.unsplash.com/photo-1509365465985-25d11c17e812?w=128&h=128&fit=crop&crop=center",
        tags=["品质精选", "健康甜品", "下午茶点"],
        discount="满20减5",
        bulletin="🥐 可颂面包 新鲜出炉 限时抢购！",
    ),

    # ────── 8. 生日蛋糕（2 家）─────────────────────
    Shop(
        id="15",
        name="生日·幸福西饼蛋糕定制",
        rating=4.8,
        sales=850,
        min_order=25.0,
        delivery_fee=3.0,
        delivery_time=40,
        notice="提前2小时预约，新鲜现做",
        image="https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=128&h=128&fit=crop&crop=center",
        tags=["品质精选", "节日必备", "生日蛋糕"],
        discount="满50减10",
        bulletin="🎂 水果鲜奶蛋糕 买一送一！",
    ),
    Shop(
        id="16",
        name="生日·巴黎贝甜烘焙坊",
        rating=4.7,
        sales=820,
        min_order=20.0,
        delivery_fee=3.0,
        delivery_time=35,
        notice="法式甜品工艺，精致美味",
        image="https://images.unsplash.com/photo-1550617931-e17a7b70dce2?w=128&h=128&fit=crop&crop=center",
        tags=["品质精选", "节日必备", "生日蛋糕"],
        discount="满40减8",
        bulletin="🧁 红丝绒蛋糕 校园首发！",
    ),
]

DISH_SEEDS = [
    # ═══════════════════════════════════════════════════════
    # 1. 精品·西苑手工面馆 (shop_id=1)
    # ═══════════════════════════════════════════════════════
    Dish(id="101", name="招牌牛肉拉面", price=15.0, image="🍜", category="拉面", sales=980, shop_id="1"),
    Dish(id="102", name="香菇滑鸡双拼饭", price=14.0, image="🍛", category="米饭", sales=856, shop_id="1"),
    Dish(id="103", name="老北京炸酱面", price=12.0, image="🍝", category="拌面", sales=890, shop_id="1"),
    Dish(id="104", name="番茄鸡蛋刀削面", price=10.0, image="🥘", category="汤面", sales=678, shop_id="1"),

    # ═══════════════════════════════════════════════════════
    # 2. 精品·东门湘味小炒 (shop_id=2)
    # ═══════════════════════════════════════════════════════
    Dish(id="201", name="辣椒炒肉", price=16.0, image="🌶️", category="小炒", sales=960, shop_id="2"),
    Dish(id="202", name="剁椒鱼头", price=28.0, image="🐟", category="大菜", sales=890, shop_id="2"),
    Dish(id="203", name="蒜蓉西兰花", price=10.0, image="🥦", category="素菜", sales=543, shop_id="2"),
    Dish(id="204", name="农家小炒肉盖饭", price=15.0, image="🍖", category="盖饭", sales=920, shop_id="2"),

    # ═══════════════════════════════════════════════════════
    # 3. 原豆·瑞幸咖啡校园店 (shop_id=3)
    # ═══════════════════════════════════════════════════════
    Dish(id="301", name="生椰拿铁", price=13.0, image="🥥", category="拿铁", sales=990, shop_id="3"),
    Dish(id="302", name="美式咖啡", price=9.0, image="☕", category="美式", sales=880, shop_id="3"),
    Dish(id="303", name="陨石厚乳拿铁", price=16.0, image="💫", category="拿铁", sales=890, shop_id="3"),
    Dish(id="304", name="橙C美式", price=12.0, image="🍊", category="美式", sales=670, shop_id="3"),

    # ═══════════════════════════════════════════════════════
    # 4. 原豆·星巴克咖啡服务站 (shop_id=4)
    # ═══════════════════════════════════════════════════════
    Dish(id="401", name="焦糖玛奇朵", price=18.0, image="🍮", category="玛奇朵", sales=980, shop_id="4"),
    Dish(id="402", name="抹茶星冰乐", price=20.0, image="🍵", category="星冰乐", sales=850, shop_id="4"),
    Dish(id="403", name="拿铁咖啡", price=15.0, image="☕", category="拿铁", sales=760, shop_id="4"),
    Dish(id="404", name="冷萃冰咖啡", price=17.0, image="🧊", category="冷萃", sales=540, shop_id="4"),

    # ═══════════════════════════════════════════════════════
    # 5. 甜品·DQ冰雪皇后校园店 (shop_id=5)
    # ═══════════════════════════════════════════════════════
    Dish(id="501", name="奥利奥暴风雪", price=18.0, image="🍪", category="暴风雪", sales=990, shop_id="5"),
    Dish(id="502", name="草莓华夫脆", price=20.0, image="🍓", category="暴风雪", sales=920, shop_id="5"),
    Dish(id="503", name="巧克力甜筒", price=8.0, image="🍫", category="甜筒", sales=980, shop_id="5"),
    Dish(id="504", name="芒果冰沙", price=15.0, image="🥭", category="冰沙", sales=730, shop_id="5"),

    # ═══════════════════════════════════════════════════════
    # 6. 甜品·鲜芋仙台式甜水铺 (shop_id=6)
    # ═══════════════════════════════════════════════════════
    Dish(id="601", name="招牌芋圆4号", price=16.0, image="🍡", category="芋圆", sales=820, shop_id="6"),
    Dish(id="602", name="红豆豆花", price=12.0, image="🫘", category="豆花", sales=780, shop_id="6"),
    Dish(id="603", name="仙草冻奶茶", price=14.0, image="🧋", category="奶茶", sales=650, shop_id="6"),
    Dish(id="604", name="芒果冰沙", price=15.0, image="🥭", category="冰沙", sales=430, shop_id="6"),

    # ═══════════════════════════════════════════════════════
    # 7. 西式·麦德堡校园汉堡店 (shop_id=7)
    # ═══════════════════════════════════════════════════════
    Dish(id="701", name="巨无霸牛肉堡", price=19.0, image="🍔", category="汉堡", sales=990, shop_id="7"),
    Dish(id="702", name="香辣鸡腿堡", price=15.0, image="🍗", category="汉堡", sales=950, shop_id="7"),
    Dish(id="703", name="黄金鸡块（10块装）", price=18.0, image="✨", category="小食", sales=860, shop_id="7"),
    Dish(id="704", name="薯条大份", price=10.0, image="🍟", category="小食", sales=780, shop_id="7"),

    # ═══════════════════════════════════════════════════════
    # 8. 西式·必胜客披萨校园站 (shop_id=8)
    # ═══════════════════════════════════════════════════════
    Dish(id="801", name="超级至尊披萨（9寸）", price=42.0, image="🍕", category="披萨", sales=890, shop_id="8"),
    Dish(id="802", name="夏威夷风情披萨（9寸）", price=38.0, image="🍍", category="披萨", sales=760, shop_id="8"),
    Dish(id="803", name="意式肉酱面", price=22.0, image="🍝", category="意面", sales=650, shop_id="8"),
    Dish(id="804", name="芝士焗饭", price=20.0, image="🧀", category="焗饭", sales=510, shop_id="8"),

    # ═══════════════════════════════════════════════════════
    # 9. 麻辣·杨国福麻辣烫校园店 (shop_id=9)
    # ═══════════════════════════════════════════════════════
    Dish(id="901", name="自选麻辣烫（荤素搭配）", price=18.0, image="🥘", category="麻辣烫", sales=990, shop_id="9"),
    Dish(id="902", name="番茄骨汤麻辣烫", price=20.0, image="🍅", category="麻辣烫", sales=930, shop_id="9"),
    Dish(id="903", name="酸辣粉", price=10.0, image="🍜", category="粉面", sales=980, shop_id="9"),
    Dish(id="904", name="麻辣拌", price=16.0, image="🥗", category="拌菜", sales=720, shop_id="9"),

    # ═══════════════════════════════════════════════════════
    # 10. 麻辣·转转小火锅工坊 (shop_id=10)
    # ═══════════════════════════════════════════════════════
    Dish(id="1001", name="牛油麻辣单人锅", price=25.0, image="🍲", category="火锅", sales=790, shop_id="10"),
    Dish(id="1002", name="番茄牛腩单人锅", price=28.0, image="🍅", category="火锅", sales=890, shop_id="10"),
    Dish(id="1003", name="菌菇清汤锅", price=22.0, image="🍄", category="火锅", sales=650, shop_id="10"),
    Dish(id="1004", name="自选涮菜拼盘", price=15.0, image="🥬", category="配菜", sales=780, shop_id="10"),

    # ═══════════════════════════════════════════════════════
    # 11. 暖胃·老火靓汤炖品世家 (shop_id=11)
    # ═══════════════════════════════════════════════════════
    Dish(id="1101", name="花旗参炖竹丝鸡", price=22.0, image="🐔", category="炖汤", sales=670, shop_id="11"),
    Dish(id="1102", name="椰子炖乌鸡", price=20.0, image="🥥", category="炖汤", sales=540, shop_id="11"),
    Dish(id="1103", name="淮山排骨汤", price=18.0, image="🍖", category="炖汤", sales=430, shop_id="11"),
    Dish(id="1104", name="冰糖炖雪梨", price=12.0, image="🍐", category="甜汤", sales=320, shop_id="11"),

    # ═══════════════════════════════════════════════════════
    # 12. 暖胃·阿婆牛杂汤粉馆 (shop_id=12)
    # ═══════════════════════════════════════════════════════
    Dish(id="1201", name="招牌萝卜牛杂", price=16.0, image="🐂", category="牛杂", sales=940, shop_id="12"),
    Dish(id="1202", name="牛杂汤河粉", price=14.0, image="🍜", category="汤粉", sales=980, shop_id="12"),
    Dish(id="1203", name="净云吞", price=12.0, image="🥟", category="云吞", sales=650, shop_id="12"),
    Dish(id="1204", name="牛三星汤", price=18.0, image="🍲", category="汤品", sales=430, shop_id="12"),

    # ═══════════════════════════════════════════════════════
    # 13. 下午茶·奶茶星球 Bubble Planet (shop_id=13)
    # ═══════════════════════════════════════════════════════
    Dish(id="1301", name="经典珍珠奶茶", price=10.0, image="🧋", category="奶茶", sales=990, shop_id="13"),
    Dish(id="1302", name="杨枝甘露", price=15.0, image="🥭", category="果茶", sales=950, shop_id="13"),
    Dish(id="1303", name="芝士葡萄", price=18.0, image="🍇", category="芝士茶", sales=780, shop_id="13"),
    Dish(id="1304", name="满杯红柚", price=16.0, image="🍊", category="果茶", sales=680, shop_id="13"),

    # ═══════════════════════════════════════════════════════
    # 14. 下午茶·好利来烘焙工坊 (shop_id=14)
    # ═══════════════════════════════════════════════════════
    Dish(id="1401", name="黄油可颂", price=12.0, image="🥐", category="面包", sales=980, shop_id="14"),
    Dish(id="1402", name="半熟芝士", price=18.0, image="🧀", category="蛋糕", sales=850, shop_id="14"),
    Dish(id="1403", name="蛋黄酥礼盒（4枚装）", price=22.0, image="🥮", category="糕点", sales=670, shop_id="14"),
    Dish(id="1404", name="提拉米苏杯", price=16.0, image="🍫", category="甜品", sales=540, shop_id="14"),

    # ═══════════════════════════════════════════════════════
    # 15. 生日·幸福西饼蛋糕定制 (shop_id=15)
    # ═══════════════════════════════════════════════════════
    Dish(id="1501", name="水果鲜奶蛋糕（8寸）", price=68.0, image="🎂", category="奶油蛋糕", sales=430, shop_id="15"),
    Dish(id="1502", name="黑森林蛋糕（8寸）", price=72.0, image="🍫", category="巧克力", sales=320, shop_id="15"),
    Dish(id="1503", name="芒果千层蛋糕", price=58.0, image="🥭", category="千层", sales=280, shop_id="15"),
    Dish(id="1504", name="慕斯蛋糕礼盒", price=45.0, image="🎁", category="慕斯", sales=210, shop_id="15"),

    # ═══════════════════════════════════════════════════════
    # 16. 生日·巴黎贝甜烘焙坊 (shop_id=16)
    # ═══════════════════════════════════════════════════════
    Dish(id="1601", name="红丝绒蛋糕", price=32.0, image="🧁", category="蛋糕", sales=430, shop_id="16"),
    Dish(id="1602", name="草莓奶油蛋糕卷", price=25.0, image="🍓", category="蛋糕卷", sales=350, shop_id="16"),
    Dish(id="1603", name="法式马卡龙礼盒（6枚）", price=35.0, image="🌸", category="马卡龙", sales=280, shop_id="16"),
    Dish(id="1604", name="巧克力布朗尼", price=22.0, image="🍫", category="布朗尼", sales=190, shop_id="16"),
]


def seed_data() -> None:
    db = SessionLocal()
    try:
        # ─── 商家/菜品种子 — 每次启动强制刷新 ───
        # 1. 删除旧菜品
        db.query(Dish).delete()
        # 2. 删除旧商家（注意：订单可能引用商家，若有关联需先清订单）
        db.query(Shop).delete()
        db.flush()

        # 3. 插入最新 16 家商家 + 64 道菜品
        db.add_all(SHOP_SEEDS)
        db.flush()
        db.add_all(DISH_SEEDS)
        db.flush()

        # ─── 初始用户种子 — 仅在无用户时填充 ───
        if db.query(User).count() == 0:
            admin = User(
                student_id="admin",
                name="管理员",
                password_hash=get_password_hash("123456"),
                balance=0.0,
                avatar="🛡️",
            )
            db.add(admin)

            user = User(
                student_id="23408000429",
                name="Rain",
                password_hash=get_password_hash("111111"),
                balance=50.0,
                avatar="🧑‍🎓",
            )
            db.add(user)

        # 补偿：确保 admin 账户始终存在
        if not db.query(User).filter(User.student_id == "admin").first():
            admin = User(
                student_id="admin",
                name="管理员",
                password_hash=get_password_hash("123456"),
                balance=0.0,
                avatar="🛡️",
            )
            db.add(admin)

        db.commit()
    finally:
        db.close()
