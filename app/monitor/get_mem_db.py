import sqlite3
import time



def create_db():
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE merory (time INTEGER primary key, memtotal INTEGER, memfree INTEGER, buffers INTEGER, cached INTEGER)')

    cursor.close()
    conn.commit()
    conn.close()


def get_memory():
    with open('/proc/meminfo') as f:
        meminfos = f.readlines()
        for meminfo in meminfos:
            meminfo = meminfo.split()
            if meminfo[0] == 'MemTotal:':
                total = int(meminfo[1])
            elif meminfo[0] == 'MemFree:':
                free = int(meminfo[1])
            elif meminfo[0] == 'Buffers:':
                buffers = int(meminfo[1])
            elif meminfo[0] == 'Cached:':
                cached = int(meminfo[1])
    t = int(time.time())
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    sql = 'insert into memory (time, memtotal, memfree, buffers, cached) value (%s, %s, %s, %s)' %(time, total, free, buffers, cached)
    cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()


# create_db()
while True:
    time.sleep(1)
    get_memory()