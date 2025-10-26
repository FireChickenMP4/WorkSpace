import os
import shutil
import re

def organize_by_problem_id():
    current_dir = os.getcwd()
    # 正则表达式：匹配文件名开头的题号（字母+数字组合，后跟空格）
    # 例如：P2397、B1234、CF1039D、ABC1234E 等
    problem_id_pattern = r'^([A-Za-z0-9]+)\s'
    
    for filename in os.listdir(current_dir):
        # 跳过目录和隐藏文件
        if os.path.isdir(os.path.join(current_dir, filename)) or filename.startswith('.'):
            continue
            
        # 检查文件名是否以题号开头（题号后必须有空格）
        match = re.match(problem_id_pattern, filename)
        if match:
            problem_id = match.group(1)  # 提取题号（保留原始大小写）
            target_dir = os.path.join(current_dir, problem_id)
            
            # 创建目标文件夹
            os.makedirs(target_dir, exist_ok=True)
            
            # 移动文件
            source_path = os.path.join(current_dir, filename)
            target_path = os.path.join(target_dir, filename)
            
            if source_path != target_path:
                shutil.move(source_path, target_path)
                print(f"Moved: {filename} -> {problem_id}/{filename}")
        else:
            # 不匹配题号格式的文件保留原位置
            print(f"Skipped (non-matching): {filename}")

if __name__ == "__main__":
    organize_by_problem_id()
    print("\nOrganization completed! (Supported formats: PXXXX, BXXXX, CF1039D, etc.)")