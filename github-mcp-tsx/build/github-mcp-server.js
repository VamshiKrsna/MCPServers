"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
require("dotenv/config");
const index_js_1 = require("@modelcontextprotocol/sdk/server/index.js");
const stdio_js_1 = require("@modelcontextprotocol/sdk/server/stdio.js");
const axios_1 = __importDefault(require("axios"));
const types_js_1 = require("@modelcontextprotocol/sdk/types.js");
const GITHUB_API_URL = "https://api.github.com";
const GITHUB_ACCESS_TOKEN = process.env.GITHUB_ACCESS_TOKEN;
if (!GITHUB_ACCESS_TOKEN) {
    throw new Error("GITHUB_ACCESS_TOKEN environment variable is not set.");
}
const server = new index_js_1.Server({
    name: "github-mcp-server",
    version: "1.0.0",
}, {
    capabilities: {
        resources: {},
    },
});
server.setRequestHandler(types_js_1.ListResourcesRequestSchema, async () => {
    return {
        resources: [
            {
                uri: "github://user",
                name: "GitHub User Info",
                description: "Your GitHub profile information",
                mimeType: "application/json",
            },
            {
                uri: "github://repos",
                name: "GitHub Repositories",
                description: "List of your GitHub repositories",
                mimeType: "application/json",
            },
        ],
    };
});
server.setRequestHandler(types_js_1.ReadResourceRequestSchema, async (request) => {
    const uri = request.params.uri;
    if (uri === "github://user") {
        try {
            const response = await axios_1.default.get(`${GITHUB_API_URL}/user`, {
                headers: {
                    Authorization: `token ${GITHUB_ACCESS_TOKEN}`,
                },
            });
            return {
                contents: [
                    {
                        uri: "github://user",
                        text: JSON.stringify(response.data, null, 2),
                    },
                ],
            };
        }
        catch (error) {
            throw new Error(`Error fetching GitHub user info: ${error}`);
        }
    }
    else if (uri === "github://repos") {
        try {
            const response = await axios_1.default.get(`${GITHUB_API_URL}/user/repos`, {
                headers: {
                    Authorization: `token ${GITHUB_ACCESS_TOKEN}`,
                },
            });
            return {
                contents: [
                    {
                        uri: "github://repos",
                        text: JSON.stringify(response.data, null, 2),
                    },
                ],
            };
        }
        catch (error) {
            throw new Error(`Error fetching GitHub repositories: ${error}`);
        }
    }
    else {
        throw new Error("Resource not found");
    }
});
const transport = new stdio_js_1.StdioServerTransport();
server.connect(transport).then(() => {
    console.info('{"jsonrpc": "2.0", "method": "log", "params": { "message": "GitHub MCP Server running..." }}');
}).catch((error) => {
    console.error(error);
});
