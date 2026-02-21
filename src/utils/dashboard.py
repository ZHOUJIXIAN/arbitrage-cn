"""
任务进度显示模块 - 高级可视化输出
"""
import time
from typing import Dict, List, Optional
from datetime import datetime


class ProgressTracker:
    """任务进度追踪器"""

    def __init__(self):
        self.tasks = {}
        self.current_task = None
        self.start_time = datetime.now()

    def start_task(self, task_id: str, name: str, total_steps: int = 1):
        """开始一个任务"""
        self.tasks[task_id] = {
            'name': name,
            'total_steps': total_steps,
            'current_step': 0,
            'start_time': datetime.now(),
            'status': 'running'
        }
        self.current_task = task_id
        self._show_task_start(task_id, name, total_steps)

    def update_task(self, task_id: str, step: int = 1, message: str = ""):
        """更新任务进度"""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        task['current_step'] += step

        self._show_progress(task_id, task['name'], message)

    def complete_task(self, task_id: str, message: str = ""):
        """完成任务"""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        task['status'] = 'completed'
        task['end_time'] = datetime.now()
        duration = (task['end_time'] - task['start_time']).total_seconds()

        self._show_task_complete(task_id, task['name'], duration, message)

    def show_summary(self):
        """显示任务汇总"""
        self._show_divider()
        print(" 📊  任务汇总")
        self._show_divider()

        total_tasks = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t['status'] == 'completed')
        running = sum(1 for t in self.tasks.values() if t['status'] == 'running')

        print(f"  总任务数: {total_tasks}")
        print(f"  已完成: {completed} {'✅' if completed == total_tasks else f'{completed}/{total_tasks}'}")
        print(f"  进行中: {running} {'🔄' if running > 0 else '无'}")

        if completed > 0:
            total_time = datetime.now() - self.start_time
            print(f"  总耗时: {total_time.total_seconds():.1f} 秒")

        self._show_divider()

    def _show_divider(self):
        """显示分隔线"""
        print("─" * 60)

    def _show_task_start(self, task_id: str, name: str, total_steps: int):
        """显示任务开始"""
        self._show_divider()
        print(f" 🚀  开始任务: {name}")
        print(f" 📝  任务 ID: {task_id}")
        print(f" 📊  步骤数: {total_steps}")
        self._show_divider()

    def _show_progress(self, task_id: str, name: str, message: str):
        """显示进度"""
        task = self.tasks[task_id]
        progress = (task['current_step'] / task['total_steps']) * 100
        bar_length = 40
        filled_length = int(bar_length * progress / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)

        self._show_divider()
        print(f" 🔄  正在执行: {name}")
        print(f" 📊  进度: [{bar}] {progress:.1f}%")
        print(f" 📝  {message}")
        self._show_divider()

    def _show_task_complete(self, task_id: str, name: str, duration: float, message: str):
        """显示任务完成"""
        self._show_divider()
        print(f" ✅  任务完成: {name}")
        print(f" ⏱️  耗时: {duration:.2f} 秒")
        print(f" 📝  {message}")
        self._show_divider()


class Dashboard:
    """任务看板 - 实时显示所有任务状态"""

    def __init__(self, tracker: ProgressTracker):
        self.tracker = tracker
        self.last_update = datetime.now()

    def show(self):
        """显示看板"""
        self._clear_screen()
        self._show_header()
        self._show_tasks()
        self._show_footer()

    def _clear_screen(self):
        """清屏（跨平台）"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def _show_header(self):
        """显示标题"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._show_divider()
        print(" ╔════════════════════════════════════════════════════════════╗")
        print(f" ║  🤖  大龙虾任务看板                                          ║")
        print(f" ║  📅  {now}                                    ║")
        print(" ╠════════════════════════════════════════════════════════════╣")

    def _show_tasks(self):
        """显示所有任务"""
        if not self.tracker.tasks:
            print(" ║  📭  当前没有任务                                       ║")
            print(" ╚════════════════════════════════════════════════════════════╝")
            return

        task_list = list(self.tracker.tasks.values())
        task_list.sort(key=lambda x: (x['status'] == 'running', x['start_time']), reverse=True)

        for task in task_list:
            status_icon = "🔄" if task['status'] == 'running' else "✅" if task['status'] == 'completed' else "⏸️"
            status_text = "进行中" if task['status'] == 'running' else "已完成" if task['status'] == 'completed' else "等待中"

            if task['status'] == 'running':
                progress = (task['current_step'] / task['total_steps']) * 100
                bar_length = 40
                filled_length = int(bar_length * progress / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)
                progress_text = f"[{bar}] {progress:.0f}%"
            else:
                progress_text = "100%" if task['status'] == 'completed' else "0%"

            name = task['name'][:40] + "..." if len(task['name']) > 40 else task['name']
            print(f" ║  {status_icon}  {name:<45}  {status_text:<10}  {progress_text:<15}  ║")

        print(" ╠════════════════════════════════════════════════════════════╣")

    def _show_footer(self):
        """显示页脚"""
        total_tasks = len(self.tracker.tasks)
        completed = sum(1 for t in self.tracker.tasks.values() if t['status'] == 'completed')

        print(f" ║  📊  总任务: {total_tasks}  │  已完成: {completed}  │  进行中: {sum(1 for t in self.tracker.tasks.values() if t['status'] == 'running')}  ║")
        print(" ╚════════════════════════════════════════════════════════════╝")

    def _show_divider(self):
        """显示分隔线"""
        print("═" * 60)


def demo_dashboard():
    """演示看板功能"""
    print("\n" + "="*60)
    print("📊 任务看板演示")
    print("="*60 + "\n")

    tracker = ProgressTracker()
    dashboard = Dashboard(tracker)

    # 模拟任务
    tracker.start_task("task1", "GitHub 代码推送", 3)

    time.sleep(1)
    tracker.update_task("task1", message="正在压缩文件...")
    dashboard.show()

    time.sleep(1)
    tracker.update_task("task1", message="正在连接 GitHub...")
    dashboard.show()

    tracker.complete_task("task1", message="推送成功：41 个文件")

    # 添加新任务
    tracker.start_task("task2", "1号工作站安全审计", 5)

    time.sleep(1)
    tracker.update_task("task2", message="检查防火墙状态...")
    dashboard.show()

    time.sleep(1)
    tracker.update_task("task2", step=1, message="检查开放端口...")
    dashboard.show()

    tracker.complete_task("task2", message="安全加固完成")

    # 显示汇总
    dashboard.show()
    tracker.show_summary()

    print("\n" + "="*60)
    print("✅ 演示完成")
    print("="*60 + "\n")


if __name__ == "__main__":
    demo_dashboard()
