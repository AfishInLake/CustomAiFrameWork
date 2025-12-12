# 启动mcp服务

```shell
npx @playwright/mcp@latest --port 8931
uvx excel-mcp-server streamable-http
```

# .env配置
配置 阿里 DASHSCOPE API KEY
```shell
DASHSCOPE_API_KEY = "sk-a587535f4171437xxxxxx8fa6f3ebe6f"  
LLM_MODEL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
```

# 启动项目
```shell
uv sync
python manage.py run
```


