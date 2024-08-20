import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Tắt cảnh báo về chứng chỉ HTTPS
warnings.simplefilter('ignore', InsecureRequestWarning)

# Cấu hình proxy sử dụng ScraperAPI
proxies = {
    "https": "scraperapi.country_code=us.device_type=desktop.session_number=100:de8388ca6209d8d9677a450b343ec68b@proxy-server.scraperapi.com:8001"
}

# Số lượng luồng để lấy proxy
num_threads = 5

def get_proxy():
    try:
        response = requests.get('https://gimmeproxy.com/api/getProxy', proxies=proxies, verify=False)
        if response.status_code == 200:
            proxy_info = response.json()
            return proxy_info
    except requests.RequestException as e:
        print(f"Error fetching proxy: {e}")
    return None

def display_proxy_info(proxy_info):
    if proxy_info:
        ip = proxy_info.get('ip', 'N/A')
        port = proxy_info.get('port', 'N/A')
        country = proxy_info.get('country', 'N/A')
        protocol = proxy_info.get('protocol', 'N/A')
        anonymity_level = proxy_info.get('anonymityLevel', 'N/A')

        # Hiển thị thông tin proxy trên các dòng riêng biệt
        print(f"IP: {ip}")
        print(f"Port: {port}")
        print(f"Country: {country}")
        print(f"Protocol: {protocol}")
        print(f"Anonymity Level: {anonymity_level}")
        print("-" * 40)
        
        return f"{ip}:{port}"
    return None

def save_proxies(proxies, filename):
    with open(filename, 'w') as file:
        for proxy in proxies:
            file.write(f"{proxy}\n")

def fetch_proxies(num_proxies):
    fetched_proxies = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(get_proxy) for _ in range(num_proxies)]
        for future in as_completed(futures):
            proxy_info = future.result()
            if proxy_info:
                proxy = display_proxy_info(proxy_info)
                if proxy:
                    fetched_proxies.append(proxy)
            else:
                print("Failed to fetch a proxy.")
    return fetched_proxies

if __name__ == "__main__":
    try:
        # Yêu cầu người dùng nhập số lượng proxy và tên file để lưu
        num_proxies = int(input("Nhập số lượng proxy muốn lấy: "))
        output_file = input("Nhập tên file để lưu proxy (ví dụ: proxy.txt): ")

        if num_proxies <= 0:
            print("Số lượng proxy phải là số dương.")
        else:
            proxies_list = fetch_proxies(num_proxies)

            if proxies_list:
                save_proxies(proxies_list, output_file)
                print(f"Saved {len(proxies_list)} proxies to {output_file}")
            else:
                print("No proxies fetched.")
    except ValueError:
        print("Vui lòng nhập số hợp lệ cho số lượng proxy.")
