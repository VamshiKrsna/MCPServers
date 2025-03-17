import 'dotenv/config';
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import axios from "axios";
import {
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const GITHUB_API_URL = "https://api.github.com";
const GITHUB_ACCESS_TOKEN = process.env.GITHUB_ACCESS_TOKEN;
if (!GITHUB_ACCESS_TOKEN) {
  throw new Error("GITHUB_ACCESS_TOKEN environment variable is not set.");
}

const server = new Server(
  {
    name: "github-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      resources: {}, 
    },
  }
);

server.setRequestHandler(ListResourcesRequestSchema, async () => {
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

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const uri: string = request.params.uri;
  
  if (uri === "github://user") {
    try {
      const response = await axios.get(`${GITHUB_API_URL}/user`, {
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
    } catch (error) {
      throw new Error(`Error fetching GitHub user info: ${error}`);
    }
  } else if (uri === "github://repos") {
    try {
      const response = await axios.get(`${GITHUB_API_URL}/user/repos`, {
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
    } catch (error) {
      throw new Error(`Error fetching GitHub repositories: ${error}`);
    }
  } else {
    throw new Error("Resource not found");
  }
});

const transport = new StdioServerTransport();
server.connect(transport).then(() => {
  console.info(
    '{"jsonrpc": "2.0", "method": "log", "params": { "message": "GitHub MCP Server running..." }}'
  );
}).catch((error) => {
  console.error(error);
});
