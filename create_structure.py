import os

# 生成するディレクトリ構造を定義
dir_structure = {
    "app": ["main.py", "models.py", "schemas.py", "routes.py"],
    "app/templates": ["index.html"],
    "": ["requirements.txt"]  # ルートディレクトリに作成するファイル
}

def create_structure(base_path, structure):
    for dir_name, files in structure.items():
        dir_path = os.path.join(base_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)  # ディレクトリの作成

        for file_name in files:
            file_path = os.path.join(dir_path, file_name)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    pass  # 空のファイルを作成

if __name__ == "__main__":
    base_path = os.getcwd()  # 現在のディレクトリを基準とする
    create_structure(base_path, dir_structure)
    print("ディレクトリ構造の生成が完了しました。")
