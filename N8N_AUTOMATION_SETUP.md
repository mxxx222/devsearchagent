# n8n Automation Setup for New Topics (4h Updates)

## 🎯 Overview

This n8n workflow automates the "New Topics (4h Updates)" feature in your AI search dashboard. It runs every 4 hours to:

1. **Trigger AI topic generation**
2. **Analyze Twitter trends**
3. **Search for new topics**
4. **Send notifications** (Slack, Email)
5. **Save data to database**
6. **Log execution**

## 🚀 Quick Setup

### 1. Install n8n

```bash
# Using npm
npm install n8n -g

# Using Docker
docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n

# Using Docker Compose
curl -L https://raw.githubusercontent.com/n8n-io/n8n/master/docker/compose/docker-compose.yml -o docker-compose.yml
docker-compose up -d
```

### 2. Access n8n Interface

Open your browser and go to: `http://localhost:5678`

### 3. Import the Workflow

1. In n8n interface, click **"Import from file"**
2. Select the `n8n_automation_workflow.json` file
3. Click **"Import"**

### 4. Configure Credentials

#### Slack Webhook (Optional)
1. Go to your Slack workspace
2. Create a new webhook: https://api.slack.com/messaging/webhooks
3. Replace `YOUR/SLACK/WEBHOOK` in the workflow with your actual webhook URL

#### Email Configuration
1. Configure your email credentials in n8n
2. Update the email addresses in the "Send Email Notification" node

#### Database Connection (Optional)
1. Configure PostgreSQL credentials in n8n
2. Update the database connection in the "Save to Database" node

## 🔧 Workflow Configuration

### Main Workflow Steps

1. **Cron Trigger (4h)** - Runs every 4 hours
2. **Trigger AI Generation** - Calls your Flask API to generate new AI recommendations
3. **Analyze Twitter Trends** - Analyzes trending topics from Twitter API
4. **Trigger Topic Search** - Triggers manual topic search
5. **Check Success** - Validates that operations completed successfully
6. **Get New Topics** - Retrieves the latest AI recommendations
7. **Get Trending Topics** - Gets current trending topics
8. **Process Topics** - Formats and processes the data
9. **Send Notifications** - Sends Slack and email notifications
10. **Save to Database** - Stores the results (optional)
11. **Log Execution** - Logs the automation execution

### API Endpoints Used

- `POST /api/recommendations/trigger` - Trigger AI recommendation generation
- `GET /api/twitter/analyze` - Analyze Twitter trends
- `POST /api/scheduler/trigger` - Trigger manual topic search
- `GET /api/recommendations` - Get AI recommendations
- `GET /api/trending` - Get trending topics
- `GET /api/twitter/search` - Search Twitter tweets

## 📊 Notification Formats

### Slack Notification
```
🔄 New Topics Update (4h)

📊 Summary:
- Total Topics: 15
- AI Recommendations: 8
- Trending Topics: 7

🔥 Top Topics:
1. AI Coding Tools (AI Recommendation)
2. Python Programming (Trending)
3. Machine Learning (AI Recommendation)
4. JavaScript Frameworks (Trending)
5. Software Development (AI Recommendation)

⏰ Updated: 2025-10-23T08:20:00.000Z
```

### Email Notification
- HTML formatted email with styled content
- Statistics summary
- Top topics with visual indicators
- Timestamp and automation details

## 🔄 Customization Options

### Change Update Frequency
Edit the Cron Trigger node:
- **Every 2 hours**: `0 */2 * * *`
- **Every 6 hours**: `0 */6 * * *`
- **Daily at 9 AM**: `0 9 * * *`

### Add More Data Sources
You can add more nodes to fetch data from:
- GitHub trending repositories
- Reddit programming communities
- Hacker News
- Stack Overflow tags

### Custom Notifications
Modify the notification nodes to:
- Send to multiple Slack channels
- Add SMS notifications
- Create custom webhook calls
- Generate PDF reports

## 🛠️ Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Ensure your Flask server is running on `http://localhost:8080`
   - Check that all API endpoints are accessible
   - Verify API keys are configured correctly

2. **Authentication Issues**
   - Check Twitter API credentials in `config.env`
   - Verify OpenAI API key is set
   - Ensure all environment variables are loaded

3. **Database Connection Issues**
   - Verify PostgreSQL credentials
   - Check database table structure
   - Ensure database is accessible from n8n

### Debug Mode

Enable debug mode in n8n to see detailed execution logs:
1. Go to Settings → Workflow Settings
2. Enable "Save execution progress"
3. Check execution logs for detailed error information

## 📈 Monitoring and Analytics

### Execution History
- View execution history in n8n interface
- Check success/failure rates
- Monitor execution times

### Custom Metrics
Add custom nodes to track:
- Topic discovery rates
- API response times
- Notification delivery success
- User engagement metrics

## 🔒 Security Considerations

1. **API Keys**: Store sensitive credentials in n8n credential store
2. **Webhook Security**: Use HTTPS for webhook URLs
3. **Database Access**: Use read-only database users where possible
4. **Rate Limiting**: Be aware of API rate limits

## 🚀 Advanced Features

### Conditional Logic
Add conditional nodes to:
- Only send notifications if significant changes detected
- Skip execution during maintenance windows
- Handle different notification types based on data

### Data Processing
Enhance data processing with:
- Machine learning models for topic classification
- Sentiment analysis of trending topics
- Duplicate detection and filtering
- Topic clustering and categorization

### Integration Options
Extend the workflow with:
- Google Sheets integration for data export
- Airtable for project management
- Zapier for additional automation
- Custom API endpoints for external systems

## 📝 Maintenance

### Regular Tasks
1. **Monitor execution logs** weekly
2. **Update API credentials** as needed
3. **Review and optimize** workflow performance
4. **Backup workflow configuration** regularly

### Updates and Improvements
1. **Test changes** in a development environment first
2. **Document modifications** for team members
3. **Version control** workflow configurations
4. **Monitor for new n8n features** and integrations

## 🎉 Success Metrics

Track these metrics to measure automation success:
- **Execution Success Rate**: >95%
- **Data Freshness**: Topics updated within 4-hour windows
- **Notification Delivery**: >98% successful deliveries
- **API Response Times**: <5 seconds average
- **Topic Discovery**: New relevant topics found regularly

Your n8n automation is now ready to keep your AI search dashboard updated with fresh topics every 4 hours! 🚀
