from fastmcp import FastMCP
import functools
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# 初始化SSE模式服务器
mcp = FastMCP(name="mcp-server-math-tools")

def log_io(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] 调用 {func.__name__} 输入: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} 输出: {result}")
        return result
    return wrapper

# 保留原有工具和资源
@mcp.tool
@log_io
def aggregate_calculate(numbers: list[float], op: str) -> float:
    """
    聚合数学分析工具
    numbers: 数值列表
    op: 支持 'mean', 'max', 'min', 'var', 'stdev', 'median', 'mode', 'range', 'q1', 'q3', 'skew', 'kurtosis'
    """
    import statistics
    import math
    if not numbers:
        raise ValueError('输入列表不能为空')
    if op == 'mean':
        return statistics.mean(numbers)
    elif op == 'max':
        return max(numbers)
    elif op == 'min':
        return min(numbers)
    elif op == 'var':
        return statistics.variance(numbers) if len(numbers) > 1 else 0.0
    elif op == 'stdev':
        return statistics.stdev(numbers) if len(numbers) > 1 else 0.0
    elif op == 'median':
        return statistics.median(numbers)
    elif op == 'mode':
        try:
            return statistics.mode(numbers)
        except statistics.StatisticsError:
            raise ValueError('没有唯一众数')
    elif op == 'range':
        return max(numbers) - min(numbers)
    elif op == 'q1':
        sorted_nums = sorted(numbers)
        n = len(sorted_nums)
        mid = n // 2
        lower_half = sorted_nums[:mid]
        return statistics.median(lower_half)
    elif op == 'q3':
        sorted_nums = sorted(numbers)
        n = len(sorted_nums)
        mid = n // 2
        if n % 2 == 0:
            upper_half = sorted_nums[mid:]
        else:
            upper_half = sorted_nums[mid+1:]
        return statistics.median(upper_half)
    elif op == 'skew':
        mean = statistics.mean(numbers)
        stdev = statistics.stdev(numbers) if len(numbers) > 1 else 0.0
        n = len(numbers)
        if stdev == 0 or n < 3:
            return 0.0
        skew = sum((x - mean) ** 3 for x in numbers) / n / (stdev ** 3)
        return skew
    elif op == 'kurtosis':
        mean = statistics.mean(numbers)
        stdev = statistics.stdev(numbers) if len(numbers) > 1 else 0.0
        n = len(numbers)
        if stdev == 0 or n < 4:
            return 0.0
        kurt = sum((x - mean) ** 4 for x in numbers) / n / (stdev ** 4) - 3
        return kurt
    else:
        raise ValueError(f'不支持的聚合运算类型: {op}')

@mcp.tool
@log_io
def math_eval(expr: str) -> float:
    """
    通用数学表达式求值工具。
    
    功能：
    - 支持解析和计算任意复杂的数学表达式字符串。
    - 可进行多层嵌套、组合运算，如 'sin(pi/2) + log(10) * sqrt(16) / pow(2, 3)'。
    - 可替代所有基础数学函数工具（如加减乘除、三角、对数、指数、开方、幂等）。
    
    注意事项：
    - 仅支持单个表达式的求值，不支持对数值列表的统计分析（如均值、方差等）。如需统计分析请使用 aggregate_calculate 工具。
    - 表达式中的函数和常量名称需与 math 模块一致（如 log, sqrt, pow, pi, e 等）。
    
    示例：
    math_eval("sin(pi/2) + log(10) * sqrt(16) / pow(2, 3)")
    math_eval("abs(-5) + exp(1)")
    """
    from simpleeval import SimpleEval
    import math
    functions = {}
    names = {}
    for k in dir(math):
        if not k.startswith('_'):
            attr = getattr(math, k)
            if callable(attr):
                functions[k] = attr
            else:
                names[k] = attr
    s = SimpleEval(functions=functions, names=names)
    return s.eval(expr)

@mcp.resource("greeting://{name}")
def hello(name: str) -> str:
    """动态问候资源"""
    return f"👋 你好{name}! 当前时间: {__import__('datetime').datetime.now()}"


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

# 配置SSE模式并指定端口
if __name__ == "__main__":
    mcp.run(
        transport="sse",
        port=9000  # SSE模式端口
    )