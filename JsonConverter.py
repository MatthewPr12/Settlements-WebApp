import re
import json
from GetLocation import get_location


def file_reader(path):
    data = []
    with open(path, 'r', encoding='utf-8') as text_file:
        common_info = {}
        for line in text_file.readlines():
            # skip empty lines
            if not line:
                continue
            # name of protopresbyterate is in parentheses
            elif re.match(r'\(.*?\)', line) and line[1].isupper():
                line = re.sub("[(.)]", "", line)
                line = line.split()
                common_info[line[-1]] = line[0]
            elif re.match(r'^\d+.\.', line):
                line = re.sub(r'^.*?\s+', '', line)
                line = line.split()
                common_info[line[-1].strip('.')] = line[0]
            elif re.match(r'^\d+\)', line):
                line = line.split(',')
                if len(line[0].split()) != 3:
                    settlement = line[0].split()[1]
                else:
                    settlement = f"{line[0].split()[1]} {line[0].split()[2]}"
                print(settlement)
                location = get_location(settlement)
                print(location)
                print(common_info)
                town = common_info.copy()
                town['населений пункт'] = {'назва': settlement, "location": {"lat": location[0], "lng": location[-1]}}
                while not re.match(r'^\d+\)', line[0]):
                    pass
                data.append(town)
    return data


def main():
    data = file_reader('/Users/matthewprytula/pythonProject/term2/Settlements-WebApp/image_texts/Bridskyi.txt')
    with open('result.json', 'w') as res_file:
        json.dump(data, res_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
