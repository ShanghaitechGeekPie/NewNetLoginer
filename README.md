# NewNetLoginer

适用于新验证系统的上海科技大学网络自动验证登录器。

## 使用

建议使用 `venv`：

```bash
python -m venv venv
source venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

创建 `config.json` 并编辑：

```bash
cp config.json.example config.json
vim config.json
```

授予执行权限并运行：

```bash
chmod +x net_loginer.py
./net_loginer.py
```
