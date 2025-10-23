# 🚀 n8n Quick Start Guide

## ✅ n8n is Running!

n8n is now successfully running and accessible at: **http://localhost:5678**

## 🎯 Next Steps

### 1. Access n8n Interface
Open your browser and go to: **http://localhost:5678**

### 2. Create Your First Workflow
1. Click **"New Workflow"**
2. You'll see a blank canvas
3. Start building your automation

### 3. Import the AI Dashboard Workflow
1. Click **"Import from file"** (or use the import button)
2. Select: `n8n_automation_workflow.json`
3. Click **"Import"**

### 4. Configure the Workflow
After importing, you'll need to configure:

#### 🔧 **Cron Trigger**
- **Schedule**: `0 */4 * * *` (every 4 hours)
- **Timezone**: Your local timezone

#### 🌐 **HTTP Request Nodes**
- **AI Recommendations**: `http://localhost:8080/api/recommendations/trigger`
- **Twitter Analysis**: `http://localhost:8080/api/twitter/analyze`
- **Topic Search**: `http://localhost:8080/api/scheduler/trigger`

#### 🔑 **Credentials Setup**
Click on each HTTP node and configure:
- **Method**: POST or GET
- **URL**: The API endpoint
- **Headers**: Add if needed
- **Body**: JSON payload for POST requests

### 5. Test the Workflow
1. Click **"Execute Workflow"** button
2. Watch the execution in real-time
3. Check the results

## 📊 Workflow Features

### 🤖 **AI Recommendations**
- Triggers AI-powered topic suggestions
- Uses OpenAI and Gemini APIs
- Generates coding and software development topics

### 🐦 **Twitter Analysis**
- Analyzes trending topics on Twitter
- Searches for AI coding and software development content
- Tracks engagement metrics

### 🔍 **Topic Search**
- Performs automated searches
- Tracks trending topics
- Updates the dashboard

### 📈 **Data Processing**
- Processes and analyzes results
- Stores data in database
- Generates insights

### 📧 **Notifications**
- Slack notifications (if configured)
- Email alerts (if configured)
- Success/failure notifications

## 🔧 Configuration Tips

### 1. **API Endpoints**
Make sure your Flask app is running on port 8080:
```bash
npm start  # or python app.py
```

### 2. **Database**
The workflow will automatically save results to your SQLite database.

### 3. **Error Handling**
- Each node has error handling
- Failed executions are logged
- Retry logic is built-in

### 4. **Scheduling**
- Default: Every 4 hours
- Customizable cron expressions
- Timezone aware

## 🧪 Testing

### Manual Test
1. Click **"Execute Workflow"**
2. Check each node's output
3. Verify data is saved

### Scheduled Test
1. Set a test schedule (e.g., every minute)
2. Wait for automatic execution
3. Check results

## 🔍 Monitoring

### Execution History
- View all past executions
- Check success/failure rates
- Debug failed runs

### Logs
- Detailed execution logs
- Error messages
- Performance metrics

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Refused**
   - Make sure Flask app is running
   - Check port 8080 is available

2. **API Errors**
   - Verify API endpoints are correct
   - Check authentication if needed

3. **Database Errors**
   - Ensure database is accessible
   - Check permissions

### Debug Steps
1. Check n8n execution logs
2. Verify Flask app logs
3. Test API endpoints manually
4. Check database connectivity

## 📚 Resources

- **n8n Documentation**: https://docs.n8n.io/
- **Cron Expressions**: https://crontab.guru/
- **HTTP Request Node**: https://docs.n8n.io/integrations/builtin/cluster-nodes/n8n-nodes-base.httprequest/

## 🎉 Ready to Go!

Your n8n automation is now ready! The workflow will:
- ✅ Run every 4 hours automatically
- ✅ Generate AI recommendations
- ✅ Analyze Twitter trends
- ✅ Update your dashboard
- ✅ Send notifications

**Happy Automating!** 🚀
