import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import random
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, CallbackContext
import time

# Tắt cảnh báo về chứng chỉ HTTPS
warnings.simplefilter('ignore', InsecureRequestWarning)

# Số lượng luồng để lấy proxy
num_threads = 5

# Danh sách các API proxy
proxy_apis = [
    'https://gimmeproxy.com/api/getProxy',
    'https://anotherproxyapi.com/api/getProxy',
    'http://pubproxy.com/api/proxy',
    # Thêm các API khác ở đây
]

def get_proxy():
    api_url = random.choice(proxy_apis)
    try:
        response = requests.get(api_url, verify=False)
        if response.status_code == 200:
            proxy_info = response.json()
            
            # Xử lý dữ liệu từ API pubproxy.com
            if 'data' in proxy_info:
                # Dữ liệu từ pubproxy.com có thể nằm trong trường 'data'
                proxy_info = proxy_info['data'][0]
            
            return proxy_info
    except requests.RequestException as e:
        print(f"Error fetching proxy from {api_url}: {e}")
    return None

def display_proxy_info(proxy_info):
    if proxy_info:
        ip = proxy_info.get('ip', 'N/A')
        port = proxy_info.get('port', 'N/A')
        return f"{ip}:{port}", f"IP: {ip}\nPort: {port}\n"
    return None, None

def fetch_proxies(num_proxies):
    fetched_proxies = []
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(get_proxy) for _ in range(num_proxies)]
        for future in as_completed(futures):
            proxy_info = future.result()
            if proxy_info:
                proxy, _ = display_proxy_info(proxy_info)
                if proxy:
                    fetched_proxies.append(proxy)
            else:
                print("Failed to fetch a proxy.")
    end_time = time.time()
    duration = end_time - start_time
    return fetched_proxies, duration

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Chào bạn! Gửi lệnh /getproxy <số_lượng> để nhận proxy.")

def get_proxy_handler(update: Update, context: CallbackContext):
    try:
        if len(context.args) != 1 or not context.args[0].isdigit():
            update.message.reply_text("Vui lòng nhập số lượng proxy hợp lệ. Ví dụ: /getproxy 5")
            return

        num_proxies = int(context.args[0])
        update.message.reply_text("Đang lấy proxy, vui lòng chờ...")
        proxies_list, duration = fetch_proxies(num_proxies)
        
        if proxies_list:
            # Lưu vào file
            with open('proxy.txt', 'w') as file:
                for proxy in proxies_list:
                    file.write(f"{proxy}\n")
            
            # Gửi file cho người dùng
            with open('proxy.txt', 'rb') as file:
                update.message.reply_document(document=InputFile(file, 'proxy.txt'))
            
            # Thông báo thời gian
            update.message.reply_text(f"Đã lấy {len(proxies_list)} proxy(s) trong {duration:.2f} giây.")
        else:
            update.message.reply_text("Không lấy được proxy nào.")
    except Exception as e:
        update.message.reply_text(f"Đã xảy ra lỗi: {e}")

def main():
    # Thay YOUR_TOKEN bằng token API của bạn
    updater = Updater("YOUR_TOKEN", use_context=True)
    
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getproxy", get_proxy_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
