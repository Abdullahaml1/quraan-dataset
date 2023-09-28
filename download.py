import time
import json
import requests
from tqdm import tqdm
import argparse


def read_data_json(file_name):
    try:
        with open(file_name, 'r') as f:
            data= json.load(f)
    except:
        data = []
    return data
def save_data_json(file_name, new_data):
    try:
        with open(file_name, 'r') as f:
            data= json.load(f)
    except:
        data = []
    data = data + [new_data]
    with open(file_name, 'w+') as f:
        json.dump(data, f, indent=2)

def download_zekr(base_url, file_name, footer='&lang=en&after_date=2000-01-01', bypass_url=0):
    data = read_data_json(file_name)
    current_page=1
    if data == []:
        next_url = base_url
    else:
        next_url = data[-1]['next_page_url'] + footer
        current_page = data[-1]['current_page'] 


    if bypass_url > 0:
        next_url = next_url.split(footer)[0].split('=')[0] + \
            '=' +  str(current_page+1+bypass_url) + footer

    current_page=current_page+1+bypass_url
    print(next_url)

    # get total pages
    try:
        req = requests.get(next_url, timeout=20)
        last_page = json.loads(req.text)['last_page']
        current_page = json.loads(req.text)['current_page']
    except:
        print('Fault Page: ', current_page)
        return


    with tqdm(total=last_page-current_page+1) as pbar:
        while next_url != None:
            # print('Next Url: ',next_url)
            try:
                req = requests.get(next_url, timeout=20)
                req_dict = json.loads(req.text)
                next_url = req_dict['next_page_url'] + footer  
                current_page = req_dict['current_page']
                # print('current_page= ',current_page)
                save_data_json(file_name,req_dict)
            except:
                print('Fault Page: ', current_page+1)
                break
                # next_url = next_url.split(footer)[0].split('=')[0] + \
                        # '=' +  str(current_page+2) + footer



            pbar.update(1)
        
            
            time.sleep(5)

def get_duration_in_minutes(file_name) -> int:
    with open(file_name) as f:
        pages = json.load(f)

    duration = 0.0
    for page in pages:
        for sample in page['data']:
            duration += sample['duration'] / 60.0


    return duration

def get_size_in_mb(file_name) -> int:
    with open(file_name) as f:
        pages = json.load(f)

    size = 0.0
    for page in pages:
        for sample in page['data']:
            size += sample['size'] / 1000000.0


    return size


            


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bypass-next-url", type=int, default=1)
    parser.add_argument("--json-file", type=str, default='zekr_metadaat_v2.json')
    parser.add_argument("--get-duration-in-hours", action='store_true')
    parser.add_argument("--get-size-in-gb", action='store_true')

    args = parser.parse_args()

    if args.get_duration_in_hours:
        duration = get_duration_in_minutes(args.json_file)/60.0
        print(f'Total Duration={duration:f} hours')

    elif args.get_size_in_gb:
        size = get_size_in_mb(args.json_file)/1000
        print(f'Total Size={size:f} GB')
    else:

        download_zekr('https://v2.zekr.online/api/v1/quran/latest?page=1&lang=en&after_date=2000-01-01', 'zekr_metadata_v2.json',
                bypass_url=args.bypass_next_url)
        # download_zekr('https://v2.zekr.online/api/v1/quran/latest?page=1&lang=en&after_date=2000-01-01', 'debug.json')
