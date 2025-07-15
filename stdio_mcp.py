from fastmcp import FastMCP

# 初始化服务器
mcp = FastMCP(name="QuickMCP")

# 添加工具：加法计算
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# 添加动态资源：个性化问候
@mcp.resource("greeting://{name}")
def hello(name: str) -> str:
    """Generate a greeting"""
    return f"👋 Hello {name}! Current time: {__import__('datetime').datetime.now()}"



# 启动服务（默认 STDIO 模式）
if __name__ == "__main__":
    mcp.run()

# # # 修改启动代码
# if __name__ == "__main__":
#     app = mcp.http_app()  # 生成 ASGI 应用
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)