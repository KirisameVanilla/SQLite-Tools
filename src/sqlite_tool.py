"""
SQLite3 桌面工具
功能：
- 导入/导出 .db/.db3 文件
- 查看数据库结构
- 查询和修改数据
- 执行SQL语句
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime
from src.utils import SQLiteUtils
from src.utils import export_db_to_csv, export_db_to_xlsx
from src.gui import StructureTab, QueryTab, SQLTab


class SQLiteTool:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLite3 工具")
        self.root.geometry("1000x700")

        # 逻辑层
        self.logic = SQLiteUtils()

        # 创建界面
        self.setup_ui()

    def setup_ui(self):
        # 菜单栏
        self.create_menu()

        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 顶部工具栏（只显示数据库信息）
        self.create_toolbar(main_frame)

        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # 创建标签页组件
        self.structure_tab = StructureTab(notebook, self.logic)
        self.query_tab = QueryTab(notebook, self.logic, self.update_status)
        self.sql_tab = SQLTab(
            notebook, self.logic, self.update_status, self.refresh_database_structure
        )

        # 状态栏
        self.create_status_bar(main_frame)

    def create_toolbar(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        # 只显示当前数据库信息
        self.db_info_label = ttk.Label(toolbar, text="未连接数据库")
        self.db_info_label.pack(side=tk.LEFT, padx=(0, 10))

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建数据库", command=self.create_database)
        file_menu.add_command(label="打开数据库", command=self.open_database)
        file_menu.add_command(label="导入数据库", command=self.import_database)
        file_menu.add_command(label="导出数据库", command=self.export_database)
        file_menu.add_separator()
        file_menu.add_command(label="导出为CSV", command=self.export_csv)
        file_menu.add_command(label="导出为XLSX", command=self.export_xlsx)
        menubar.add_cascade(label="文件", menu=file_menu)
        self.root.config(menu=menubar)

    def export_csv(self):
        if not self.logic.current_db_path:
            messagebox.showwarning("警告", "请先打开一个数据库")
            return
        db_path = self.logic.current_db_path

        db_name = os.path.splitext(os.path.basename(db_path))[0]
        output_dir = filedialog.askdirectory(title="选择导出CSV的文件夹")
        if not output_dir:
            return
        try:
            export_db_to_csv(db_path, os.path.join(output_dir, db_name))
            self.update_status(f"已导出为CSV: {os.path.join(output_dir, db_name)}")
            messagebox.showinfo(
                "成功", f"已导出为CSV: {os.path.join(output_dir, db_name)}"
            )
        except Exception as e:
            messagebox.showerror("错误", f"导出CSV失败: {str(e)}")

    def export_xlsx(self):
        if not self.logic.current_db_path:
            messagebox.showwarning("警告", "请先打开一个数据库")
            return
        db_path = self.logic.current_db_path

        db_name = os.path.splitext(os.path.basename(db_path))[0]
        output_path = filedialog.asksaveasfilename(
            title="导出为XLSX",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
            initialfile=f"{db_name}.xlsx",
        )
        if not output_path:
            return
        try:
            export_db_to_xlsx(db_path, output_path)
            self.update_status(f"已导出为XLSX: {output_path}")
            messagebox.showinfo("成功", f"已导出为XLSX: {output_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出XLSX失败: {str(e)}")

    def create_status_bar(self, parent):
        self.status_bar = ttk.Label(parent, text="就绪", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

    def update_status(self, message):
        self.status_bar.config(
            text=f"{datetime.now().strftime('%H:%M:%S')} - {message}"
        )

    def create_database(self):
        file_path = filedialog.asksaveasfilename(
            title="新建数据库",
            defaultextension=".db",
            filetypes=[
                ("SQLite数据库", "*.db"),
                ("SQLite数据库", "*.db3"),
                ("所有文件", "*.*"),
            ],
        )
        if file_path:
            try:
                self.logic.create_database(file_path)
                self.db_info_label.config(
                    text=f"当前数据库: {os.path.basename(file_path)}"
                )
                self.refresh_database_structure()
                self.update_status(f"已创建数据库: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"创建数据库失败: {str(e)}")

    def open_database(self):
        file_path = filedialog.askopenfilename(
            title="打开数据库",
            filetypes=[
                ("SQLite数据库", "*.db"),
                ("SQLite数据库", "*.db3"),
                ("所有文件", "*.*"),
            ],
        )
        if file_path:
            try:
                self.logic.open_database_file(file_path)
                self.db_info_label.config(
                    text=f"当前数据库: {os.path.basename(file_path)}"
                )
                self.refresh_database_structure()
                self.update_status(f"已打开数据库: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"打开数据库失败: {str(e)}")

    def import_database(self):
        source_file = filedialog.askopenfilename(
            title="选择要导入的数据库",
            filetypes=[
                ("SQLite数据库", "*.db"),
                ("SQLite数据库", "*.db3"),
                ("所有文件", "*.*"),
            ],
        )
        if source_file:
            target_file = filedialog.asksaveasfilename(
                title="保存到",
                defaultextension=".db",
                filetypes=[
                    ("SQLite数据库", "*.db"),
                    ("SQLite数据库", "*.db3"),
                    ("所有文件", "*.*"),
                ],
            )
            if target_file:
                try:
                    self.logic.import_database(source_file, target_file)
                    self.db_info_label.config(
                        text=f"当前数据库: {os.path.basename(target_file)}"
                    )
                    self.refresh_database_structure()
                    self.update_status(f"已导入数据库: {os.path.basename(target_file)}")
                except Exception as e:
                    messagebox.showerror("错误", f"导入数据库失败: {str(e)}")

    def export_database(self):
        if not self.logic.current_db_path:
            messagebox.showwarning("警告", "请先打开一个数据库")
            return
        target_file = filedialog.asksaveasfilename(
            title="导出数据库到",
            defaultextension=".db",
            filetypes=[
                ("SQLite数据库", "*.db"),
                ("SQLite数据库", "*.db3"),
                ("所有文件", "*.*"),
            ],
        )
        if target_file:
            try:
                self.logic.export_database(target_file)
                self.update_status(f"已导出数据库: {os.path.basename(target_file)}")
            except Exception as e:
                messagebox.showerror("错误", f"导出数据库失败: {str(e)}")

    def refresh_database_structure(self):
        """刷新数据库结构，通知所有标签页更新"""
        try:
            tables = self.logic.get_tables()

            # 通知各个标签页更新表列表
            self.structure_tab.refresh_tables(tables)
            self.query_tab.refresh_tables(tables)

            # 更新查询标签页的数据库连接
            if hasattr(self.logic, "conn"):
                self.query_tab.set_conn(self.logic.conn)

            self.update_status(f"已加载 {len(tables)} 个表")
        except Exception as e:
            messagebox.showerror("错误", f"刷新数据库结构失败: {str(e)}")
