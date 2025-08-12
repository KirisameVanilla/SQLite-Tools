"""
数据查询标签页组件
提供数据查询、添加、修改、删除记录的功能
"""

import tkinter as tk
from tkinter import ttk, messagebox


class QueryTab:
    def __init__(self, parent_notebook, logic, update_status_callback=None):
        self.logic = logic
        self.parent_notebook = parent_notebook
        self.update_status_callback = update_status_callback

        # 创建标签页框架
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="数据查询")

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 查询条件框架
        condition_frame = ttk.LabelFrame(self.frame, text="查询条件")
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
        ttk.Label(self.frame, text="查询结果").pack(anchor=tk.W)

        result_frame = ttk.Frame(self.frame)
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
            self.frame, orient=tk.HORIZONTAL, command=self.result_tree.xview
        )
        result_h_scroll.pack(fill=tk.X)
        self.result_tree.configure(xscrollcommand=result_h_scroll.set)

    def set_conn(self, conn):
        """设置数据库连接"""
        self.conn = conn

    def refresh_tables(self, tables):
        """刷新表列表"""
        self.query_table_combo["values"] = tables

    def on_query_table_change(self, event):
        """表选择变化事件"""
        pass  # 可以在这里添加表变化时的逻辑

    def execute_query(self):
        """执行查询"""
        table_name = self.query_table_var.get()
        if not table_name:
            messagebox.showwarning("警告", "请选择一个表")
            return
        try:
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            data = self.logic.execute_query(table_name)
            column_names = data["columns"]
            self.result_tree["columns"] = column_names
            self.result_tree["show"] = "headings"
            for col in column_names:
                self.result_tree.heading(col, text=col)
                self.result_tree.column(col, width=100)
            for row in data["rows"]:
                self.result_tree.insert("", tk.END, values=row)

            # 通知主窗口更新状态
            if self.update_status_callback:
                self.update_status_callback(
                    f"查询完成，返回 {len(data['rows'])} 条记录"
                )
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")

    def add_record(self):
        """添加记录"""
        if not hasattr(self, "conn") or not self.conn:
            messagebox.showwarning("警告", "请先打开一个数据库")
            return

        table_name = self.query_table_var.get()
        if not table_name:
            messagebox.showwarning("警告", "请选择一个表")
            return

        # 打开添加记录对话框
        self.open_record_dialog(table_name, "add")

    def modify_record(self):
        """修改记录"""
        if not hasattr(self, "conn") or not self.conn:
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
        """删除记录"""
        if not hasattr(self, "conn") or not self.conn:
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

            # 通知主窗口更新状态
            if self.update_status_callback:
                self.update_status_callback("记录删除成功")

        except Exception as e:
            messagebox.showerror("错误", f"删除记录失败: {str(e)}")

    def open_record_dialog(self, table_name, mode, values=None):
        """打开记录编辑对话框"""
        if not hasattr(self, "conn") or not self.conn:
            return

        # 获取主窗口引用
        root = self.frame.winfo_toplevel()

        dialog = tk.Toplevel(root)
        dialog.title(f"{'添加' if mode == 'add' else '修改'}记录 - {table_name}")
        dialog.geometry("400x300")
        dialog.transient(root)
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

                cursor = self.conn.cursor()

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

                # 通知主窗口更新状态
                if self.update_status_callback:
                    self.update_status_callback(
                        f"记录{'添加' if mode == 'add' else '修改'}成功"
                    )

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
