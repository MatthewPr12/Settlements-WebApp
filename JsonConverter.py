import re
import json
from GetLocation import get_location


def file_reader(path):
    data = []
    with open(path, 'r', encoding='utf-8') as text_file:
        common_info = {}
        lines = text_file.readlines()
        for idx, line in enumerate(lines):
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
                line_lst = line.split(',')
                if len(line_lst[0].split()) != 3:
                    settlement = line_lst[0].split()[1]
                else:
                    settlement = f"{line_lst[0].split()[1]} {line_lst[0].split()[2]}"
                location = get_location(settlement)
                town = common_info.copy()
                town['населений пункт'] = {'назва': settlement, "location": {"lat": location[0], "lng": location[-1]}}

                town['церкви'] = []
                inside_idx = idx
                main_info = ''
                church = {}
                while lines[inside_idx] != '\n':
                    main_info += lines[inside_idx]
                    inside_idx += 1
                main_info = re.split(',|\n', main_info)
                # print(main_info)
                if len(main_info) > 2:
                    if 'ц.' in main_info[1]:
                        main_info[1] = re.sub(r'ц\.', '', main_info[1])
                        church['назва'] = main_info[1].strip()
                    elif 'ц ' in main_info[1]:
                        main_info[1] = re.sub(r'ц ', '', main_info[1])
                        church['назва'] = main_info[1].strip()
                    elif 'ц.' in main_info[2]:
                        main_info[2] = re.sub(r'ц\.', '', main_info[2])
                        church['назва'] = main_info[2].strip()
                    else:
                        church['назва'] = 'немає'
                else:
                    church['назва'] = 'немає'

                united_main_info = ','.join(main_info)
                year = []
                renewed = []
                if re.search(r'дер\.', united_main_info):
                    church['тип'] = 'дер.'
                    year = re.findall(r'дер\. (\d{4})', united_main_info)
                elif re.search(r'мур\.', united_main_info):
                    church['тип'] = 'мур.'
                    year = re.findall(r'мур\. (\d{4})', united_main_info)
                if year:
                    church['рік'] = year[0]
                if re.search(r'відн(.{0,5})\.', united_main_info):
                    renewed = re.findall(r'відн(.{0,5})\. (\d{4})', united_main_info)
                if renewed:
                    church['відн.'] = renewed[0][-1]
                if re.search(r'Дн\.', united_main_info):
                    church["Дн."] = "Дн."
                town['церкви'].append(church)
                section_info = get_section_info(lines, idx)
                print(section_info)
                data.append(town)
    return data


def get_section_info(lines, idx):
    section_info = [lines[idx].strip()]
    idx += 1
    while not re.match(r"\d{1,2}\)", lines[idx]) and idx < len(lines)-1:
        if lines[idx].strip():
            section_info.append(lines[idx].strip())
        idx += 1
    if idx == len(lines) - 1:
        section_info.append(lines[idx].strip())
    return section_info


def main():
    data = file_reader('/Users/matthewprytula/pythonProject/term2/Settlements-WebApp/image_texts/Terebovelskyi.txt')
    with open('result.json', 'w') as res_file:
        json.dump(data, res_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
