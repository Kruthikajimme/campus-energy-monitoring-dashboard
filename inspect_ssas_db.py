import sqlite3
import glob

dbs = glob.glob(r'C:\Users\Kruthika\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\*\Data\*.db\metadata.sqlitedb')
print('Found metadata DBs:', dbs)
if dbs:
    conn = sqlite3.connect(dbs[0])
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    print('SQLite tables:', tables)
    for t in tables:
        try:
            cur.execute(f"SELECT count(*) FROM [{t}]")
            cnt = cur.fetchone()[0]
            if cnt > 0:
                print(f"  {t}: {cnt} rows")
        except Exception as e:
            pass
    conn.close()

