import os
import pandas as pd

def process_files(download_dir):
    result_pd = pd.DataFrame(columns=["域名", "探测点", "解析结果IP"])
    result_dict = {}
    # 遍历 download_dir 中的所有文件
    for filename in os.listdir(download_dir):
        if filename.endswith(".csv") or filename.endswith(".xlsx"):  # 增加 .xlsx 文件检查
            file_path = os.path.join(download_dir, filename)
            try:
                # 根据文件类型读取文件
                if filename.endswith(".csv"):
                    df = pd.read_csv(file_path)
                elif filename.endswith(".xlsx"):
                    df = pd.read_excel(file_path , engine="openpyxl")  # 读取 Excel 文件

                # 确保文件包含“状态”、“探测点”和“解析结果IP”列
                if "状态" in df.columns and "探测点" in df.columns and "解析结果IP" in df.columns :
                    domain = filename.replace(".csv", "").replace("-http-result.xlsx", "")

                    # 预处理探测点：只取前2个字符
                    df["探测点"] = df["探测点"].astype(str).str[:2]

                    # 处理 "劫持"（检查解析结果IP）
                    hijacked_points = set()
                    for _, row in df.iterrows():
                        ip_address = str(row["解析结果IP"])  # 确保是字符串
                        detect_point = row["探测点"]
                        if not (ip_address.startswith("103.") or ip_address.startswith("43.")):  
                            hijacked_points.add(detect_point)
                            
                            
                    # 处理 "屏蔽"（状态码以 "6" 开头）
                    filtered_df = df[df["状态"].astype(str).str.startswith('6')]
                    blocked_points = set(filtered_df["探测点"])

                    # 初始化字典项
                    if domain not in result_dict:
                        result_dict[domain] = {
                            "劫持": set(),
                            "屏蔽": set()
                        }
                    # 记录数据
                    result_dict[domain]["劫持"].update(hijacked_points)
                    result_dict[domain]["屏蔽"].update(blocked_points)
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
    # 生成最终结果
    result_list = []
    for domain, data in result_dict.items():
        # 组织探测点数据
        hijacked_str = ', '.join([f'"{point}"' for point in sorted(data["劫持"])]) if data["劫持"] else '""'
        blocked_str = ', '.join([f'"{point}"' for point in sorted(data["屏蔽"])]) if data["屏蔽"] else '""'

        result_list.append([domain, hijacked_str, blocked_str])

    # 将结果保存为 CSV 文件
    result_pd = pd.DataFrame(result_list, columns=["域名", "劫持探测点", "屏蔽探测点"])
    
    # 将结果保存到新的 CSV 文件中
    output_file = os.path.join(download_dir, "filtered_result.csv")
    result_pd.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"处理完成，结果已保存到: {output_file}")

# 示例使用
download_dir = "footbook/ali_domain_check/downloaded_csvs_20250324160302"
process_files(download_dir)
