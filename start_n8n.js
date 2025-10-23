#!/usr/bin/env node
/**
 * Start n8n with custom configuration for AI Search Dashboard
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Starting n8n for AI Search Dashboard...');
console.log('==========================================');

// Set environment variables for n8n
process.env.N8N_HOST = 'localhost';
process.env.N8N_PORT = '5678';
process.env.N8N_PROTOCOL = 'http';
process.env.N8N_EDITOR_BASE_URL = 'http://localhost:5678';

// Start n8n
const n8n = spawn('n8n', ['start'], {
  stdio: 'inherit',
  shell: true
});

n8n.on('error', (err) => {
  console.error('❌ Error starting n8n:', err);
  process.exit(1);
});

n8n.on('close', (code) => {
  console.log(`n8n process exited with code ${code}`);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down n8n...');
  n8n.kill('SIGINT');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Shutting down n8n...');
  n8n.kill('SIGTERM');
  process.exit(0);
});

console.log('✅ n8n started successfully!');
console.log('🌐 Access n8n at: http://localhost:5678');
console.log('📋 Import the workflow: n8n_automation_workflow.json');
console.log('🛑 Press Ctrl+C to stop n8n');
