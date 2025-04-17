"""
Resume MCP Server
"""
import json
import os
import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# 创建MCP服务器实例
mcp = FastMCP("Resume Server", log_level="ERROR")
API_BASE = "https://saas.api.yoo-ai.com"
# 用户API Key
API_KEY = os.getenv('API_KEY')


def check_api_key():
    """检查 API_KEY 是否已设置"""
    if not API_KEY:
        raise ValueError("API_KEY 环境变量未设置")
    return API_KEY


@mcp.tool()
async def recognize(
        file: str = Field(description="上传的文件路径")
) -> str:
    """
    Name:
        简历解析工具
    Description:
        步骤：
        1.简历解析工具分析简历数据内容。
        2.通过analyse_data使简历内容根据JD分析处理优化。
        3.通过优化后内容结构生成简历
    Args:
        file：上传的文件路径
    Returns:
        返回解析结果
    """
    try:
        with open(file, 'rb') as fp:
            files = {'file': (os.path.basename(file), fp, 'application/octet-stream')}

            url = API_BASE + '/resumes/cv-recognize'
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    files=files,
                    headers={'Authorization': 'Bearer ' + API_KEY},
                    timeout=180
                )
                response = response.json()

                if response['code'] != 200:
                    return response['msg']

                return response['data']['tagInfo']
    except httpx.HTTPError as e:
        raise Exception(f"HTTP request failed: {str(e)}") from e
    except json.JSONDecodeError:
        raise Exception("Error: Failed to decode JSON")


@mcp.tool()
async def analyse_data(
        recognize_data=Field(description="简历识别内容"),
        jd: str = Field(description="JD内容")
) -> str:
    """
    Name:
        简历内容根据JD分析处理
    Description:
        根据识别简历结构和用户输入的JD信息重新整理美化
    Args:
        recognize_data：分析的数据
        jd：JD内容
    Returns:
        返回解析结果
    """
    url = API_BASE + '/resumes/jd-analyse'
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            data={
                'data': recognize_data,
                'jd': jd
            },
            headers={'Authorization': 'Bearer ' + API_KEY},
            timeout=60
        )
        response = response.json()

        if response['code'] != 200:
            return response['msg']

        return response['data']


@mcp.tool()
async def resume_style_write(
        color: str = Field(description="颜色：红色、橙色、黄色、绿色、青色、蓝色、紫色、粉色、黑色、白色、灰色"),
        modules: dict = Field(description="简历解析的结构")
) -> str:
    """
    Name:
        通过输入参数生成简历
    Description:
        根据简历结构重新生成简历
    Args:
        color：颜色：红色、橙色、黄色、绿色、青色、蓝色、紫色、粉色、黑色、白色、灰色,
        modules:简历解析的结构
    Returns:
        url:简历地址
        :param modules:
        :param color:
    """
    try:
        url = API_BASE + '/resumes/resume-style'
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    'color': color,
                    'modules': json.dumps(modules)
                },
                headers={'Authorization': 'Bearer ' + API_KEY},
                timeout=60
            )
            response = response.json()

            if response['code'] != 200:
                return response['msg']

            return response['data']['url']
    except httpx.HTTPError as e:
        raise Exception(f"HTTP request failed: {str(e)}") from e
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON")

if __name__ == "__main__":
    mcp.run()
