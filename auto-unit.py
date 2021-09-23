# ex uuid: 9aa9ec96-6fdd-41e3-9220-ab326e58ae81
#         2abcf342-bf67-416c-86b4-056ca9167e8f
#         8 -  4 - 4 - 4 - 12
import argparse
import csv
import random
import string
import json

parser = argparse.ArgumentParser(description="auto generate units for horizon-eda")

parser.add_argument("-p", type=str, required=True, help="specify root path to csv file")
parser.add_argument("-m", type=str, required=True, help="specify manufacturer")
parser.add_argument("-n", type=str, required=True, help="specify name of unit")
parser.add_argument(
    "-d", type=str, required=True, help="specify path to horizon pool db"
)


args = parser.parse_args()

csv_path = args.p


def uuid_gen(format=[8, 4, 4, 4,12], chars=string.ascii_lowercase[0:6] + string.digits):
    tmp = ""
    for n in format:
        tmp += "".join(random.SystemRandom().choice(chars) for _ in range(n)) + "-"
    return tmp[:-1]

def alphabetize_dict(list, key):
    tmp = []
    while(1):
        changes = False
        for index, elem in enumerate(list):
            if index > 0:
                if elem[key] < prev_elem[key]:
                    tmp = list[index-1]
                    list[index-1] = list[index]
                    list[index] = tmp
                    changes = True
            prev_elem = elem
        if not changes:
            return list



unit = {
    "manufacturer": args.m,
    "name": args.n,
    "pins": [],
    "type": "unit",
    "uuid": uuid_gen(),
}


pin_list = {}
tmp = []


banks = {"0":"0","1":"1","2":"2","3":"3","power":["vcc","gnd","vccio","gndpll","vccpll","vpp"],"spi":"spi"}

for bank_name_key in banks:
    pin_list = {}
    tmp = []
    bank_name = banks[bank_name_key]
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pin_function = row["Pin Function"]
            pin_type = row["Pin Type"].lower()
            bank = row["Bank"].lower()
            pin_name = row["121-cabga"]
            direction = ""
            if bank in bank_name:
                if pin_name != "-" and pin_name != "" and pin_name != " ": 
                    if "pio" in pin_type or "config" in pin_type or "spi" in pin_type:
                        direction = "bidirectional"
                    elif "gnd" in pin_type or "gbin" in pin_type:
                        direction = "passive"
                    elif "vcc" in pin_type or "vpp" in pin_type:
                        direction = "power_input"
                    elif "nc" in pin_type:
                        direction = "not_connected"
                    tmp.append({"direction": direction, "names": [pin_function],"primary_name":pin_name,"swap_group": 0})

    for elem in alphabetize_dict(tmp, "primary_name"):
        pin_list[uuid_gen()] = elem
    unit["pins"] = pin_list
    unit["uuid"] = uuid_gen()

    if type(bank_name) == list:
        out_path =  args.n + "-power.json" 
        with open(out_path, 'w') as outfile:
            unit["name"] = args.n+"-power"
            json.dump(unit, outfile, indent=3)

    else:
        out_path =  args.n +  f"-{bank_name}.json" 
        with open(out_path, 'w') as outfile:
            unit["name"] = args.n+f"-{bank_name}"
            json.dump(unit, outfile, indent=3)
