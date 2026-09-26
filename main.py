from pathlib import Path
from datetime import datetime

def format_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size / (1024 * 1024):.2f} MB"

def scan_folder():
    print("========== 作业文件扫描 ==========")
    folder_input = input("请输入需要扫描的文件夹路径：").strip()
    folder = Path(folder_input)
    if not folder.exists():
        print("错误：这个文件夹不存在。")
        return
    if not folder.is_dir():
        print("错误：输入的不是文件夹。")
        return
    print()
    print("如果需要筛选文件类型，请输入 .pdf 或 .docx")
    print("如果不筛选，直接按 Enter。")
    extension = input("请输入扩展名：").strip().lower()
    if extension and not extension.startswith("."):
        extension = "." + extension
    print()
    print("========== 扫描结果 ==========")
    count = 0
  
    for file in folder.iterdir():
        if not file.is_file():
            continue
        if extension and file.suffix.lower() != extension:
            continue
        stat = file.stat()
        size = format_size(stat.st_size)
        modified_time = datetime.fromtimestamp(
            stat.st_mtime
        ).strftime("%Y-%m-%d %H:%M:%S")
        print()
        print(f"文件名：{file.name}")
        print(f"大小：{size}")
        print(f"修改时间：{modified_time}")
        count += 1
    print()
    print("------------------------------")
    print(f"共找到 {count} 个文件。")

if __name__ == "__main__":
    scan_folder()
