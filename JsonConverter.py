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
                # print(section_info)

                given, staff, par, dot = given_by(section_info)
                if given:
                    town['надає'] = given
                if staff:
                    town['персонал'] = staff
                if par:
                    town['душ'] = par
                if dot:
                    town['дот.'] = dot
                data.append(town)
    return data


def given_by(section):
    res_giv = {}
    res_staff = {}
    parishioners = []
    dot = {}
    substrings = {"Банк", "банк", "Спадкоємці", "Конвент",
                  "Рада", "Наслідники"}
    for idx, i in enumerate(section):
        if re.search(r'Надає', i):
            i = i.split(':')
            output = any([substr in i[-1] for substr in substrings])
            if output:
                res_giv['тип'] = 'організація'
            else:
                res_giv['тип'] = 'особа'
            res_giv['назва'] = i[-1].strip()
        elif re.match(r"^Парох", i):
            if not section[idx + 1][0].isupper():
                i += ' ' + section[idx + 1]
            i = i.split(':')
            pastor_info = i[-1].split(',')
            pastor = {}
            if '.' in pastor_info[0]:
                p_type = pastor_info[0].split()[0]
                name = pastor_info[0].split()[1]
                surname = pastor_info[0].split()[2]
                pastor = {'тип': p_type, "імʼя": name, "прізвище": surname}
                del pastor_info[0]
            else:
                name = pastor_info[0].split()[0]
                surname = pastor_info[0].split()[1]
                pastor = {"імʼя": name, "прізвище": surname}
                del pastor_info[0]
            used_info_idx = set()
            for num, inf in enumerate(pastor_info):
                if re.search(r"^р\.", inf.strip()):
                    pastor['р.'] = re.findall(r"(\d{4})", inf)[0]
                    used_info_idx.add(num)
                elif re.search(r"^о\. (\d{4})", inf.strip()):
                    pastor['о.'] = re.findall(r"(\d{4})", inf)[0]
                    used_info_idx.add(num)
                elif re.search(r"^ж\.", inf.strip().lower()):
                    pastor['стан'] = 'ж.'
                    used_info_idx.add(num)
            other = ''
            for num, inf in enumerate(pastor_info):
                if num not in used_info_idx:
                    other += inf + ', '
            if other:
                pastor['інше'] = other
            res_staff['парох'] = pastor
        elif re.match(r"Сотр", i):
            res_staff["сотрудники"] = get_coworkers(section, idx)
        elif re.match(r'Душ', i):
            parishioners = get_num_of_parishioners(section, idx)
        elif re.match(r"Дот", i):
            dot = get_dot(section, idx)

    return res_giv, res_staff, parishioners, dot


def get_coworkers(section, idx):
    coworkers = [{}]
    coworker_info = section[idx]
    if idx + 1 < len(section):
        if not section[idx + 1][0].isupper():
            coworker_info += ' ' + section[idx + 1]
    coworker_info = coworker_info.split(':')[-1]
    coworker_info = coworker_info.split(',')
    main_cow_inf = coworker_info[0]
    used_info_idx = set()
    if len(main_cow_inf.split()) == 4:
        coworkers[0]['інше'] = main_cow_inf
    elif '.' in main_cow_inf:
        c_type = main_cow_inf.split()[0]
        name = main_cow_inf.split()[1]
        surname = main_cow_inf.split()[2]
        coworkers[0]['тип'] = c_type
        coworkers[0]["імʼя"] = name
        coworkers[0]["прізвище"] = surname
        del coworker_info[0]
    else:
        name = main_cow_inf.split()[1]
        surname = main_cow_inf.split()[2]
        coworkers[0]["імʼя"] = name
        coworkers[0]["прізвище"] = surname
        del coworker_info[0]
    for num, inf in enumerate(coworker_info):
        if re.search(r"^р\.", inf.strip()):
            coworkers[0]['р.'] = re.findall(r"(\d{4})", inf)[0]
            used_info_idx.add(num)
        elif re.search(r"^о\. (\d{4})", inf.strip()):
            coworkers[0]['о.'] = re.findall(r"(\d{4})", inf)[0]
            used_info_idx.add(num)
        elif re.search(r"^ж\.", inf.strip().lower()):
            coworkers[0]['стан'] = 'ж.'
            used_info_idx.add(num)
    other = ''
    for indx, inform in enumerate(coworker_info):
        if indx not in used_info_idx:
            other += inform + ', '
    if other:
        coworkers[0]['інше'] = other
    return coworkers


def get_num_of_parishioners(section, idx):
    parishioners = []
    united_info = section[idx]
    united_info = re.sub(r"Душ:", '', united_info)
    idx += 1
    while idx < len(section) and (section[idx][0].islower() or section[idx][0] in {'Б', 'П'}):
        united_info += ' ' + section[idx]
        idx += 1
    additional = united_info.split(';')
    for i in additional:
        if re.search(r"[вз]\s+(пр\.|прис\.|прил\.|доч\.)\s+(\w*)", i):
            element = {}
            adjacent = ''
            adj = re.findall(r"^[вз]\s+(пр\.|прис\.|прил\.|доч\.)\s+(\w*)", i.strip())
            if adj:
                adjacent = adj[-1][-1]
            if adjacent:
                element['прил.'] = adjacent
            for name, quant in re.findall(r"(\D{2,3}\.)\s*(\d{1,4})", i):
                element[name] = quant
            if element:
                parishioners.append(element)
        else:
            element = {}
            united_info_lst = re.split(',', i)
            for inf in united_info_lst:
                if re.search(r"(\D{2,3}\.).*(\d{1,4})", inf):
                    element[re.search(r"(\D{2,3}\.).", inf).group(0).strip()] = \
                        re.search(r"(\d{1,4})", inf).group(0)
            if element:
                parishioners.append(element)
    return parishioners


def get_dot(section, idx):
    dot = {}
    united_info = section[idx]
    united_info = re.sub(r".*:", "", united_info)
    idx += 1
    while idx < len(section) and \
            (not section[idx][0].isupper() and \
             not re.match(r"\d{1,2}\)", section[idx])):
        united_info += ' ' + section[idx]
        idx += 1
    united_info_lst = re.split(r",|;", united_info)
    for i in united_info_lst:
        if re.match(r"\w*\. \d+ \wа \d+ а \d+ т", i.strip()):
            i = i.split()
            element = {'ha': i[1], 'a': i[3], 'm2': i[5]}
            dot[i[0]] = element
        elif re.match(r"\w*\. \d+ а \d+ т", i.strip()):
            i = i.split()
            element = {'a': i[1], 'm2': i[3]}
            dot[i[0]] = element
        elif re.match(r"\d+ \wа \d+ а \d+ т", i.strip()):
            i = i.split()
            element = {'ha': i[0], 'a': i[2], 'm2': i[4]}
            dot['п.'] = element
        elif re.search(r"разом \d+ \wа \d+ а \d+ т", i.strip()):
            i = re.sub(r".*м", '', i.strip())
            i = i.split()
            element = {'ha': i[0], 'a': i[2], 'm2': i[4]}
            dot['п.'] = element
        elif re.match(r"дім і буд\.", i.strip()):
            i = re.sub(r"дім і буд\.", '', i)
            dot['дім'] = i.strip()
            dot['буд.'] = i.strip()
        elif re.match(r"дім", i.strip()) and len(i.strip().split()) == 2:
            dot["дім"] = i.strip().split()[-1]
        elif re.match(r"буд.", i.strip()) and len(i.strip().split()) == 2:
            dot["буд."] = i.strip().split()[-1]
        elif re.search(r"Дн", i):
            dot["Дн."] = "Дн."
    return dot


def get_section_info(lines, idx):
    section_info = [lines[idx].strip()]
    idx += 1
    while not re.match(r"\d{1,2}\)", lines[idx]) and idx < len(lines) - 1:
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
