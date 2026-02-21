# 高级界面配置指南

## 🎨 Dashboard 功能

### 可视化任务看板

#### 实时进度条
```
[██████████████████████░░░░░░░░░░░░░░░░░░░░░░] 66.7%
```

#### 任务状态追踪
- 🔄 进行中
- ✅ 已完成
- ⏸️ 等待中
- ❌ 失败

#### 任务汇总
```
总任务: 2
已完成: 1 ✅
进行中: 0 无
总耗时: 4.3 秒
```

---

## 🚀 使用方法

### 1. 基础使用（集成到你的脚本）

```python
from src.utils.dashboard import ProgressTracker, Dashboard

# 创建追踪器
tracker = ProgressTracker()

# 开始任务
tracker.start_task("task1", "GitHub 代码推送", 3)

# 更新进度
tracker.update_task("task1", step=1, message="正在压缩文件...")

# 完成任务
tracker.complete_task("task1", message="推送成功：41 个文件")

# 显示汇总
tracker.show_summary()
```

### 2. 看板模式（推荐）

```python
from src.utils.dashboard import ProgressTracker, Dashboard

tracker = ProgressTracker()
dashboard = Dashboard(tracker)

# 添加多个任务
tracker.start_task("task1", "GitHub 代码推送", 3)
tracker.start_task("task2", "1号工作站安全审计", 5)

# 刷新看板（自动更新显示）
dashboard.show()
```

### 3. 集成到 LOF 套利策略

```python
# 在 lof_arbitrage.py 中
from src.utils.dashboard import ProgressTracker

class LOFArbitrage:
    def __init__(self, ...):
        self.tracker = ProgressTracker()
        self.dashboard = Dashboard(self.tracker)

    def scan_opportunities(self):
        # 开始扫描任务
        self.tracker.start_task("scan", "扫描套利机会", total_steps=len(self.watchlist))

        for fund_code in self.watchlist:
            # 更新进度
            self.tracker.update_task("scan", message=f"扫描 {fund_code}...")

            # 扫描逻辑
            self.check_arbitrage_opportunity(data)

        # 完成扫描
        self.tracker.complete_task("scan", message=f"发现 {len(self.opportunities)} 个机会")

        # 显示汇总
        self.dashboard.show()
```

---

## 🎯 高级功能（可选扩展）

### 1. 多任务并行

```python
# 同时运行多个任务
tracker.start_task("git", "Git 操作", 3)
tracker.start_task("test", "运行测试", 2)
tracker.start_task("deploy", "部署到生产", 4)

dashboard.show()
```

### 2. 子任务嵌套

```python
# 主任务
tracker.start_task("main", "主任务", total_steps=3)

# 子任务 1
tracker.update_task("main", step=1, message="步骤 1：备份数据")

# 子任务 2
tracker.update_task("main", step=2, message="步骤 2：执行迁移")

# 子任务 3
tracker.update_task("main", step=3, message="步骤 3：验证结果")

tracker.complete_task("main")
```

### 3. 错误处理

```python
try:
    tracker.start_task("risky", "风险操作", 1)
    # 执行操作
    tracker.complete_task("risky", message="操作成功")
except Exception as e:
    # 可以扩展支持失败状态
    print(f"❌ 任务失败: {e}")
```

### 4. 自定义样式

可以修改 `dashboard.py` 中的以下方法来自定义样式：

- `_show_divider()` - 分隔线样式
- `_show_header()` - 标题样式
- `_show_footer()` - 页脚样式
- 进度条字符（当前使用 `█` 和 `░`）

---

## 🔧 配置选项

### 自动刷新看板

```python
import time

tracker = ProgressTracker()
dashboard = Dashboard(tracker)

# 自动刷新（每 1 秒）
tracker.start_task("auto", "自动刷新任务", total_steps=10)

for i in range(10):
    tracker.update_task("auto", step=i+1)
    dashboard.show()  # 每次更新都刷新看板
    time.sleep(1)

tracker.complete_task("auto")
```

### 静默模式（不显示进度）

```python
# 在不需要进度显示时使用
tracker = ProgressTracker()
tracker.start_task("quiet", "静默任务", 1)
# 只在结束时显示
tracker.complete_task("quiet")
```

---

## 📊 与通知系统集成

```python
from src.utils.dashboard import ProgressTracker
from src.utils.notifier import NotificationManager

tracker = ProgressTracker()
notifier = NotificationManager(notification_config)

# 任务完成时发送通知
def on_task_complete(task_name, result):
    tracker.show_summary()

    # 发送 Telegram 通知
    notifier.send(
        title=f"✅ 任务完成: {task_name}",
        message=f"任务详情: {result}"
    )

tracker.complete_task("task1", "推送成功")
```

---

## 💡 最佳实践

### 1. 任务粒度
- 任务不要太大（避免进度条不更新）
- 合理的步数：3-10 步

### 2. 消息描述
- 使用简洁、清晰的描述
- 包含有用的上下文信息

### 3. 进度更新
- 不要太频繁（避免刷屏）
- 关键节点更新即可

### 4. 错误处理
- 始终捕获异常
- 提供有用的错误信息

---

## 🎨 样式示例

### 简洁模式
```
────────────────────────────
🚀 开始任务: 备份数据
────────────────────────────
```

### 详细模式
```
────────────────────────────
🚀 开始任务: 备份数据
📝 任务 ID: backup-001
📊 步骤数: 3
────────────────────────────
```

### 高级模式（带看板）
```
══════════════════════════════════
 ║  🤖  大龙虾任务看板                ║
 ║  📅  2026-02-21 14:50            ║
══════════════════════════════════
 ║  🔄 任务1              进行中    [███░░░░░░] 30% ║
 ║  ✅ 任务2              已完成    [████████] 100% ║
══════════════════════════════════
```

---

**需要更多功能吗？**
- 彩色输出
- 交互式看板
- 日志集成
- 统计图表
