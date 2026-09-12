import os
import argparse

def is_ignored(path, ignore_dirs):
    for ignore in ignore_dirs:
        if ignore in path.split(os.sep):
            return True
    return False

def generate_tree(dir_path, ignore_dirs, prefix=""):
    tree_str = ""
    try:
        items = sorted(os.listdir(dir_path))
    except PermissionError:
        return ""

    # 過濾掉不需要的資料夾
    items = [item for item in items if not is_ignored(os.path.join(dir_path, item), ignore_dirs)]

    for i, item in enumerate(items):
        path = os.path.join(dir_path, item)
        is_last = (i == len(items) - 1)
        tree_str += prefix + ("└── " if is_last else "├── ") + item + "\n"
        
        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            tree_str += generate_tree(path, ignore_dirs, prefix + extension)
    return tree_str

def main():
    parser = argparse.ArgumentParser(description="Pack code repository into a single text file for LLM prompts.")
    parser.add_argument("dir", nargs="?", default=".", help="Directory to pack (default: current directory)")
    parser.add_argument("-o", "--output", default="llm_prompt.txt", help="Output file name")
    args = parser.parse_args()

    ignore_dirs = ['.git', 'node_modules', '__pycache__', 'venv', 'env', '.idea', '.vscode']
    allowed_extensions = {'.py', '.js', '.ts', '.html', '.css', '.md', '.txt', '.json', '.java', '.cpp', '.h'}

    output_content = []
    output_content.append(f"# Codebase Context for {os.path.abspath(args.dir)}\n\n")

    # 將樹狀圖寫入最終文件
    output_content.append("## Directory Structure\n```text\n")
    output_content.append(os.path.basename(os.path.abspath(args.dir)) + "/\n")
    output_content.append(generate_tree(args.dir, ignore_dirs))
    output_content.append("```\n\n")

    for root, dirs, files in os.walk(args.dir):
        if is_ignored(root, ignore_dirs):
            continue

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in allowed_extensions:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    rel_path = os.path.relpath(filepath, args.dir)
                    output_content.append(f"## File: {rel_path}\n")
                    output_content.append("```" + (ext[1:] if len(ext) > 1 else "") + "\n")
                    output_content.append(content)
                    output_content.append("\n```\n\n")
                except Exception:
                    pass

    with open(args.output, 'w', encoding='utf-8') as f:
        f.writelines(output_content)
    print(f"✅ Successfully packed repository into {args.output}")

if __name__ == "__main__":
    main()
