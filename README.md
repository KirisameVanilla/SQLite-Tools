# SQLite3 桌面工具

一个功能完整的SQLite3数据库管理桌面应用程序，使用Python和Tkinter开发。

## 功能特性

### 数据库操作
- ✅ 新建SQLite数据库（.db/.db3文件）
- ✅ 打开现有数据库文件
- ✅ 导入数据库文件
- ✅ 导出数据库文件
- ✅ 实时显示当前连接的数据库信息

### 数据库结构查看
- ✅ 显示所有数据表列表
- ✅ 查看表结构（列名、数据类型、是否为空、默认值、主键）
- ✅ 预览表数据（前100条记录）
- ✅ 支持水平和垂直滚动

### 数据查询与管理
- ✅ 选择表进行数据查询
- ✅ 添加新记录到表中
- ✅ 修改现有记录
- ✅ 删除选中记录
- ✅ 直观的表格显示查询结果

### SQL语句执行
- ✅ 多行SQL语句编辑器
- ✅ 执行任意SQL语句（SELECT、INSERT、UPDATE、DELETE、CREATE等）
- ✅ 显示查询结果
- ✅ 错误提示和调试信息

### 界面特性
- ✅ 现代化的标签页界面
- ✅ 状态栏显示操作信息和时间
- ✅ 工具栏快速操作按钮
- ✅ 响应式布局适配不同屏幕尺寸

## 安装与运行

### 环境要求
- Python 3.7+
- tkinter（通常随Python安装）
- sqlite3（Python标准库）

### 快速开始

1. **克隆或下载项目文件**
   ```
   SQLite-Tools/
   ├── sqlite_tool.py          # 主程序文件
   ├── create_sample_db.py     # 示例数据库创建脚本
   ├── run_tool.bat           # Windows启动脚本
   └── README.md              # 说明文档
   ```

2. **创建虚拟环境**（推荐）
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install pandas  # 可选，用于数据处理
   ```

4. **运行程序**
   
   **方法一：直接运行Python脚本**
   ```bash
   python sqlite_tool.py
   ```
   
   **方法二：使用Windows批处理脚本**
   双击 `run_tool.bat` 文件

5. **创建示例数据库**（可选）
   ```bash
   python create_sample_db.py
   ```

## 使用指南

### 基本操作流程

1. **启动应用程序**
   - 运行 `sqlite_tool.py` 或双击 `run_tool.bat`

2. **打开/创建数据库**
   - 点击"新建数据库"创建新的数据库文件
   - 点击"打开数据库"选择现有的.db或.db3文件
   - 点击"导入数据库"从其他位置复制数据库文件

3. **查看数据库结构**
   - 切换到"数据库结构"标签页
   - 在左侧表列表中选择要查看的表
   - 右侧会显示表结构和数据预览

4. **查询和管理数据**
   - 切换到"数据查询"标签页
   - 从下拉菜单选择要操作的表
   - 点击"查询"显示所有记录
   - 使用"添加记录"、"修改记录"、"删除记录"按钮管理数据

5. **执行SQL语句**
   - 切换到"SQL执行"标签页
   - 在文本框中输入SQL语句
   - 点击"执行SQL"运行语句
   - 查看执行结果

### 功能说明

#### 数据库结构标签页
- **表列表**：显示数据库中的所有表
- **表结构**：显示选中表的列信息
- **数据预览**：显示表中的前100条记录

#### 数据查询标签页
- **表选择**：选择要操作的数据表
- **查询按钮**：显示表中的所有数据
- **添加记录**：打开表单添加新记录
- **修改记录**：修改选中的记录
- **删除记录**：删除选中的记录

#### SQL执行标签页
- **SQL编辑器**：支持多行SQL语句输入
- **执行SQL**：执行输入的SQL语句
- **清空按钮**：清空编辑器内容
- **结果显示**：显示SQL执行结果

### 支持的SQL操作

```sql
-- 创建表
CREATE TABLE example (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    value REAL
);

-- 插入数据
INSERT INTO example (name, value) VALUES ('测试', 123.45);

-- 查询数据
SELECT * FROM example WHERE value > 100;

-- 更新数据
UPDATE example SET value = 200 WHERE name = '测试';

-- 删除数据
DELETE FROM example WHERE id = 1;

-- 删除表
DROP TABLE example;
```

## 示例数据库

运行 `create_sample_db.py` 会创建一个包含以下表的示例数据库：

- **users表**：用户信息（id, name, email, age, created_at）
- **products表**：产品信息（id, name, price, category, in_stock）
- **orders表**：订单信息（id, user_id, product_id, quantity, order_date）

## 注意事项

1. **数据备份**：在进行重要操作前，请备份数据库文件
2. **SQL语句**：执行SQL语句时请谨慎，特别是DELETE和DROP操作
3. **文件权限**：确保程序对数据库文件有读写权限
4. **编码支持**：支持UTF-8编码的中文数据

## 故障排除

### 常见问题

1. **无法打开数据库文件**
   - 检查文件是否存在
   - 确认文件不被其他程序占用
   - 验证文件权限

2. **SQL执行错误**
   - 检查SQL语法是否正确
   - 确认表名和列名拼写
   - 查看错误提示信息

3. **程序无法启动**
   - 确认Python环境正确安装
   - 检查tkinter是否可用
   - 验证虚拟环境是否正确激活

## 技术特性

- **开发语言**：Python 3.7+
- **GUI框架**：Tkinter
- **数据库**：SQLite3
- **架构**：面向对象设计
- **兼容性**：Windows、Linux、macOS

## 更新日志

### v1.0.0
- 实现基本的数据库操作功能
- 支持数据库文件的导入导出
- 提供图形化的数据管理界面
- 集成SQL语句执行器
- 添加数据表结构查看功能

## 许可证

本项目采用MIT许可证，详情请参见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个工具！
