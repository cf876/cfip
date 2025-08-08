import requests
from bs4 import BeautifulSoup
import re
import os
import time
import random

# 目标URL列表
urls = [
    'https://ip.164746.xyz', 
    'https://cf.090227.xyz', 
    'https://stock.hostmonit.com/CloudFlareYes',
    'https://www.wetest.vip/page/cloudflare/address_v4.html'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

# 检查ip.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')
if os.path.exists('ip20.txt'):
    os.remove('ip20.txt')

# 使用集合存储IP地址实现自动去重
unique_ips = set()

for url in urls:
    try:
        # 发送HTTP请求获取网页内容
        response = requests.get(url, timeout=5)
        
        # 确保请求成功
        if response.status_code == 200:
            # 获取网页的文本内容
            html_content = response.text
            
            # 使用正则表达式查找IP地址
            ip_matches = re.findall(ip_pattern, html_content, re.IGNORECASE)
            
            # 将找到的IP添加到集合中（自动去重）
            unique_ips.update(ip_matches)
    except requests.exceptions.RequestException as e:
        print(f'请求 {url} 失败: {e}')
        continue

# 将去重后的IP地址按数字顺序排序后写入文件
if unique_ips:
    # 按IP地址的数字顺序排序（非字符串顺序）
    sorted_ips = sorted(unique_ips, key=lambda ip: [int(part) for part in ip.split('.')])
    
    with open('ip.txt', 'w') as file:
        for ip in sorted_ips:
            # 查询IP的地理位置
            try:
                response = requests.get(f'http://ip-api.com/json/{ip}')
                # 在每次查询后等待2秒，避免被屏蔽
                time.sleep(1)
                if response.status_code == 200:
                    data = response.json()
                    country = data.get('countryCode', 'Unknown')
                    file.write(f"{ip}#{country}#{ip}\n")
                else:
                    file.write(f"{ip}#Unknown#{ip}\n")
            except requests.exceptions.RequestException as e:
                print(f'查询IP {ip}的地理位置失败: {e}')
                file.write(f"{ip}#Unknown#{ip}\n")
    print(f'已保存 {len(sorted_ips)} 个唯一IP地址到ip.txt文件。')
    
    # 随机选择20个IP并写入ip20.txt
    if len(unique_ips) >= 20:
        selected_ips = random.sample(list(unique_ips), 20)
        with open('ip20.txt', 'w') as file:
            for ip in selected_ips:
                # 从ip.txt中提取位置信息
                with open('ip.txt', 'r') as ip_file:
                    lines = ip_file.readlines()
                    for line in lines:
                        if line.startswith(ip):
                            parts = line.strip().split('#')
                            country = parts[1] if len(parts) > 1 else 'Unknown'
                            file.write(f"{ip}#{country}#{ip}\n")
                            break
        print(f'已随机选取20个IP并保存到ip20.txt文件。')
    else:
        print(f'唯一IP地址数量少于20个，无法选取20个IP。')
else:
    print('未找到有效的IP地址。')
