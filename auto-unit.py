# ex uuid: 9aa9ec96-6fdd-41e3-9220-ab326e58ae81
#         2abcf342-bf67-416c-86b4-056ca9167e8f
#         8 -  4 - 4 - 4 - 12
import argparse
import csv
import random
import string
import json
import sqlite3

parser = argparse.ArgumentParser(description="auto generate units for horizon-eda")

parser.add_argument("-p", type=str, required=True, help="specify root path to csv file")
parser.add_argument("-m", type=str, required=True, help="specify manufacturer")
parser.add_argument("-n", type=str, required=True, help="specify name of unit")
parser.add_argument(
    "-hdb", type=str, required=True, help="specify path to horizon pool db"
)

args = parser.parse_args()

csv_path = args.p


def uuid_gen(format=[8, 4, 4, 12], chars=string.ascii_lowercase + string.digits):
    tmp = ""
    for n in format:
        tmp += "".join(random.SystemRandom().choice(chars) for _ in range(n)) + "-"
    return tmp[:-1]

def conn_gen(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
    except Error as e:
        print(e)
    return conn

def add_to_table(conn,task):
    sql = ''' INSERT INTO units(uuid,name,manufacturer,filename, pool_uuid,last_pool_uuid) VALUES(?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

unit = {
    "manufacturer": args.m,
    "name": args.n,
    "pins": [],
    "type": "unit",
    "uuid": uuid_gen(),
}


pin_list = {}
with open(csv_path, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        pin_function = row["Pin Function"]
        pin_type = row["Pin Type"].lower()
        bank = row["Bank"]
        pin_name = row["121-cabga"]
        direction = ""
        if pin_name != "-" and pin_name != "" and pin_name != " ": 
            if "pio" in pin_type or "config" in pin_type or "spi" in pin_type:
                direction = "bidirectional"
            elif "gnd" in pin_type or "gbin" in pin_type:
                direction = "passive"
            elif "vcc" in pin_type or "vpp" in pin_type:
                direction = "power_input"
            elif "nc" in pin_type:
                direction = "not_connected"
            tmp = {"direction": direction, "names": [pin_function],"primary_name":pin_name,"swap_group": 0}
            pin_list[uuid_gen()] = tmp
unit["pins"] = pin_list

out_path =  args.n + ".json" 
with open(out_path, 'w') as outfile:
    json.dump(unit, outfile, indent=3)

task = (unit['uuid'], args.n, args.m, "","","")
add_to_table(conn_gen(args.hdb),task)