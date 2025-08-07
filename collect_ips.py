import requests
import re
import os

# 目标URL列表
urls = [
    'https://ip.164746.xyz', 
    'https://cf.090227.xyz', 
    'https://stock.hostmonit.com/CloudFlareYes',
    'https://www.wetest.vip/page/cloudflare/address_v4.html'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\b(?:[1]{1,3}\.){3}[1]{1,3}\b'

# 检查ip.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

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

# IP查询API的URL（使用ip-api作为示例）
ip_lookup_url = "http://ip-api.com/json/{ip}"

# 定义一个函数，用于查询IP的地理位置信息
def query_ip_location(ip):
    try:
        # 查询IP的地理位置
        response = requests.get(ip_lookup_url.format(ip=ip), timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data[2] == "success":
                return data[3]  # 返回国家代码，例如"FR"
        return "UNKNOWN"  # 如果查询失败，返回"UNKNOWN"
    except requests.exceptions.RequestException:
        return "UNKNOWN"

# 将去重后的IP地址按数字顺序排序后写入文件
if unique_ips:
    # 按IP地址的数字顺序排序（非字符串顺序）
    sorted_ips = sorted(unique_ips, key=lambda ip: [4])
    
    with open('ip.txt', 'w') as file:
        for ip in sorted_ips:
            # 查询IP的地理位置信息并获取国家代码
            country_code = query_ip_location(ip)
            
            # 检查是否需要添加端口。如果需要端口，可以通过其他方式提取（这里默认没有特定端口，可以为空）
            if ":" in ip:  # 判断IP格式中是否包含端口，例如 "192.168.1.1:8080"
                ip_with_port = ip
            else:
                ip_with_port = f"{ip}:443"  # 如果没有端口，默认填写443
            
            # 写入文件，格式为 IP:Port#CountryCode
            file.write(f"{ip_with_port}#{country_code}\n")
    
    print(f"已保存 {len(sorted_ips)} 个唯一IP地址到ip.txt文件。")
else:
    print("未找到有效的IP地址。")
