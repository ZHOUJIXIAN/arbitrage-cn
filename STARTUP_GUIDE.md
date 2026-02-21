# Windows 开机自启配置指南

## 快速配置（推荐）

### 步骤 1: 在 1号工作站创建批处理文件

创建文件：`C:\Users\H\Desktop\arbitrage_cn\startup.bat`

内容：
```batch
@echo off
echo Starting A-Share Arbitrage Framework...

cd /d "C:\Users\H\Desktop\arbitrage_cn"
"C:\Users\H\Desktop\venv\Scripts\python.exe" main.py --strategy all --broker sim

pause
```

### 步骤 2: 创建任务计划

打开 **任务计划程序**：
- Win + R → 输入 `taskschd.msc` → 回车

**创建任务**：
1. **操作** → **创建基本任务**
2. **名称**: `ArbitrageFramework`
3. **触发器**：
   - 选择 **"启动时"**
   - 勾选 **"延迟任务"**
   - 设置延迟：**30 秒**
4. **操作**：
   - **启动程序**: `C:\Users\H\Desktop\arbitrage_cn\startup.bat`
   - **起于**: `C:\Users\H\Desktop\arbitrage_cn`
5. **条件**：
   - 只在计算机使用交流电源时启动此任务
   - 不管用户是否登录都要运行
6. **设置**：
   - 勾选 **"按需运行任务"**
   - 不勾选 **"如果任务运行时间超过则停止任务"**

### 步骤 3: 测试

手动运行：
```powershell
C:\Users\H\Desktop\arbitrage_cn\startup.bat
```

### 步骤 4: 重启验证

重启电脑，检查：
- 任务是否自动运行
- 日志文件是否更新：`C:\Users\H\Desktop\arbitrage_cn\logs\`

---

## 高级配置

### 使用 schtasks 命令

```powershell
# 创建任务
schtasks /create /tn ArbitrageFramework ^
  /tr C:\Users\H\Desktop\arbitrage_cn\startup.bat ^
  /sc onstart /delay 0000:30 ^
  /rl highest /f

# 查看任务
schtasks /query /tn ArbitrageFramework

# 删除任务
schtasks /delete /tn ArbitrageFramework /f

# 运行任务
schtasks /run /tn ArbitrageFramework
```

### 注册表方式（不推荐）

```powershell
# 添加到启动项（仅当前用户）
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" ^
  /v ArbitrageFramework /t REG_SZ ^
  /d "C:\Users\H\Desktop\arbitrage_cn\startup.bat" /f
```

---

## 常见问题

### Q: 任务没有运行

**可能原因**:
1. 延迟时间不够
2. 路径错误
3. Python 环境问题

**解决方法**:
- 增加延迟到 60 秒
- 检查文件路径是否正确
- 手动运行 startup.bat 测试

### Q: 如何查看任务历史

```powershell
schtasks /query /tn ArbitrageFramework /fo LIST /v
```

### Q: 如何启用日志

修改 `startup.bat`，添加日志重定向：

```batch
@echo off
cd /d "C:\Users\H\Desktop\arbitrage_cn"
"C:\Users\H\Desktop\venv\Scripts\python.exe" main.py --strategy all --broker sim >> logs\startup.log 2>&1
```

---

## 验证清单

- [ ] startup.bat 文件已创建
- [ ] 手动运行 startup.bat 成功
- [ ] 任务计划程序已创建任务
- [ ] 延迟时间设置为 30 秒
- [ ] 重启电脑，任务自动运行
- [ ] 日志文件正常生成
