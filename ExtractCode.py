import os

def generate_project_summary(project_path, output_file="project_summary.md", ignore_files=None, ignore_paths=None):
    """
    遍历项目目录，生成项目目录结构及文件内容的 Markdown 文件，并忽略指定的文件内容和路径内容。
    :param project_path: 项目的根目录路径
    :param output_file: 输出的 Markdown 文件路径
    :param ignore_files: 要忽略的文件名列表
    :param ignore_paths: 要忽略的路径列表（相对路径）
    """
    if ignore_files is None:
        ignore_files = []
    if ignore_paths is None:
        ignore_paths = []

    with open(output_file, "w", encoding="utf-8") as summary_file:
        summary_file.write("# 项目文档汇总\n\n")
        summary_file.write(f"项目路径：`{project_path}`\n\n")
        summary_file.write("## 目录结构\n\n")

        # 记录目录结构（包括忽略的文件和路径）
        for root, dirs, files in os.walk(project_path):
            relative_root = os.path.relpath(root, project_path)
            level = root.replace(project_path, "").count(os.sep)
            indent = "  " * level
            summary_file.write(f"{indent}- {os.path.basename(root)}/\n")
            subindent = "  " * (level + 1)
            for file in files:
                summary_file.write(f"{subindent}- {file}\n")

        summary_file.write("\n## 文件内容\n\n")

        # 记录文件内容（排除忽略的文件和路径内容）
        for root, _, files in os.walk(project_path):
            relative_root = os.path.relpath(root, project_path)

            # 跳过忽略的路径
            if relative_root in ignore_paths:
                continue

            for file in files:
                # 跳过忽略的文件
                if file in ignore_files:
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    content = f"无法读取文件：{e}"

                relative_path = os.path.relpath(file_path, project_path)
                summary_file.write(f"### `{relative_path}`\n\n")
                summary_file.write("```text\n")
                summary_file.write(content)
                summary_file.write("\n```\n\n")

if __name__ == "__main__":
    # 指定项目路径
    project_path = "./funclip"

    # 指定忽略的文件名
    ignore_files = [
        ".gitignore",
        "LICENSE",
        "README.md",
        "README_zh.md"
    ]

    # 指定忽略的路径（相对路径）
    ignore_paths = [
        "test",
        "__pycache__"
    ]

    output_file = "project_summary.md"
    generate_project_summary(project_path, output_file, ignore_files, ignore_paths)
    print(f"文档汇总已生成：{output_file}")
