import os

EXCLUDE_DIRS = {".git", ".github", "__pycache__", "venv", "node_modules"}
EXCLUDE_FILES = {".gitignore", "README.md", "STRUCTURE.md"}

def generate_tree(directory, prefix=""):
    """Рекурсивно формирует список файлов и папок в виде Markdown."""
    if not os.path.exists(directory):
        return "⚠ Указанная папка не существует!\n"

    entries = sorted(os.listdir(directory))
    entries = [e for e in entries if e not in EXCLUDE_FILES]
    tree_md = ""

    for index, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = index == len(entries) - 1
        connector = "└── " if is_last else "├── "

        if os.path.isdir(path) and entry not in EXCLUDE_DIRS:
            tree_md += f"{prefix}{connector} **{entry}/**\n"
            tree_md += generate_tree(path, prefix + ("    " if is_last else "│   "))

        elif os.path.isfile(path):
            tree_md += f"{prefix}{connector} {entry}\n"

    return tree_md

def save_structure():
    """Запрашивает у пользователя путь к папке и создает STRUCTURE.md."""
    root_dir = input("Введите путь к папке проекта: ").strip()

    if not os.path.exists(root_dir):
        print("❌ Ошибка: указанная папка не существует.")
        return
    
    tree = f"# 📂 Структура проекта\n\n```\n{generate_tree(root_dir)}```\n"
    
    output_file = os.path.join(root_dir, "STRUCTURE.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tree)
    
    print(f"✅ Файл STRUCTURE.md создан в папке: {root_dir}")

if __name__ == "__main__":
    save_structure()
