"""
SQL执行标签页组件
提供SQL语句执行功能
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SQLTab:
    def __init__(
        self, parent_notebook, logic, update_status_callback=None, refresh_callback=None
    ):
        self.logic = logic
        self.parent_notebook = parent_notebook
        self.update_status_callback = update_status_callback
        self.refresh_callback = refresh_callback

        # 创建标签页框架
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="SQL执行")

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # SQL输入区域
        ttk.Label(self.frame, text="SQL语句").pack(anchor=tk.W)

        sql_input_frame = ttk.Frame(self.frame)
        sql_input_frame.pack(fill=tk.X, pady=(5, 10))

        self.sql_text = tk.Text(sql_input_frame, height=8)
        self.sql_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sql_scroll = ttk.Scrollbar(
            sql_input_frame, orient=tk.VERTICAL, command=self.sql_text.yview
        )
        sql_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.sql_text.configure(yscrollcommand=sql_scroll.set)

        # SQL执行按钮
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="执行SQL", command=self.execute_sql).pack(
            side=tk.LEFT
        )
        ttk.Button(
            button_frame, text="清空", command=lambda: self.sql_text.delete(1.0, tk.END)
        ).pack(side=tk.LEFT, padx=(10, 0))

        # SQL执行结果
        ttk.Label(self.frame, text="执行结果").pack(anchor=tk.W)

        sql_result_frame = ttk.Frame(self.frame)
        sql_result_frame.pack(fill=tk.BOTH, expand=True)

        self.sql_result_tree = ttk.Treeview(sql_result_frame)
        self.sql_result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sql_result_v_scroll = ttk.Scrollbar(
            sql_result_frame, orient=tk.VERTICAL, command=self.sql_result_tree.yview
        )
        sql_result_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.sql_result_tree.configure(yscrollcommand=sql_result_v_scroll.set)

        sql_result_h_scroll = ttk.Scrollbar(
            self.frame, orient=tk.HORIZONTAL, command=self.sql_result_tree.xview
        )
        sql_result_h_scroll.pack(fill=tk.X)
        self.sql_result_tree.configure(xscrollcommand=sql_result_h_scroll.set)

    def execute_sql(self):
        """执行SQL语句"""
        sql = self.sql_text.get(1.0, tk.END).strip()
        if not sql:
            messagebox.showwarning("警告", "请输入SQL语句")
            return
        try:
            # 清空之前的结果
            for item in self.sql_result_tree.get_children():
                self.sql_result_tree.delete(item)

            result = self.logic.execute_sql(sql)

            if "columns" in result:
                # 查询结果，显示数据
                column_names = result["columns"]
                self.sql_result_tree["columns"] = column_names
                self.sql_result_tree["show"] = "headings"
                for col in column_names:
                    self.sql_result_tree.heading(col, text=col)
                    self.sql_result_tree.column(col, width=100)
                for row in result["rows"]:
                    self.sql_result_tree.insert("", tk.END, values=row)

                # 通知主窗口更新状态
                if self.update_status_callback:
                    self.update_status_callback(
                        f"查询完成，返回 {len(result['rows'])} 条记录"
                    )
            else:
                # 非查询语句，显示影响行数
                if self.update_status_callback:
                    self.update_status_callback(
                        f"SQL执行成功，影响 {result.get('affected_rows', 0)} 行"
                    )

                # 如果有refresh_callback，调用它刷新数据库结构
                if self.refresh_callback:
                    self.refresh_callback()

        except Exception as e:
            messagebox.showerror("错误", f"SQL执行失败: {str(e)}")

    def clear_sql(self):
        """清空SQL文本"""
        self.sql_text.delete(1.0, tk.END)

    def set_sql(self, sql):
        """设置SQL文本"""
        self.sql_text.delete(1.0, tk.END)
        self.sql_text.insert(1.0, sql)
