import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import readcsv_ali 
# 指定 GeckoDriver 路径（如果已添加到 PATH，可以省略）
geckodriver_path = "browe/geckodriver"  # 例如：C:\\geckodriver.exe (Windows)

# 创建新的下载文件夹
def create_download_folder(base_dir):
    # 使用当前时间戳创建文件夹
    folder_name = "downloaded_csvs_" + time.strftime("%Y%m%d%H%M%S")
    download_dir = os.path.join(base_dir, folder_name)
    
    # 如果文件夹不存在，创建文件夹
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    return download_dir

# 配置 Firefox 的下载设置
def configure_firefox(download_dir):
    firefox_options = webdriver.FirefoxOptions()
    # **无头模式**
    firefox_options.add_argument("--headless")

    # **禁用通知 & 图像加载**
    firefox_options.set_preference("dom.webnotifications.enabled", False)
    firefox_options.set_preference("permissions.default.image", 2)
    absolute_download_dir = os.path.abspath(download_dir)
    # 设置下载路径
    firefox_options.set_preference("browser.download.folderList", 2)  # 2 为自定义目录
    firefox_options.set_preference("browser.download.dir", absolute_download_dir )  # 设置下载目录
    firefox_options.set_preference("browser.download.useDownloadDir", True)
    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/csv")  # 自动保存 CSV 文件

    return firefox_options

# 处理单个域名并下载 CSV 文件
def process_domain(driver, domain, download_dir):
    print(f"正在处理域名: {domain}")

    # 打开目标网站
    driver.get("https://boce.aliyun.com/detect/http")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "url1")))  # 等待页面加载

    # 找到输入框并输入目标 URL
    input_box = driver.find_element(By.ID, "url1")
    input_box.clear()
    input_box.send_keys(domain)
    print(f"已设置输入框的值: {domain}")

    # 找到并点击“立即检测”按钮
    submit_button = driver.find_element(By.XPATH, "//button[span[text()='立即检测']]")
    driver.execute_script("arguments[0].click();", submit_button)

    # 等待检测结果加载
    WebDriverWait(driver, 200).until(
        EC.presence_of_element_located((By.XPATH, "//button[@class='next-btn next-small next-btn-normal export-button']"))
    )

    # 找到并点击“导出报表”按钮
    export_button = driver.find_element(By.XPATH, "//button[@class='next-btn next-small next-btn-normal export-button']")
    export_button.click()

    # 等待文件下载完成（根据网络速度，可能需要调整等待时间）
    time.sleep(5)

    print(f"{domain} 的 CSV 文件已开始下载。")
    return rename_downloaded_file(download_dir, domain)

def rename_downloaded_file(download_dir, domain):
    # 等待文件下载完成（根据网络速度，可能需要调整等待时间）
    time.sleep(20)
    
    # 获取下载目录下所有文件
    files = os.listdir(download_dir)
    csv_files = [f for f in files if f.endswith(".csv")]
    
    if len(csv_files) == 1:
        # 如果有且仅有一个 CSV 文件，取第一个文件
        latest_file = csv_files[0]
        
        # 构建新的文件名
        new_file_name = f"{domain.replace('https://', '').replace('http://', '').replace('/', '_')}_report.csv"
        old_file_path = os.path.join(download_dir, latest_file)
        new_file_path = os.path.join(download_dir, new_file_name)

        # 重命名文件
        os.rename(old_file_path, new_file_path)
        print(f"文件已重命名为：{new_file_path}")
        return new_file_path
    else:
        print("未找到或找到了多个 CSV 文件。")
        return None
    
def read_domains_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# 主函数：遍历域名列表并调用处理函数
def main():
    base_dir = "ali_domain_check"  # 根目录，替换为你自己的路径
    download_dir = create_download_folder(base_dir)  # 创建下载文件夹
    domain_file = "ali_domain_check/domain.txt"
    # 设置 Firefox 配置
    print(download_dir)
    firefox_options = configure_firefox(download_dir)

    # 启动 Firefox WebDriver
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)

    # 你的域名列表
    domain_list = read_domains_from_file(domain_file)

    try:
        for domain in domain_list:
        # 遍历域名列表并进行处理
            for attempt in range(3):
                try:
                    process_domain(driver, domain, download_dir)
                    break  # 成功则跳出重试循环
                except Exception as e:
                    print(f"处理 {domain} 发生错误, 第 {attempt+1} 次重试: {e}")
                    if attempt == 2:
                        print(f"{domain} 处理失败，跳过。")
    finally:
        # 关闭浏览器
        driver.quit()
    readcsv_ali.process_files(download_dir)
if __name__ == "__main__":
    main()
