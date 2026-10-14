import sqlite3
import os
import random

# --- ۱. تنظیمات اولیه و دیتابیس ---
LEADERBOARD_FILE = "leaderboard.txt"


conn = sqlite3.connect('evil_game.db')
c = conn.cursor()
# اضافه کردن ستون move_counter برای مدیریت زمان باس‌ها
c.execute('''CREATE TABLE IF NOT EXISTS game (
                id INTEGER PRIMARY KEY,
                gold INTEGER,
                factories INTEGER,
                factory_cost INTEGER,
                soldiers INTEGER,
                power INTEGER,
                moves INTEGER)''')

c.execute('INSERT OR IGNORE INTO game VALUES (1, 100, 0, 50, 0, 0, 0)')
conn.commit()

# --- ۲. توابع اصلی ---

def update_game(conn, gold_delta, factory_delta, cost_delta, soldier_delta, power_delta, move_delta):
    c = conn.cursor()
    c.execute('''UPDATE game SET 
                 gold = gold + ?, factories = factories + ?, factory_cost = factory_cost + ?,
                 soldiers = soldiers + ?, power = power + ?, moves = moves + ? 
                 WHERE id=1''', 
              (gold_delta, factory_delta, cost_delta, soldier_delta, power_delta, move_delta))
    conn.commit()

def get_stats(conn):
    c = conn.cursor()
    c.execute('SELECT gold, factories, factory_cost, soldiers, power, moves FROM game WHERE id=1')
    return c.fetchone()

def save_highscore(factories):
    current_high = 0
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            try:
                content = f.read().strip()
                current_high = int(content) if content else 0
            except: current_high = 0
    if factories > current_high:
        with open(LEADERBOARD_FILE, "w") as f:
            f.write(str(factories))
        print(f"\n🏆 [رکورد جدید!!!] {factories} کارخانه!")

# --- ۳. بدنه اصلی بازی ---

print("--- 🔥 قلمرو سیاه: عصر باس‌ها 🔥 ---")
print("دستورات: [build] | [soldier] | [battle] | [exit]")

try:
    while True:
        stats = get_stats(conn)
        gold, factories, cost, soldiers, power, moves = stats
        
        # بررسی ظهور باس (هر 10 حرکت یک بار)
        boss_active = False
        if moves > 0 and moves % 10 == 0:
            boss_active = True
            print("\n" + "!"*30)
            print("🚨 경고: یک باس قدرتمند ظاهر شد! 🚨")
            print("!"*30)

        # نمایش وضعیت
        print(f"\n💰 طلا: {gold} | 🏭 کارخانه: {factories} | ⚔️ قدرت: {power} | 💂 سرباز: {soldiers}")
        if boss_active:
            print("⚠️ [وضعیت بحرانی: باس در مقابل شماست! دستور battle را بزنید!]")
        
        cmd = input("دستور شما: ").lower().strip()

        # هر حرکت کاربر، یک واحد به 'moves' اضافه می‌کند
        current_move_increment = 1

        if cmd == "build":
            if gold >= cost:
                update_game(conn, -cost, 1, 30, 0, 0, current_move_increment)
                print("✅ کارخانه ساخته شد!")
            else:
                print(f"❌ طلا کم است!")

        elif cmd == "soldier":
            s_cost = 50 + (soldiers * 10)
            if gold >= s_cost:
                update_game(conn, -s_cost, 0, 0, 1, 10, current_move_increment)
                print("💂 سرباز استخدام شد!")
            else:
                print(f"❌ طلا کم است!")

        elif cmd == "battle":
            if soldiers < 1:
                print("❌ سرباز نداری!")
            else:
                # تعیین قدرت دشمن (اگر باس باشد، خیلی قوی‌تر است)
                if boss_active:
                    enemy_power = (power * 2) + random.randint(20, 50)
                    print(f"👹 در حال مبارزه با باس عظیم‌الجثه... (قدرت باس: {enemy_power})")
                else:
                    enemy_power = random.randint(1, power + 50)
                    print(f"⚔️ در حال نبرد با دشمن معمولی... (قدرت دشمن: {enemy_power})")

                if power >= enemy_power:
                    if boss_active:
                        loot = random.randint(500, 1000) # جایزه بزرگ برای باس
                        print(f"👑 افسانه‌ای! باس را شکست دادی! غنیمت: {loot} طلا")
                    else:
                        loot = random.randint(50, 150)
                        print(f"🎉 پیروز شدی! غنیمت: {loot} طلا")
                    update_game(conn, loot, 0, 0, 0, 0, current_move_increment)
                else:
                    loss = random.randint(20, 50)
                    print(f"💀 شکست خوردی! {loss} طلا از دست دادی.")
                    update_game(conn, -loss, 0, 0, 0, 0, current_move_increment)

        elif cmd == "exit":
            save_highscore(factories)
            break
        else:
            print("⚠️ دستور نامعتبر!")

        # درآمد کارخانه‌ها
        c.execute('UPDATE game SET gold = gold + ? WHERE id=1', (factories * 10,))
        conn.commit()

except Exception as e:
    print(f"\nخطا: {e}")
finally:
    conn.close()
