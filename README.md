# NewNetLoginer

适用于新验证系统的上海科技大学网络自动验证登录器。

## 安装依赖

使用 `pdm`：

```bash
pdm install
```

或者使用传统方式：

```bash
python -m venv venv
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

## 使用

复制 `.env` 并编辑：

```bash
cp .env.example .env
vim .env
```

运行：

```bash
python src/__init__.py
```
