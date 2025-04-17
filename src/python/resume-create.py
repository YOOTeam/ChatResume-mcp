"""
Resume MCP Server
"""
import json
import os
import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# 创建MCP服务器实例
mcp = FastMCP("Chatppt Server", log_level="ERROR")
API_BASE = "https://saas.api.yoo-ai.com"
# 用户API Key
API_KEY = os.getenv('API_KEY')


def check_api_key():
    """检查 API_KEY 是否已设置"""
    if not API_KEY:
        raise ValueError("API_KEY 环境变量未设置")
    return API_KEY


@mcp.tool()
async def check():
    """查询用户当前配置token"""
    return os.getenv('API_KEY')


# 注册工具的装饰器，可以很方便的把一个函数注册为工具
# @mcp.tool()
async def build_resume(
        text: str = Field(description="生成简历query"),
        name: str = Field(description="个人简历姓名", default=''),
        mobile: str = Field(description="个人简历手机号", default=''),
        job: str = Field(description="个人工作岗位", default=''),
        school: str = Field(description="个人简历学校", default=''),
        major: str = Field(description="个人简历专业", default=''),
        work_year: str = Field(description="个人简历工作年限", default=''),
        company: str = Field(description="个人简历公司", default=''),
        gender: str = Field(description="性别", default=''),
        age: str = Field(description="个人简历年龄", default=''),
) -> str:
    """
    Name:
        生成简历工具
    Description:
        根据输入参数，生成一份简历文档;
        除了text字段必须，其他可以为空字符;
        当成功后使用默认浏览器打开简历地址并下载简历;
    Args:
        text: 生成简历query
        name: 个人简历姓名
        mobile: 个人简历手机号
        job: 个人工作岗位
        school: 个人简历学校
        major: 个人简历专业
        work_year: 个人简历工作年限
        company: 个人简历公司
        gender: 性别
        age: 个人简历年龄
    Returns:
        显示简历信息与图片，并下载简历
    """

    try:
        url = API_BASE + '/resumes/build-resume'
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={'text': text, 'name': name if name else '',
                                                    'mobile': mobile if mobile else '', 'job': job if job else '',
                                                    'school': school if school else '', 'major': major if major else '',
                                                    'work_year': work_year if work_year else '',
                                                    'company': company if company else '',
                                                    'gender': gender if gender else '', 'age': age if age else ''},
                                         headers={'Authorization': 'Bearer ' + API_KEY}, timeout=180)
            return response.json()
    except httpx.HTTPError as e:
        raise Exception(f"HTTP request failed: {str(e)}") from e


# @mcp.tool()
async def match(
        job_title: str = Field(description="岗位名称"),
        job_desc: str = Field(description="岗位描述"),
        resume_url: str = Field(description="简历URL", default='')
) -> str:
    """
    Name:
        人岗匹配工具
    Description:
        通过岗位名称、岗位描述、简历URL进行人岗匹配,返回分析ID
    Args:
        job_title：岗位名称,
        job_desc：岗位描述,
        resume_url：简历URL
    Returns:
        requestId: 分析ID
    """

    try:
        url = API_BASE + '/resumes/match'
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={'job_title': job_title, 'job_desc': job_desc,
                                                    'resume_url': resume_url},
                                         headers={'Authorization': 'Bearer ' + API_KEY}, timeout=180)
            return response.json()
    except httpx.HTTPError as e:
        raise Exception(f"HTTP request failed: {str(e)}") from e


# @mcp.tool()
async def info(
        request_id: str = Field(description="分析ID")
) -> str:
    """
    Name:
        获取简历分析报告
    Description:
        通过分析ID获取简历分析报告
    Args:
        request_id：分析ID
    Returns:
        返回分析结果
    """

    try:
        url = API_BASE + '/resumes/info'
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={'requestId': request_id},
                                         headers={'Authorization': 'Bearer ' + API_KEY}, timeout=180)
            return response.json()
    except httpx.HTTPError as e:
        raise Exception(f"HTTP request failed: {str(e)}") from e


@mcp.tool()
async def write(
        text: str = Field(description="处理的文本"),
        task: str = Field(description="['1'=>'润色'，'2'=>'扩写'，'3'=>'精炼'，'4'=>'续写'，'5'=>'短词成文']"),
        scene: str = Field(
            description='["JD", "工作经历", "自我评价", "技能特长", "校园实践", "岗位画像", "人才画像"]'),
        job: str = Field(description="岗位", default=''),
        industry: str = Field(description="行业", default=''),
        channels: str = Field(description='["社会招聘","校园招聘"]', default='社会招聘'),
        company: str = Field(description="公司名称", default=''),
) -> str:
    """
    Name:
        集成多种辅写服务（润色、扩写、精炼、续写、短词成文），结合用户指定的所属行业、岗位及具体场景，生成符合职业要求的简历内容
        具体场景示例
    Description:
        润色工作经历
        场景：用户希望将一段平淡无奇的工作经历描述变得更加生动、有说服力。
        操作：选择“润色”服务，输入所属行业（如“IT互联网”）、岗位（如“软件开发工程师”）及待润色的工作经历文本。
        结果：API返回经过润色后的工作经历描述，更加突出用户的贡献和成就。
        扩写技能特长
        场景：用户仅列出了几项技能，但希望能在简历中详细展示每项技能的应用场景和熟练程度。
        操作：选择“扩写”服务，指定行业、岗位，并输入技能列表。
        结果：API为每项技能生成详细的描述，包括使用场景、项目经验或具体成果。
    Args:
        text：处理的文本
        task：任务类型
        scene：场景
        job：岗位
        industry：行业
        channels：渠道
        company：公司名称
    Returns:
        返回辅写结果
    """

    try:
        url = API_BASE + '/resumes/write-resume'
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={'text': text, 'task': task, 'scene': scene, 'job': job,
                                                    'industry': industry, 'channels': channels, 'company': company},
                                         headers={'Authorization': 'Bearer ' + API_KEY}, timeout=180)
            return response.json()
    except httpx.HTTPError as e:
        raise Exception(f"HTTP request failed: {str(e)}") from e
