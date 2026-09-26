from pathlib import Path
from datetime import datetime

# =========================
# 工具函数
# =========================

def format_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size / (1024 * 1024):.2f} MB"

def get_unique_path(target_path):
    """
    如果目标文件已经存在，
    就自动添加 _1、_2、_3……
    避免覆盖原文件。
    """
    if not target_path.exists():
        return target_path

    parent = target_path.parent
    stem = target_path.stem
    suffix = target_path.suffix
    number = 1
    while True:
        new_path = parent / f"{stem}_{number}{suffix}"

        if not new_path.exists():
            return new_path

        number += 1

# =========================
# 需求 1：扫描和列出文件
# =========================

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

# =========================
# 需求 2：批量改名
# =========================

def batch_rename():
    print()
    print("========== 批量改名 ==========")
    folder_input = input("请输入作业文件夹路径：").strip()
    folder = Path(folder_input)
    if not folder.exists():
        print("错误：这个文件夹不存在。")
        return
    if not folder.is_dir():
        print("错误：输入的不是文件夹。")
        return
    rename_list = []
    for file in folder.iterdir():
        if not file.is_file():
            continue
        if file.suffix.lower() not in [".pdf", ".docx"]:
            continue
        filename_without_extension = file.stem
        parts = filename_without_extension.split("_")
        # 文件名必须至少包含：
        # 学号_姓名_作业名
        if len(parts) < 3:
            print(
                f"跳过：{file.name}，"
                "文件名格式不符合要求。"
            )
            continue
        student_id = parts[0]
        assignment_name = "_".join(parts[2:])
        new_filename = (
            f"{assignment_name}_{student_id}{file.suffix}"
        )
        target_path = folder / new_filename
        # 自动处理重名
        target_path = get_unique_path(target_path)
        rename_list.append(
            {
                "old": file,
                "new": target_path
            }
        )
    if not rename_list:
        print("没有找到可以改名的文件。")
        return
    # 先打印预览
    print()
    print("以下文件将被改名：")
    print()
    for item in rename_list:
        print(
            f"{item['old'].name}"
            f"  →  "
            f"{item['new'].name}"
        )
    print()
    # 必须确认后才真正改名
    confirm = input(
        "确认执行以上改名吗？(y/n)："
    ).strip().lower()
    if confirm != "y":
        print("已经取消，没有修改任何文件。")
        return
    success_count = 0
    for item in rename_list:
        try:
            item["old"].rename(item["new"])
            success_count += 1
        except Exception as error:
            print(
                f"修改失败：{item['old'].name}"
            )
            print(error)
    print()
    print(
        f"批量改名完成，共成功处理 {success_count} 个文件。"
    )

# =========================
# 主菜单
# =========================

def main():
    while True:
        print()
        print("==============================")
        print("     作业文件批量归档工具")
        print("==============================")
        print("1. 扫描并列出文件")
        print("2. 批量改名")
        print("0. 退出程序")
        print("==============================")
        choice = input("请输入功能编号：").strip()
        if choice == "1":
            scan_folder()
        elif choice == "2":
            batch_rename()
        elif choice == "0":
            print("程序已退出。")
            break
        else:
            print("输入错误，请输入 0、1 或 2。")

if __name__ == "__main__":
    main()
