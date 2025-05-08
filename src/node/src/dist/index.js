#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema, } from "@modelcontextprotocol/sdk/types.js";
import fetch from "node-fetch";
function getApiKey() {
    const apiKey = process.env.API_KEY;
    if (!apiKey) {
        console.error("API_KEY environment variable is not set");
        process.exit(1);
    }
    return "Bearer " + apiKey;
}
const API_KEY = getApiKey();
const API_URL = "https://saas.api.yoo-ai.com";
// Tool definitions
const Create_TOOL = {
    name: "create_resume",
    description: "根据输入参数，生成一份简历文档，除了text字段必须，其他可以为空字符，当成功后使用默认浏览器打开简历地址并下载简历",
    inputSchema: {
        type: "object",
        properties: {
            text: {
                type: "string",
                description: "生成简历query"
            },
            name: {
                type: "string",
                description: "个人简历姓名"
            },
            mobile: {
                type: "string",
                description: "个人简历手机号"
            },
            job: {
                type: "string",
                description: "个人工作岗位"
            },
            school: {
                type: "string",
                description: "个人简历学校"
            },
            major: {
                type: "string",
                description: "个人简历专业"
            },
            work_year: {
                type: "string",
                description: "个人简历工作年限"
            },
            company: {
                type: "string",
                description: "个人简历公司"
            },
            gender: {
                type: "string",
                description: "性别"
            },
            age: {
                type: "string",
                description: "个人简历年龄"
            }
        },
        required: ["text"]
    }
};
const Match_TOOL = {
    name: "match_resume",
    description: "通过岗位名称、岗位描述、简历URL进行人岗匹配,返回分析ID",
    inputSchema: {
        type: "object",
        properties: {
            job_title: {
                type: "string",
                description: "岗位名称"
            },
            job_desc: {
                type: "string",
                description: "岗位描述"
            },
            resume_url: {
                type: "string",
                description: "简历URL"
            }
        },
        required: ["job_title", "job_desc"]
    }
};
const Info_TOOL = {
    name: "info",
    description: "通过分析ID获取简历分析报告",
    inputSchema: {
        type: "object",
        properties: {
            requestId: {
                type: "string",
                description: "分析ID"
            }
        },
        required: ["requestId"]
    }
};
async function handleResumeBuild(text, mobile, name, job, school, major, work_year, company, gender, age) {
    const url = new URL(API_URL + "/mcp/resumes/build-resume");
    let params = JSON.stringify({
        "text": text,
        "mobile": mobile,
        "name": name,
        "job": job,
        "school": school,
        "major": major,
        "work_year": work_year,
        "company": company,
        "gender": gender,
        "age": age
    });
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": API_KEY
        },
        body: params,
    });
    const data = await response.json();
    if (data.code !== 200) {
        return {
            content: [{
                    type: "text",
                    text: `Build failed: ${data.code} : ${data.msg}`,
                }],
            isError: true
        };
    }
    return {
        content: [{
                type: "text",
                text: JSON.stringify({
                    document: data.data.document,
                }, null, 2)
            }],
        isError: false
    };
}
async function handleResumeMatch(job_title, job_desc, resume_url) {
    const url = new URL(API_URL + "/mcp/resumes/match");
    let params = JSON.stringify({
        "job_title": job_title,
        "job_desc": job_desc,
        "resume_url": resume_url
    });
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": API_KEY
        },
        body: params,
    });
    const data = await response.json();
    if (data.code !== 200) {
        return {
            content: [{
                    type: "text",
                    text: `Build failed: ${data.code} : ${data.msg}`,
                }],
            isError: true
        };
    }
    return {
        content: [{
                type: "text",
                text: JSON.stringify({
                    document: data.data.id,
                }, null, 2)
            }],
        isError: false
    };
}
async function handleInfo(RequestId) {
    const url = new URL(API_URL + "/mcp/resumes/info");
    let params = JSON.stringify({
        "RequestId": RequestId,
    });
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": API_KEY
        },
        body: params,
    });
    const data = await response.json();
    if (data.code !== 200) {
        return {
            content: [{
                    type: "text",
                    text: `Build failed: ${data.code} : ${data.msg}`,
                }],
            isError: true
        };
    }
    return {
        content: [{
                type: "text",
                text: JSON.stringify({
                    document: data.data,
                }, null, 2)
            }],
        isError: false
    };
}
// Create an MCP server
const server = new Server({
    name: "mcp-server/resume",
    version: "1.0.0",
}, {
    capabilities: {
        tools: {},
    },
});
const MAPS_TOOLS = [
    Create_TOOL,
    Match_TOOL,
    Info_TOOL
];
// Set up request handlers
server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: MAPS_TOOLS,
}));
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    try {
        switch (request.params.name) {
            case "create_resume": {
                const { text } = request.params.arguments;
                const { mobile } = request.params.arguments;
                const { name } = request.params.arguments;
                const { job } = request.params.arguments;
                const { school } = request.params.arguments;
                const { major } = request.params.arguments;
                const { work_year } = request.params.arguments;
                const { company } = request.params.arguments;
                const { gender } = request.params.arguments;
                const { age } = request.params.arguments;
                return await handleResumeBuild(text, mobile, name, job, school, major, work_year, company, gender, age);
            }
            case 'match_resume': {
                const { job_title } = request.params.arguments;
                const { job_desc } = request.params.arguments;
                const { resume_url } = request.params.arguments;
                return await handleResumeMatch(job_title, job_desc, resume_url);
            }
            case 'info': {
                const { requestId } = request.params.arguments;
                return await handleInfo(requestId);
            }
            default:
                return {
                    content: [{
                            type: "text",
                            text: `Unknown tool: ${request.params.name}`
                        }],
                    isError: true
                };
        }
    }
    catch (error) {
        return {
            content: [{
                    type: "text",
                    text: `Error: ${error instanceof Error ? error.message : String(error)}`
                }],
            isError: true
        };
    }
});
async function runServer() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("MCP Server running on stdio");
}
runServer().catch((error) => {
    console.error("Fatal error running server:", error);
    process.exit(1);
});
