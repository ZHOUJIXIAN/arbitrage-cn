"""
Windows 开机自启配置
通过任务计划程序设置套利框架自动运行
"""
import os
import subprocess
from datetime import datetime, timedelta


def create_startup_task(
    task_name: str = "ArbitrageFramework",
    script_path: str = r"C:\Users\H\Desktop\arbitrage_cn\main.py",
    python_path: str = r"C:\Users\H\Desktop\venv\Scripts\python.exe",
    log_path: str = r"C:\Users\H\Desktop\arbitrage_cn\logs\startup.log"
):
    """
    创建开机自启任务

    Args:
        task_name: 任务名称
        script_path: 主程序路径
        python_path: Python 可执行文件路径
        log_path: 日志路径

    Returns:
        bool: 是否成功
    """

    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # 任务命令
    command = f'"{python_path}" "{script_path}" --strategy all --broker sim'

    # schtasks 命令（创建开机启动任务）
    schtasks_cmd = [
        "schtasks",
        "/create",
        f"/tn", task_name,
        f"/tr", python_path,
        f"/sc", "onstart",
        f"/delay", "0000:30",  # 启动后延迟 30 秒
        "/rl", "highest",  # 最高优先级
        "/f"  # 如果任务已存在则覆盖
    ]

    # 添加任务参数
    schtasks_cmd.extend([
        f"/c", f'sch /Run /User /Create /TN {task_name} /TR {python_path} /SC onstart /Delay 0000:30 /RL Highest /F'
    ])

    print("=" * 50)
    print("Windows 开机自启配置")
    print("=" * 50)
    print(f"\n任务名称: {task_name}")
    print(f"程序路径: {script_path}")
    print(f"Python: {python_path}")
    print(f"日志路径: {log_path}")
    print(f"\n启动延迟: 30 秒（确保网络和服务启动）")
    print(f"优先级: 最高")

    try:
        print(f"\n正在创建任务...")
        print(f"命令: {' '.join(schtasks_cmd[:8])}")

        # 删除旧任务（如果存在）
        print("\n[步骤 1] 删除旧任务...")
        subprocess.run(
            ["schtasks", "/delete", f"/tn", task_name, "/f"],
            check=False,
            shell=True
        )

        # 创建新任务
        print("[步骤 2] 创建新任务...")
        # 使用 XML 方式创建更灵活的任务
        task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}</Date>
    <Author>H</Author>
    <Description>A股套利框架 - 自动运行 LOF 套利和可转债打新</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT30S</Delay>  <!-- 启动延迟 30 秒 -->
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>H</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>"{script_path}" --strategy all --broker sim</Arguments>
      <WorkingDirectory>C:\Users\H\Desktop\arbitrage_cn</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

        # 保存 XML 文件
        xml_path = r"C:\Users\H\Desktop\startup_task.xml"
        with open(xml_path, "w", encoding="utf-16") as f:
            f.write(task_xml)

        print(f"  任务 XML 已保存: {xml_path}")

        # 导入任务
        print(f"\n[步骤 3] 导入任务...")
        result = subprocess.run(
            ["schtasks", "/create", "/tn", task_name, "/xml", xml_path, "/f"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            print(f"  ✅ 任务创建成功")

            # 验证任务
            print(f"\n[步骤 4] 验证任务...")
            verify_result = subprocess.run(
                ["schtasks", "/query", f"/tn", task_name, "/fo", "list"],
                capture_output=True,
                text=True,
                shell=True
            )

            print(f"  任务信息:\n{verify_result.stdout}")

            # 清理 XML 文件
            os.remove(xml_path)
            print(f"\n  ✅ 清理临时文件")

            return True
        else:
            print(f"  ❌ 任务创建失败")
            print(f"  错误: {result.stderr}")
            return False

    except Exception as e:
        print(f"\n❌ 创建任务时出错: {e}")
        return False


def check_existing_task(task_name: str = "ArbitrageFramework"):
    """检查现有任务"""
    print(f"\n检查现有任务: {task_name}")

    try:
        result = subprocess.run(
            ["schtasks", "/query", f"/tn", task_name, "/fo", "list"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            print(f"  ✅ 任务已存在")
            print(f"  状态: {result.stdout.strip()}")
            return True
        else:
            print(f"  ℹ️  任务不存在")
            return False

    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False


def delete_task(task_name: str = "ArbitrageFramework"):
    """删除任务"""
    print(f"\n删除任务: {task_name}")

    try:
        result = subprocess.run(
            ["schtasks", "/delete", f"/tn", task_name, "/f"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            print(f"  ✅ 任务已删除")
            return True
        else:
            print(f"  ❌ 删除失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"  ❌ 删除出错: {e}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        action = sys.argv[1].lower()

        if action == "check":
            check_existing_task()
        elif action == "delete":
            delete_task()
        elif action == "create":
            create_startup_task()
        else:
            print("用法:")
            print("  python startup.py create   # 创建开机自启任务")
            print("  python startup.py check    # 检查现有任务")
            print("  python startup.py delete   # 删除任务")
    else:
        # 默认：检查并创建
        print("\n[1] 检查现有任务...")
        check_existing_task()

        print("\n[2] 创建开机自启任务...")
        success = create_startup_task()

        if success:
            print("\n" + "=" * 50)
            print("✅ 开机自启配置完成")
            print("=" * 50)
            print("\n说明:")
            print("- 电脑开机后 30 秒自动启动套利框架")
            print("- 任务会在用户登录后运行")
            print("- 日志保存到: C:\\Users\\H\\Desktop\\arbitrage_cn\\logs\\startup.log")
            print("\n管理命令:")
            print("- 手动运行: C:\\Users\\H\\Desktop\\venv\\Scripts\\python.exe C:\\Users\\H\\Desktop\\arbitrage_cn\\main.py --strategy all")
            print("- 检查任务: schtasks /query /tn ArbitrageFramework")
            print("- 删除任务: python startup.py delete")
        else:
            print("\n❌ 配置失败")
