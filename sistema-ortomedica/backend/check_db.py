import db
con = db._con()
cur = con.cursor()
cur.execute("SELECT COUNT(*) FROM inventory_raw")
raw = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM inventory_current")
curr = cur.fetchone()[0]
print("inventory_raw:", raw)
print("inventory_current:", curr)
cur.execute("SELECT sku, name, existencia, precio FROM inventory_current ORDER BY sku LIMIT 10")
for r in cur.fetchall():
    print(r)
cur.close(); con.close()
