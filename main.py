from pathlib import Path
from datetime import datetime
import shutil
import json

# =========================
# 基本设置
# =========================

SUPPORTED_EXTENSIONS = [".pdf", ".docx"]
UNDO_FILE = ".last_operation.json"

# =========================
# 工具函数
# =========================

def is_supported_file(file_path):
    return (
        file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

def format_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size / (1024 * 1024):.2f} MB"

def get_unique_path(target_path):
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

def save_undo_record(operation_name, records):
    data = {
        "operation": operation_name,
        "records": records
    }
    with open(UNDO_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def create_report(folder, operation, processed, skipped):
    report_path = folder / "整理报告.txt"
    with open(report_path, "w", encoding="utf-8") as report:
        report.write("========== 作业文件整理报告 ==========\n\n")
        report.write(
            "生成时间："
            + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            + "\n"
        )
        report.write(f"操作类型：{operation}\n\n")
        report.write(f"成功处理：{processed} 个\n")
        report.write(f"跳过：{len(skipped)} 个\n\n")
        if skipped:
            report.write("---------- 跳过详情 ----------\n")
            for index, item in enumerate(skipped, start=1):
                report.write(f"{index}. {item['file']}\n")
                report.write(f"   原因：{item['reason']}\n")
        report.write("\n=====================================\n")
    print()
    print("整理报告已生成：")
    print(report_path)

# =========================
# 需求 1：扫描与列出
# =========================

def scan_folder():
    print()
    print("========== 扫描文件 ==========")
    folder_input = input("请输入需要扫描的文件夹路径：").strip()
    folder = Path(folder_input)
    if not folder.exists():
        print("错误：这个文件夹不存在。")
        return
    if not folder.is_dir():
        print("错误：输入的不是文件夹。")
        return
    print()
    print("支持筛选：.pdf / .docx")
    print("如果不需要筛选，直接按 Enter。")
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
    if not folder.exists() or not folder.is_dir():
        print("错误：文件夹不存在。")
        return
    rename_list = []
    skipped = []
    for file in folder.iterdir():
        if not is_supported_file(file):
            continue
        filename_without_extension = file.stem
        parts = filename_without_extension.split("_")
        if len(parts) < 3:
            skipped.append({
                "file": file.name,
                "reason": "文件名不符合“学号_姓名_作业名”的格式"
            })
            continue
        student_id = parts[0]
        assignment_name = "_".join(parts[2:])
        new_filename = (
            f"{assignment_name}_{student_id}{file.suffix}"
        )
        target = folder / new_filename
        target = get_unique_path(target)
        rename_list.append({
            "old": file,
            "new": target
        })
    if not rename_list:
        print("没有找到可以改名的文件。")
        if skipped:
            print()
            print("跳过的文件：")
            for item in skipped:
                print(
                    f"{item['file']}：{item['reason']}"
                )
        return
    print()
    print("下面是准备执行的改名：")
    print()
    for item in rename_list:
        print(
            f"{item['old'].name}"
            f"  →  "
            f"{item['new'].name}"
        )
    print()
    confirm = input(
        "确认执行以上改名吗？(y/n)："
    ).strip().lower()
    if confirm != "y":
        print("已经取消，没有修改任何文件。")
        return
    undo_records = []
    success_count = 0
    for item in rename_list:
        old_path = item["old"]
        new_path = item["new"]
        try:
            old_path.rename(new_path)
            undo_records.append({
                "old": str(old_path),
                "new": str(new_path)
            })
            success_count += 1
        except Exception as error:
            skipped.append({
                "file": old_path.name,
                "reason": str(error)
            })
    if undo_records:
        save_undo_record(
            "批量改名",
            undo_records
        )
    print()
    print(f"成功改名 {success_count} 个文件。")
    create_report(
        folder,
        "批量改名",
        success_count,
        skipped
    )

# =========================
# 需求 3：文件归档
# =========================

def archive_files():
    print()
    print("========== 文件归档 ==========")
    folder_input = input(
        "请输入需要整理的文件夹路径："
    ).strip()
    folder = Path(folder_input)
    if not folder.exists() or not folder.is_dir():
        print("错误：文件夹不存在。")
        return
    print()
    print("你可以输入学期或类别名称。")
    print("例如：")
    print("2026秋季")
    print("数据分析")
    print("统计学")
    category = input(
        "请输入归档子文件夹名称："
    ).strip()
    if not category:
        print("文件夹名称不能为空。")
        return
    target_folder = folder / category
    target_folder.mkdir(
        parents=True,
        exist_ok=True
    )
    file_list = []
    skipped = []
    for file in folder.iterdir():
        if not file.is_file():
            continue
        if file.name in [
            "整理报告.txt",
            UNDO_FILE
        ]:
            continue
        if not is_supported_file(file):
            skipped.append({
                "file": file.name,
                "reason": "不是支持的 .pdf 或 .docx 文件"
            })
            continue
        target = target_folder / file.name
        target = get_unique_path(target)
        file_list.append({
            "old": file,
            "new": target
        })
    if not file_list:
        print("没有找到可以归档的文件。")
        return
    print()
    print("准备执行以下归档：")
    print()
    for item in file_list:
        print(
            f"{item['old'].name}"
            f"  →  "
            f"{category}/{item['new'].name}"
        )
    print()
    confirm = input(
        "确认归档吗？(y/n)："
    ).strip().lower()
    if confirm != "y":
        print("已经取消归档。")
        return
    success_count = 0
    undo_records = []
    for item in file_list:
        old_path = item["old"]
        new_path = item["new"]
        try:
            shutil.move(
                str(old_path),
                str(new_path)
            )
            undo_records.append({
                "old": str(old_path),
                "new": str(new_path)
            })
            success_count += 1
        except Exception as error:

            skipped.append({
                "file": old_path.name,
                "reason": str(error)
            })
    if undo_records:
        save_undo_record(
            "文件归档",
            undo_records
        )
    print()
    print(
        f"归档完成，共处理 {success_count} 个文件。"
    )
    create_report(
        folder,
        "文件归档",
        success_count,
        skipped
    )

# =========================
# 需求 3：撤销上一次操作
# =========================
def undo_last_operation():
    print()
    print("========== 撤销上次操作 ==========")
    undo_path = Path(UNDO_FILE)
    if not undo_path.exists():
        print("目前没有可以撤销的操作。")
        return
    try:
        with open(
            undo_path,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)
    except Exception as error:
        print("读取撤销记录失败：", error)
        return
    print(
        f"上一次操作：{data['operation']}"
    )
    confirm = input(
        "确定要撤销吗？(y/n)："
    ).strip().lower()
    if confirm != "y":
        print("取消撤销。")
        return
    success_count = 0
    for record in reversed(data["records"]):
        old_path = Path(record["old"])
        new_path = Path(record["new"])
        if not new_path.exists():
            print(
                f"跳过：{new_path.name} 已不存在"
            )
            continue
        if old_path.exists():
            print(
                f"跳过：原位置已经存在文件 "
                f"{old_path.name}"
            )
            continue
        try:

            old_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )
            shutil.move(
                str(new_path),
                str(old_path)
            )
            print(
                f"已恢复："
                f"{new_path.name}"
                f" → "
                f"{old_path.name}"
            )
            success_count += 1
        except Exception as error:
            print(
                f"恢复失败：{new_path.name}"
            )
            print(error)
    print()
    print(
        f"撤销完成，共恢复 {success_count} 个文件。"
    )
    undo_path.unlink()

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
        print("3. 文件归档")
        print("4. 撤销上一次操作")
        print("0. 退出程序")
        print("==============================")
        choice = input(
            "请输入功能编号："
        ).strip()
        if choice == "1":
            scan_folder()
        elif choice == "2":
            batch_rename()
        elif choice == "3":
            archive_files()
        elif choice == "4":
            undo_last_operation()
        elif choice == "0":
            print("程序已退出。")
            break
        else:
            print(
                "输入错误，请输入 0～4。"
            )

if __name__ == "__main__":
    main()
