/**
 * Jira MCP Server
 * ===============
 * 
 * MCP (Model Context Protocol) server for Jira integration.
 * Handles Epic, Story, and Task creation via Jira REST API.
 */

const https = require('https');
const http = require('http');
const url = require('url');

class JiraMCPServer {
    constructor() {
        this.jiraBaseUrl = process.env.JIRA_BASE_URL;
        this.jiraApiToken = process.env.JIRA_API_TOKEN;
        this.jiraUsername = process.env.JIRA_USERNAME;
        
        if (!this.jiraBaseUrl || !this.jiraApiToken || !this.jiraUsername) {
            console.error('Missing required Jira environment variables');
            process.exit(1);
        }
        
        console.log('Jira MCP Server initialized');
    }
    
    async createEpic(epicData) {
        const issueData = {
            fields: {
                project: { key: 'PROJ' }, // This should be configurable
                summary: epicData.summary,
                description: epicData.description,
                issuetype: { name: 'Epic' },
                labels: epicData.labels || []
            }
        };
        
        return this.createJiraIssue(issueData);
    }
    
    async createStory(storyData) {
        const issueData = {
            fields: {
                project: { key: 'PROJ' }, // This should be configurable
                summary: storyData.summary,
                description: storyData.description,
                issuetype: { name: 'Story' },
                labels: storyData.labels || []
            }
        };
        
        if (storyData.epic_link) {
            issueData.fields.customfield_10014 = storyData.epic_link; // Epic Link field
        }
        
        return this.createJiraIssue(issueData);
    }
    
    async createTask(taskData) {
        const issueData = {
            fields: {
                project: { key: 'PROJ' }, // This should be configurable
                summary: taskData.summary,
                description: taskData.description,
                issuetype: { name: 'Task' },
                labels: taskData.labels || []
            }
        };
        
        if (taskData.parent_story) {
            issueData.fields.parent = { key: taskData.parent_story };
        }
        
        return this.createJiraIssue(issueData);
    }
    
    async createJiraIssue(issueData) {
        const options = {
            hostname: this.jiraBaseUrl,
            port: 443,
            path: '/rest/api/2/issue',
            method: 'POST',
            headers: {
                'Authorization': `Basic ${Buffer.from(`${this.jiraUsername}:${this.jiraApiToken}`).toString('base64')}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        
        return new Promise((resolve, reject) => {
            const req = https.request(options, (res) => {
                let data = '';
                
                res.on('data', (chunk) => {
                    data += chunk;
                });
                
                res.on('end', () => {
                    try {
                        const response = JSON.parse(data);
                        if (res.statusCode === 201) {
                            resolve({
                                success: true,
                                key: response.key,
                                id: response.id,
                                summary: issueData.fields.summary
                            });
                        } else {
                            resolve({
                                success: false,
                                error: response.errorMessages || response.errors || 'Unknown error'
                            });
                        }
                    } catch (error) {
                        reject(error);
                    }
                });
            });
            
            req.on('error', (error) => {
                reject(error);
            });
            
            req.write(JSON.stringify(issueData));
            req.end();
        });
    }
    
    async getIssueDetails(issueKey) {
        const options = {
            hostname: this.jiraBaseUrl,
            port: 443,
            path: `/rest/api/2/issue/${issueKey}`,
            method: 'GET',
            headers: {
                'Authorization': `Basic ${Buffer.from(`${this.jiraUsername}:${this.jiraApiToken}`).toString('base64')}`,
                'Accept': 'application/json'
            }
        };
        
        return new Promise((resolve, reject) => {
            const req = https.request(options, (res) => {
                let data = '';
                
                res.on('data', (chunk) => {
                    data += chunk;
                });
                
                res.on('end', () => {
                    try {
                        const response = JSON.parse(data);
                        if (res.statusCode === 200) {
                            resolve({
                                key: response.key,
                                status: response.fields.status.name,
                                assignee: response.fields.assignee ? response.fields.assignee.displayName : null,
                                created: response.fields.created
                            });
                        } else {
                            resolve(null);
                        }
                    } catch (error) {
                        reject(error);
                    }
                });
            });
            
            req.on('error', (error) => {
                reject(error);
            });
            
            req.end();
        });
    }
}

// MCP Protocol Handler
const server = new JiraMCPServer();

// Handle JSON-RPC 2.0 requests
process.stdin.on('data', async (data) => {
    try {
        const request = JSON.parse(data.toString());
        let response;
        
        switch (request.method) {
            case 'create_epic':
                response = await server.createEpic(request.params);
                break;
            case 'create_story':
                response = await server.createStory(request.params);
                break;
            case 'create_task':
                response = await server.createTask(request.params);
                break;
            case 'get_issue':
                response = await server.getIssueDetails(request.params.key);
                break;
            default:
                response = { error: 'Unknown method' };
        }
        
        const jsonResponse = {
            jsonrpc: '2.0',
            id: request.id,
            result: response
        };
        
        process.stdout.write(JSON.stringify(jsonResponse) + '\n');
    } catch (error) {
        const errorResponse = {
            jsonrpc: '2.0',
            id: null,
            error: {
                code: -32603,
                message: 'Internal error',
                data: error.message
            }
        };
        
        process.stdout.write(JSON.stringify(errorResponse) + '\n');
    }
});

console.log('Jira MCP Server listening for requests...');