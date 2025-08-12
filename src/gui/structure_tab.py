"""
数据库结构标签页组件
显示数据库中的表列表、表结构和数据预览
"""

import tkinter as tk
from tkinter import ttk, messagebox


class StructureTab:
    def __init__(self, parent_notebook, logic):
        self.logic = logic
        self.parent_notebook = parent_notebook

        # 创建标签页框架
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="数据库结构")

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 左侧：表列表
        left_frame = ttk.Frame(self.frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(left_frame, text="表列表").pack(anchor=tk.W)

        # 表列表框
        self.tables_listbox = tk.Listbox(left_frame, width=20)
        self.tables_listbox.pack(fill=tk.Y, expand=True, pady=(5, 0))
        self.tables_listbox.bind("<<ListboxSelect>>", self.on_table_select)

        # 右侧：表结构和数据
        right_frame = ttk.Frame(self.frame)
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

    def refresh_tables(self, tables):
        """刷新表列表"""
        self.tables_listbox.delete(0, tk.END)
        for table_name in tables:
            self.tables_listbox.insert(tk.END, table_name)

    def on_table_select(self, event):
        """表选择事件处理"""
        selection = self.tables_listbox.curselection()
        if selection:
            table_name = self.tables_listbox.get(selection[0])
            self.show_table_structure(table_name)
            self.show_table_data(table_name)

    def show_table_structure(self, table_name):
        """显示表结构"""
        try:
            for item in self.structure_tree.get_children():
                self.structure_tree.delete(item)
            columns = self.logic.get_table_structure(table_name)
            for col in columns:
                is_null = "否" if col["not_null"] else "是"
                is_pk = "是" if col["pk"] else "否"
                default_val = (
                    col["default_value"] if col["default_value"] is not None else ""
                )
                self.structure_tree.insert(
                    "",
                    tk.END,
                    values=(col["name"], col["data_type"], is_null, default_val, is_pk),
                )
        except Exception as e:
            messagebox.showerror("错误", f"显示表结构失败: {str(e)}")

    def show_table_data(self, table_name, limit=100):
        """显示表数据预览"""
        try:
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            data = self.logic.get_table_data(table_name, limit)
            column_names = data["columns"]
            self.data_tree["columns"] = column_names
            self.data_tree["show"] = "headings"
            for col in column_names:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100)
            for row in data["rows"]:
                self.data_tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("错误", f"显示表数据失败: {str(e)}")
