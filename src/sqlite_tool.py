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
import sqlite3
import os
import shutil
from datetime import datetime
from typing import Optional

# 导出工具
from .export_utils import export_db_to_csv, export_db_to_xlsx


class SQLiteTool:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLite3 工具")
        self.root.geometry("1000x700")

        # 当前数据库连接
        self.conn: Optional[sqlite3.Connection] = None
        self.current_db_path: Optional[str] = None

        # 创建界面
        self.setup_ui()

    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 顶部工具栏
        self.create_toolbar(main_frame)

        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # 数据库结构标签页
        self.create_structure_tab(notebook)

        # 数据查询标签页
        self.create_query_tab(notebook)

        # SQL执行标签页
        self.create_sql_tab(notebook)

        # 状态栏
        self.create_status_bar(main_frame)

    def create_toolbar(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        # 数据库操作按钮
        ttk.Button(toolbar, text="新建数据库", command=self.create_database).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(toolbar, text="打开数据库", command=self.open_database).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(toolbar, text="导入数据库", command=self.import_database).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(toolbar, text="导出数据库", command=self.export_database).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        # 新增：导出为CSV和XLSX
        ttk.Button(toolbar, text="导出为CSV", command=self.export_csv).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(toolbar, text="导出为XLSX", command=self.export_xlsx).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        # 分隔符
        ttk.Separator(toolbar, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # 当前数据库信息
        self.db_info_label = ttk.Label(toolbar, text="未连接数据库")
        self.db_info_label.pack(side=tk.LEFT, padx=(0, 10))

    def create_structure_tab(self, notebook):
        # 数据库结构标签页
        structure_frame = ttk.Frame(notebook)
        notebook.add(structure_frame, text="数据库结构")

        # 左侧：表列表
        left_frame = ttk.Frame(structure_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(left_frame, text="表列表").pack(anchor=tk.W)

        # 表列表框
        self.tables_listbox = tk.Listbox(left_frame, width=20)
        self.tables_listbox.pack(fill=tk.Y, expand=True, pady=(5, 0))
        self.tables_listbox.bind("<<ListboxSelect>>", self.on_table_select)

        # 右侧：表结构和数据
        right_frame = ttk.Frame(structure_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 表结构
        ttk.Label(right_frame, text="表结构").pack(anchor=tk.W)

        # 创建表结构树形视图
        columns = ("列名", "数据类型", "是否为空", "默认值", "主键")
        self.structure_tree = ttk.Treeview(
            right_frame, columns=columns, show="headings", height=8
        )

        for col in columns:
            self.structure_tree.heading(col, text=col)
            self.structure_tree.column(col, width=100)

        self.structure_tree.pack(fill=tk.X, pady=(5, 10))

        # 表数据预览
        ttk.Label(right_frame, text="数据预览").pack(anchor=tk.W)

        # 数据预览框架
        data_frame = ttk.Frame(right_frame)
        data_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 数据树形视图（动态列）
        self.data_tree = ttk.Treeview(data_frame)
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动条
        v_scrollbar = ttk.Scrollbar(
            data_frame, orient=tk.VERTICAL, command=self.data_tree.yview
        )
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_tree.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(
            right_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview
        )
        h_scrollbar.pack(fill=tk.X)
        self.data_tree.configure(xscrollcommand=h_scrollbar.set)

    def export_csv(self):
        if not self.conn or not self.current_db_path:
            messagebox.showwarning("警告", "请先打开一个数据库")
            return
        db_path = self.current_db_path
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
        if not self.conn or not self.current_db_path:
            messagebox.showwarning("警告", "请先打开一个数据库")
            return
        db_path = self.current_db_path
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

    def create_query_tab(self, notebook):
        # 数据查询标签页
        query_frame = ttk.Frame(notebook)
        notebook.add(query_frame, text="数据查询")

        # 查询条件框架
        condition_frame = ttk.LabelFrame(query_frame, text="查询条件")
        condition_frame.pack(fill=tk.X, pady=(0, 10))

        # 表选择
        table_frame = ttk.Frame(condition_frame)
        table_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(table_frame, text="选择表:").pack(side=tk.LEFT)
        self.query_table_var = tk.StringVar()
        self.query_table_combo = ttk.Combobox(
            table_frame, textvariable=self.query_table_var, state="readonly"
        )
        self.query_table_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.query_table_combo.bind("<<ComboboxSelected>>", self.on_query_table_change)

        # 查询按钮
        ttk.Button(table_frame, text="查询", command=self.execute_query).pack(
            side=tk.RIGHT
        )
        ttk.Button(table_frame, text="添加记录", command=self.add_record).pack(
            side=tk.RIGHT, padx=(0, 5)
        )
        ttk.Button(table_frame, text="删除记录", command=self.delete_record).pack(
            side=tk.RIGHT, padx=(0, 5)
        )
        ttk.Button(table_frame, text="修改记录", command=self.modify_record).pack(
            side=tk.RIGHT, padx=(0, 5)
        )

        # 查询结果
        ttk.Label(query_frame, text="查询结果").pack(anchor=tk.W)

        result_frame = ttk.Frame(query_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.result_tree = ttk.Treeview(result_frame)
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 结果滚动条
        result_v_scroll = ttk.Scrollbar(
            result_frame, orient=tk.VERTICAL, command=self.result_tree.yview
        )
        result_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_tree.configure(yscrollcommand=result_v_scroll.set)

        result_h_scroll = ttk.Scrollbar(
            query_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview
        )
        result_h_scroll.pack(fill=tk.X)
        self.result_tree.configure(xscrollcommand=result_h_scroll.set)

    def create_sql_tab(self, notebook):
        # SQL执行标签页
        sql_frame = ttk.Frame(notebook)
        notebook.add(sql_frame, text="SQL执行")

        # SQL输入区域
        ttk.Label(sql_frame, text="SQL语句").pack(anchor=tk.W)

        sql_input_frame = ttk.Frame(sql_frame)
        sql_input_frame.pack(fill=tk.X, pady=(5, 10))

        self.sql_text = tk.Text(sql_input_frame, height=8)
        self.sql_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sql_scroll = ttk.Scrollbar(
            sql_input_frame, orient=tk.VERTICAL, command=self.sql_text.yview
        )
        sql_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.sql_text.configure(yscrollcommand=sql_scroll.set)

        # SQL执行按钮
        button_frame = ttk.Frame(sql_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="执行SQL", command=self.execute_sql).pack(
            side=tk.LEFT
        )
        ttk.Button(
            button_frame, text="清空", command=lambda: self.sql_text.delete(1.0, tk.END)
        ).pack(side=tk.LEFT, padx=(10, 0))

        # SQL执行结果
        ttk.Label(sql_frame, text="执行结果").pack(anchor=tk.W)

        sql_result_frame = ttk.Frame(sql_frame)
        sql_result_frame.pack(fill=tk.BOTH, expand=True)

        self.sql_result_tree = ttk.Treeview(sql_result_frame)
        self.sql_result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sql_result_v_scroll = ttk.Scrollbar(
            sql_result_frame, orient=tk.VERTICAL, command=self.sql_result_tree.yview
        )
        sql_result_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.sql_result_tree.configure(yscrollcommand=sql_result_v_scroll.set)

        sql_result_h_scroll = ttk.Scrollbar(
            sql_frame, orient=tk.HORIZONTAL, command=self.sql_result_tree.xview
        )
        sql_result_h_scroll.pack(fill=tk.X)
        self.sql_result_tree.configure(xscrollcommand=sql_result_h_scroll.set)

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
                # 创建新的数据库文件
                conn = sqlite3.connect(file_path)
                conn.close()
                self.open_database_file(file_path)
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
            self.open_database_file(file_path)

    def open_database_file(self, file_path):
        try:
            if self.conn:
                self.conn.close()

            self.conn = sqlite3.connect(file_path)
            self.current_db_path = file_path
            self.db_info_label.config(text=f"当前数据库: {os.path.basename(file_path)}")

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
                    shutil.copy2(source_file, target_file)
                    self.open_database_file(target_file)
                    self.update_status(f"已导入数据库: {os.path.basename(target_file)}")
                except Exception as e:
                    messagebox.showerror("错误", f"导入数据库失败: {str(e)}")

    def export_database(self):
        if not self.conn or not self.current_db_path:
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
                shutil.copy2(self.current_db_path, target_file)
                self.update_status(f"已导出数据库: {os.path.basename(target_file)}")
            except Exception as e:
                messagebox.showerror("错误", f"导出数据库失败: {str(e)}")

    def refresh_database_structure(self):
        if not self.conn:
            return

        try:
            # 获取所有表名
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            # 更新表列表
            self.tables_listbox.delete(0, tk.END)
            table_names = []
            for table in tables:
                table_name = table[0]
                self.tables_listbox.insert(tk.END, table_name)
                table_names.append(table_name)

            # 更新查询标签页的表选择下拉框
            self.query_table_combo["values"] = table_names

            self.update_status(f"已加载 {len(tables)} 个表")

        except Exception as e:
            messagebox.showerror("错误", f"刷新数据库结构失败: {str(e)}")

    def on_table_select(self, event):
        selection = self.tables_listbox.curselection()
        if selection:
            table_name = self.tables_listbox.get(selection[0])
            self.show_table_structure(table_name)
            self.show_table_data(table_name)

    def show_table_structure(self, table_name):
        if not self.conn:
            return

        try:
            # 清空结构树
            for item in self.structure_tree.get_children():
                self.structure_tree.delete(item)

            # 获取表结构
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            for col in columns:
                cid, name, data_type, not_null, default_value, pk = col
                is_null = "否" if not_null else "是"
                is_pk = "是" if pk else "否"
                default_val = default_value if default_value is not None else ""

                self.structure_tree.insert(
                    "", tk.END, values=(name, data_type, is_null, default_val, is_pk)
                )

        except Exception as e:
            messagebox.showerror("错误", f"显示表结构失败: {str(e)}")

    def show_table_data(self, table_name, limit=100):
        if not self.conn:
            return

        try:
            # 清空数据树
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)

            # 获取表数据
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            rows = cursor.fetchall()

            # 获取列名
            column_names = [description[0] for description in cursor.description]

            # 设置列
            self.data_tree["columns"] = column_names
            self.data_tree["show"] = "headings"

            for col in column_names:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100)

            # 插入数据
            for row in rows:
                self.data_tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("错误", f"显示表数据失败: {str(e)}")

    def on_query_table_change(self, event):
        pass  # 可以在这里添加表变化时的逻辑

    def execute_query(self):
        if not self.conn:
            messagebox.showwarning("警告", "请先打开一个数据库")
            return

        table_name = self.query_table_var.get()
        if not table_name:
            messagebox.showwarning("警告", "请选择一个表")
            return

        try:
            # 清空结果树
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)

            # 执行查询
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            # 获取列名
            column_names = [description[0] for description in cursor.description]

            # 设置列
            self.result_tree["columns"] = column_names
            self.result_tree["show"] = "headings"

            for col in column_names:
                self.result_tree.heading(col, text=col)
                self.result_tree.column(col, width=100)

            # 插入数据
            for row in rows:
                self.result_tree.insert("", tk.END, values=row)

            self.update_status(f"查询完成，返回 {len(rows)} 条记录")

        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")

    def add_record(self):
        if not self.conn:
            messagebox.showwarning("警告", "请先打开一个数据库")
            return

        table_name = self.query_table_var.get()
        if not table_name:
            messagebox.showwarning("警告", "请选择一个表")
            return

        # 打开添加记录对话框
        self.open_record_dialog(table_name, "add")

    def modify_record(self):
        if not self.conn:
            messagebox.showwarning("警告", "请先打开一个数据库")
            return

        selection = self.result_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要修改的记录")
            return

        table_name = self.query_table_var.get()
        if not table_name:
            messagebox.showwarning("警告", "请选择一个表")
            return

        # 获取选中的记录数据
        selected_item = self.result_tree.item(selection[0])
        values = selected_item["values"]

        # 打开修改记录对话框
        self.open_record_dialog(table_name, "modify", values)

    def delete_record(self):
        if not self.conn:
            messagebox.showwarning("警告", "请先打开一个数据库")
            return

        selection = self.result_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的记录")
            return

        if not messagebox.askyesno("确认", "确定要删除选中的记录吗？"):
            return

        table_name = self.query_table_var.get()
        if not table_name:
            messagebox.showwarning("警告", "请选择一个表")
            return

        try:
            # 获取选中的记录数据
            selected_item = self.result_tree.item(selection[0])
            values = selected_item["values"]

            # 获取表的主键列
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            # 构建删除语句（使用所有列作为条件）
            column_names = [col[1] for col in columns]
            where_conditions = []
            params = []

            for i, (col_name, value) in enumerate(zip(column_names, values)):
                if value is not None:
                    where_conditions.append(f"{col_name} = ?")
                    params.append(value)
                else:
                    where_conditions.append(f"{col_name} IS NULL")

            where_clause = " AND ".join(where_conditions)
            delete_sql = f"DELETE FROM {table_name} WHERE {where_clause}"

            cursor.execute(delete_sql, params)
            self.conn.commit()

            # 刷新查询结果
            self.execute_query()
            self.update_status("记录删除成功")

        except Exception as e:
            messagebox.showerror("错误", f"删除记录失败: {str(e)}")

    def open_record_dialog(self, table_name, mode, values=None):
        """打开记录编辑对话框"""
        if not self.conn:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"{'添加' if mode == 'add' else '修改'}记录 - {table_name}")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # 获取表结构
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        # 创建输入字段
        entries = {}
        row = 0

        for col in columns:
            cid, col_name, data_type, not_null, default_value, pk = col

            ttk.Label(dialog, text=f"{col_name} ({data_type})").grid(
                row=row, column=0, sticky=tk.W, padx=5, pady=2
            )

            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=row, column=1, padx=5, pady=2)

            # 如果是修改模式，填入当前值
            if mode == "modify" and values and row < len(values):
                entry.insert(0, str(values[row]) if values[row] is not None else "")

            entries[col_name] = entry
            row += 1

        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)

        def save_record():
            if not self.conn:
                messagebox.showerror("错误", "数据库连接已断开")
                return

            try:
                # 获取输入值
                input_values = {}
                for col_name, entry in entries.items():
                    value = entry.get().strip()
                    input_values[col_name] = value if value else None

                if mode == "add":
                    # 插入新记录
                    columns_str = ", ".join(input_values.keys())
                    placeholders = ", ".join(["?" for _ in input_values])
                    sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    cursor.execute(sql, list(input_values.values()))

                else:  # modify
                    # 更新记录
                    set_clauses = []
                    params = []

                    for col_name, value in input_values.items():
                        set_clauses.append(f"{col_name} = ?")
                        params.append(value)

                    # 构建WHERE条件（使用原始值）
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    table_columns = cursor.fetchall()

                    where_conditions = []
                    where_params = []

                    for i, col in enumerate(table_columns):
                        col_name = col[1]
                        if values and i < len(values):
                            original_value = values[i]
                            if original_value is not None:
                                where_conditions.append(f"{col_name} = ?")
                                where_params.append(original_value)
                            else:
                                where_conditions.append(f"{col_name} IS NULL")

                    where_clause = " AND ".join(where_conditions)
                    set_clause = ", ".join(set_clauses)
                    sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

                    cursor.execute(sql, params + where_params)

                self.conn.commit()
                dialog.destroy()

                # 刷新查询结果
                self.execute_query()
                self.update_status(f"记录{'添加' if mode == 'add' else '修改'}成功")

            except Exception as e:
                messagebox.showerror(
                    "错误", f"{'添加' if mode == 'add' else '修改'}记录失败: {str(e)}"
                )

        ttk.Button(button_frame, text="保存", command=save_record).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def execute_sql(self):
        if not self.conn:
            messagebox.showwarning("警告", "请先打开一个数据库")
            return

        sql = self.sql_text.get(1.0, tk.END).strip()
        if not sql:
            messagebox.showwarning("警告", "请输入SQL语句")
            return

        try:
            # 清空结果树
            for item in self.sql_result_tree.get_children():
                self.sql_result_tree.delete(item)

            cursor = self.conn.cursor()
            cursor.execute(sql)

            if cursor.description:  # SELECT查询
                # 获取列名
                column_names = [description[0] for description in cursor.description]
                rows = cursor.fetchall()

                # 设置列
                self.sql_result_tree["columns"] = column_names
                self.sql_result_tree["show"] = "headings"

                for col in column_names:
                    self.sql_result_tree.heading(col, text=col)
                    self.sql_result_tree.column(col, width=100)

                # 插入数据
                for row in rows:
                    self.sql_result_tree.insert("", tk.END, values=row)

                self.update_status(f"查询完成，返回 {len(rows)} 条记录")

            else:  # INSERT, UPDATE, DELETE等
                self.conn.commit()
                affected_rows = cursor.rowcount
                self.update_status(f"SQL执行成功，影响 {affected_rows} 行")

                # 刷新数据库结构（可能创建了新表）
                self.refresh_database_structure()

        except Exception as e:
            messagebox.showerror("错误", f"SQL执行失败: {str(e)}")
