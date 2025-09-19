# Vercel Blob Storage Setup Guide

This guide will help you configure your Hootel application to use Vercel Blob for file storage instead of Amazon S3.

## Prerequisites

- A Vercel account (free tier available at [vercel.com](https://vercel.com))
- Python environment with dependencies installed (`pip install -r requirements.txt`)

## What is Vercel Blob?

Vercel Blob is a serverless object storage solution that's perfect for storing user-generated content like images, documents, and other files. It provides:
- Simple API for file operations
- Global CDN for fast file delivery
- Pay-as-you-go pricing
- Automatic file optimization

## Setup Steps

### 1. Create a Vercel Blob Store

1. Sign in to your [Vercel Dashboard](https://vercel.com/dashboard)
2. Navigate to the **Storage** tab
3. Click **Create Database**
4. Select **Blob** as the storage type
5. Choose a name for your blob store (e.g., "hootel-media")
6. Select your preferred region
7. Click **Create**

### 2. Get Your Access Token

1. In your Blob store dashboard, go to the **Tokens** tab
2. Click **Create Token**
3. Give it a name (e.g., "Django App Token")
4. Select **Read/Write** permissions
5. Copy the generated token (starts with `vercel_blob_rw_`)

⚠️ **Important**: Save this token securely - you won't be able to see it again!

### 3. Configure Your Environment

Create or update your `.env` file with the Vercel Blob token:

```env
# Vercel Blob Storage
VERCEL_BLOB_READ_WRITE_TOKEN="vercel_blob_rw_xxxxxxxxxxxxxx"

# Set DEBUG to False for production to use Vercel Blob
DEBUG="False"
```

### 4. How It Works

#### Development Mode (DEBUG=True)
- Files are stored locally in the `media/` directory
- Perfect for testing without using Vercel Blob credits

#### Production Mode (DEBUG=False)
- Files are automatically uploaded to Vercel Blob
- Direct URLs are provided for file access
- Files are served through Vercel's global CDN

### 5. Test the Configuration

1. Run migrations (if needed):
```bash
python manage.py migrate
```

2. Start the development server:
```bash
python manage.py runserver
```

3. Test file upload:
   - Go to Django Admin (`/admin`)
   - Try uploading a profile picture for a user
   - Or create a new item with images in the catalog

4. Verify in Vercel Dashboard:
   - Go to your Blob store dashboard
   - Check the **Files** tab to see uploaded files

## File Storage Structure

Files are organized with the following structure:
- User profile pictures: `accounts/{username}/{filename}`
- Item images: `items/{item_title}/{filename}`

## Storage Limits

### Free Tier
- 5 GB storage
- 100 GB bandwidth per month
- Unlimited requests

### Pro Tier
- Pay-as-you-go pricing
- $0.03 per GB stored
- $0.15 per GB bandwidth

## Migration from S3

If you have existing files in S3 that need to be migrated:

1. **Export from S3**: Download your files from S3 using AWS CLI or S3 console
2. **Upload to Vercel Blob**: Use a migration script or manually upload through Django Admin
3. **Update database records**: Ensure file paths in the database match the new structure

## Troubleshooting

### Token Not Working
- Verify the token starts with `vercel_blob_rw_`
- Ensure there are no extra spaces or quotes around the token
- Check token permissions are set to Read/Write

### Files Not Uploading
- Verify `DEBUG=False` in production (Vercel Blob only works in production mode)
- Check Vercel Blob dashboard for any quota limits
- Review server logs for detailed error messages

### File Not Found Errors
- Files uploaded to Vercel Blob get unique URLs
- Ensure you're using the correct URL format
- Check the Vercel Blob dashboard to confirm file exists

## Local Development

For local development with `DEBUG=True`:
1. Files are stored in `media/` directory
2. Create the directory if it doesn't exist:
```bash
mkdir media
```
3. Add to `.gitignore` to avoid committing uploaded files:
```
media/
```

## URL Structure

Vercel Blob URLs follow this pattern:
```
https://{store-id}.public.blob.vercel-storage.com/{pathname}
```

The custom storage backend handles URL generation automatically.

## Security Best Practices

1. **Never commit tokens**: Keep `.env` file in `.gitignore`
2. **Use environment variables**: Always load tokens from environment
3. **Rotate tokens regularly**: Create new tokens periodically
4. **Monitor usage**: Check Vercel dashboard for unusual activity
5. **Set CORS policies**: Configure CORS in Vercel if needed

## Additional Features

### Direct Upload from Frontend
Vercel Blob supports client-side uploads for better performance:
- Generate presigned URLs from your backend
- Upload directly from browser to Vercel Blob
- Reduces server load and improves upload speed

### Image Optimization
Vercel automatically optimizes images:
- Automatic format conversion (WebP, AVIF)
- Responsive image sizing
- Lazy loading support

## Support and Documentation

- [Vercel Blob Documentation](https://vercel.com/docs/storage/vercel-blob)
- [Vercel Storage Pricing](https://vercel.com/pricing/storage)
- [Django Storage Documentation](https://docs.djangoproject.com/en/5.2/topics/files/)

## Comparison: S3 vs Vercel Blob

| Feature | Amazon S3 | Vercel Blob |
|---------|-----------|-------------|
| Setup Complexity | High | Low |
| Free Tier | 12 months limited | Permanent free tier |
| Global CDN | CloudFront (separate) | Built-in |
| API Simplicity | Complex | Simple |
| Pricing | Complex tiers | Straightforward |
| Django Integration | django-storages | Custom backend (included) |

## Next Steps

1. Test file uploads in development
2. Deploy to production environment
3. Monitor usage in Vercel dashboard
4. Set up backup strategy if needed