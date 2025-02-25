import os
import pandas as pd
import numpy as np

current_path = os.path.join(os.getcwd(), 'temp\\')
# file = r'C:\Users\Jake\Desktop\MPhys Project\data\3FA_1\3FA_1_15.txt'

def list_split(lst):
    stripped_list = [x.split() for x in lst]
    stripped_list = [[float(j) for j in i] for i in stripped_list]
    return stripped_list
    
def get_data(data_lst):
    frq = []
    real_ep = []
    comp_ep = []
    for data in data_lst:
        frq.append(data[0])
        real_ep.append(data[1])
        comp_ep.append(data[2])
    frq = [float(i) for i in frq]
    real_ep = [float(i) for i in real_ep]
    comp_ep = [float(i) for i in comp_ep]
    return frq, real_ep, comp_ep

def get_run_info(file):
    lines = file.readlines()
    info = lines.pop(0)
    temp_value = lines.pop(0)
    headings = lines.pop(0)
    
    temp_value = temp_value.split('= ')[1]
    holding = []
    run_info = []
    for i in info.split(','):   
        holding.append(i)
    for i in holding:
        add = i.split('Temp')[0]
        run_info.append(add.strip())
    
    temp_value = [temp_value.strip('\n')]
    
    
    # name, other = info.split(', ')
    # run_info.append(name)
    # run_info.append(other.split('Temp')[0])
    # run_info = [i.strip() for i in run_info]
    
    headings_list = headings.split()
    headings_list[0] = headings_list[0] + headings_list[1]
    del headings_list[1]
    
    data = list_split(lines)
    return run_info, temp_value, headings_list, data

# run_info, temp_value, headings_list, data = get_run_info(file)
# print(run_info)
# print(temp_value)


def make_csv(title, headings, data, path, run_info, temp_value):
    df = pd.DataFrame(data, columns=headings)
    length = len(data)
    if not length == len(run_info):
        run_info.extend(['']*(length-len(run_info)))
    if not length == len(temp_value):
        temp_value.extend(['']*(length-len(temp_value)))
    df['run_info'] = run_info
    df['temp'] = temp_value
    # df['log(Freq)'] = np.log10(df['Freq.[Hz]'])
    # df['log(Eps\')'] = np.log10(df['Eps\''])
    # df['log(Eps\'\')'] = np.log10(df['Eps\'\''])
    df.to_csv(path + title + '.csv', index=False)
    
def txt_to_csv(filename, path=current_path):
    with open(filename, 'r') as file:
        run_info, temp_value, headings_list, data = get_run_info(file)
        head, tail = os.path.split(filename)
        tail = tail[0:-4]
        make_csv(tail, headings_list, data, path, run_info, temp_value)



def log_csv(csv_file):
    df = pd.read_csv(csv_file)
    # df['log(Freq)'] = np.log10(df['Freq.[Hz]'])
    # df['log(Eps\'\')'] = np.log10(df['Eps\''])
    # df['log(Eps\')'] = np.log10(df['Eps\'\''])
    new_csv = df.to_csv(csv_file, index=False)
    return new_csv