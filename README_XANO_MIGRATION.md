# MongoDB to Xano Migration Guide

This guide explains how to migrate your AI Prompt Sender application from MongoDB to Xano for database storage.

## Overview

The AI Prompt Sender now supports both MongoDB and Xano as database backends. You can switch between them using environment configuration, and we provide tools to migrate your existing data from MongoDB to Xano.

## Prerequisites

1. **Xano Account**: You need a Xano workspace with API access
2. **API Token**: Generate an API token in your Xano workspace
3. **Database Schema**: Set up the appropriate tables in Xano (see Schema Setup section)

## Xano Schema Setup

In your Xano workspace, you'll need to create a database table and API endpoints. Follow these steps:

### 1. Create the Conversations Table

In your Xano workspace, create a new table called `conversations` with the following fields:

| Field Name | Field Type | Settings | Description |
|------------|------------|----------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Xano auto-generated ID |
| `conversation_id` | Text | Unique | Unique conversation identifier |
| `system_prompt` | Text | Optional | System prompt content |
| `messages` | JSON | Required | Array of prompt messages |
| `responses` | JSON | Required | Array of AI responses |
| `metadata` | JSON | Optional | Additional metadata |
| `created_at` | Timestamp | Auto-set on create | Creation timestamp |
| `updated_at` | Timestamp | Auto-set on update | Last update timestamp |

### 2. Create Required API Endpoints

Create the following basic CRUD API endpoints in Xano's Function Stack:

#### Required Endpoints:

1. **POST /conversations** - Create new conversation
   - Input: JSON body with conversation data
   - Function: Add Record to conversations table

2. **GET /conversations/{conversation_id}** - Get conversation by ID
   - Input: conversation_id as path parameter
   - Function: Get Record from conversations table where conversation_id matches

3. **GET /conversations** - List conversations with pagination
   - Input: `limit` (integer, default: 100) and `offset` (integer, default: 0) as query parameters
   - Function: Query All Records with pagination

4. **PUT /conversations/{conversation_id}** - Update conversation
   - Input: conversation_id as path parameter + JSON body
   - Function: Edit Record in conversations table

5. **DELETE /conversations/{conversation_id}** - Delete conversation
   - Input: conversation_id as path parameter
   - Function: Delete Record from conversations table

### 3. Example API Function Setup

Here's how to set up the basic endpoints:

#### GET /conversations/{conversation_id}
1. Add input parameter: `conversation_id` (Text, from URL path)
2. Add "Get Record" function
3. Set table to "conversations" 
4. Set filter: `conversation_id` equals `{conversation_id}`
5. Return the record

#### POST /conversations
1. Add input parameters for all fields (conversation_id, system_prompt, messages, responses, metadata)
2. Add "Add Record" function
3. Set table to "conversations"
4. Map input fields to table fields
5. Return the created record

#### GET /conversations (with pagination)
1. Add input parameters: `limit` (Integer, default: 100), `offset` (Integer, default: 0)
2. Add "Query All Records" function
3. Set table to "conversations"
4. Enable pagination with limit and offset
5. Sort by created_at descending
6. Return the records

#### PUT /conversations/{conversation_id}
1. Add input parameter: `conversation_id` (Text, from URL path)
2. Add input parameters for all updatable fields
3. Add "Edit Record" function
4. Set table to "conversations"
5. Set filter: `conversation_id` equals `{conversation_id}`
6. Map input fields to table fields
7. Return the updated record

#### DELETE /conversations/{conversation_id}
1. Add input parameter: `conversation_id` (Text, from URL path)
2. Add "Delete Record" function
3. Set table to "conversations"
4. Set filter: `conversation_id` equals `{conversation_id}`
5. Return success response

## Configuration

### Environment Variables

Copy `env_example.txt` to `.env` and configure the following variables:

```bash
# Database Provider Selection
DATABASE_PROVIDER=xano  # Change from "mongodb" to "xano"

# Xano Configuration
XANO_BASE_URL=https://your-workspace.xano.com/api:v1
# XANO_API_TOKEN=your_api_token_here  # Optional - only needed for private endpoints
XANO_TIMEOUT=30.0
```

### API Token Setup (Optional)

**For Public Endpoints**: No API token is required. Your endpoints will be accessible without authentication.

**For Private Endpoints** (if you want to secure your API):
1. Log into your Xano workspace
2. Go to Settings → API Tokens
3. Create a new API token with appropriate permissions
4. Uncomment and set the token in your `.env` file:
   ```bash
   XANO_API_TOKEN=your_api_token_here
   ```

### Endpoint Configuration

When setting up your Xano endpoints, you have two options:

**Option 1: Public Endpoints (Recommended for testing)**
- No authentication required
- Endpoints are accessible by anyone with the URL
- Simpler setup, no token management

**Option 2: Private Endpoints (Recommended for production)**
- Requires API token authentication
- More secure for production use
- Set the endpoint to "Auth Required" in Xano

## Migration Process

### Step 1: Test Connection

First, verify that your Xano configuration is working:

```bash
python ai_prompt_sender.py
```

The application will show which database provider is configured and connection status.

### Step 2: Dry Run Migration

Test the migration without actually transferring data:

```bash
python -m database.migration_utility --dry-run
```

This will:
- Connect to both MongoDB and Xano
- Analyze your MongoDB data
- Show what would be migrated
- Report any potential issues

### Step 3: Actual Migration

Run the real migration:

```bash
python -m database.migration_utility --batch-size 50
```

Options:
- `--batch-size`: Number of conversations to process at once (default: 100)
- `--dry-run`: Simulate migration without transferring data
- `--verify-only`: Only verify existing migration
- `--verify-sample-size`: Number of conversations to verify (default: 10)

### Step 4: Verification

Verify the migration was successful:

```bash
python -m database.migration_utility --verify-only --verify-sample-size 20
```

### Step 5: Switch to Xano

Update your `.env` file:

```bash
DATABASE_PROVIDER=xano
```

Now your application will use Xano instead of MongoDB.

## Data Migration Details

### What Gets Migrated

- All conversation records
- System prompts
- User messages and AI responses
- Response metadata (tokens used, response times, errors)
- Conversation metadata
- Timestamps (preserved as closely as possible)

### Data Transformation

The migration handles the following transformations:

1. **ObjectId to String**: MongoDB ObjectIds are not transferred (Xano uses auto-increment IDs)
2. **Timestamps**: MongoDB timestamps are converted to ISO format for Xano
3. **JSON Fields**: Complex fields (messages, responses, metadata) are serialized as JSON
4. **Response Times**: Converted from milliseconds to seconds where applicable

### Duplicate Handling

The migration utility:
- Checks for existing conversations in Xano before migrating
- Skips conversations that already exist (based on `conversation_id`)
- Reports skipped conversations

## Troubleshooting

### Common Issues

#### 1. Connection Errors

**Error**: `Failed to connect to Xano`

**Solutions**:
- Verify `XANO_BASE_URL` is correct
- Check that your API token has proper permissions
- Ensure your Xano workspace is active
- Test the URL manually in a browser or Postman

#### 2. API Endpoint Not Found

**Error**: `404 Not Found`

**Solutions**:
- Verify all required API endpoints are created in Xano
- Check endpoint URLs match the expected format
- Ensure endpoints are published and not in draft mode

#### 3. Authentication Errors

**Error**: `401 Unauthorized`

**Solutions**:
- Regenerate your API token
- Check token permissions in Xano
- Verify the token is correctly set in `.env`

#### 4. Migration Failures

**Error**: Various migration errors

**Solutions**:
- Run with `--dry-run` first to identify issues
- Reduce `--batch-size` for large datasets
- Check Xano API rate limits
- Verify your Xano database schema matches requirements

#### 5. Performance Issues

**Symptoms**: Slow migration or timeouts

**Solutions**:
- Increase `XANO_TIMEOUT` in environment
- Reduce batch size: `--batch-size 25`
- Check your Xano plan's API rate limits
- Monitor Xano workspace performance

### Debugging

Enable detailed logging by setting:

```bash
export PYTHONPATH="."
python -m database.migration_utility --dry-run
```

Check logs for detailed error messages and API responses.

## Rollback Plan

If you need to rollback to MongoDB:

1. Change your `.env` file:
   ```bash
   DATABASE_PROVIDER=mongodb
   ```

2. Restart your application

Your MongoDB data remains unchanged during migration, so rollback is safe.

## Performance Considerations

### Xano vs MongoDB

**Advantages of Xano**:
- No server maintenance
- Built-in API
- Web interface for data management
- Automatic backups

**Considerations**:
- API rate limits
- Network latency for API calls
- Potentially higher costs for large datasets

### Optimization Tips

1. **Batch Size**: Start with smaller batches (25-50) for initial migration
2. **Timeouts**: Increase timeout for large conversations
3. **Monitoring**: Monitor Xano workspace usage during migration
4. **Cleanup**: Consider archiving old conversations before migration

## Support

### Resources

1. **Xano Documentation**: https://docs.xano.com
2. **API Testing**: Use Postman or curl to test your Xano endpoints
3. **Xano Community**: https://community.xano.com

### Contact

For migration-specific issues:
1. Run migration with `--dry-run` to identify problems
2. Check the error logs generated during migration
3. Verify your Xano API endpoints are working correctly
4. Test with a small subset of data first

## Migration Checklist

- [ ] Xano workspace set up
- [ ] Database table created with correct field types
- [ ] API endpoints implemented and tested
- [ ] API token generated
- [ ] Environment variables configured
- [ ] Dry run migration completed successfully
- [ ] Actual migration completed
- [ ] Migration verified
- [ ] Application tested with Xano
- [ ] MongoDB connection disabled (optional)

## Post-Migration

After successful migration:

1. **Monitor Performance**: Watch for any performance differences
2. **Backup Strategy**: Ensure Xano backups are configured
3. **Access Control**: Review API token permissions
4. **Cost Monitoring**: Monitor Xano usage and costs
5. **Documentation**: Update your deployment documentation

Remember to update your deployment scripts and documentation to reflect the new Xano configuration. 