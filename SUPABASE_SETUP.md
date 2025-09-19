# Supabase PostgreSQL Setup Guide

This guide will help you configure your Hootel application to use Supabase as your PostgreSQL database provider.

## Prerequisites

- A Supabase account (free tier available at [supabase.com](https://supabase.com))
- Python environment with dependencies installed (`pip install -r requirements.txt`)

## Setup Steps

### 1. Create a Supabase Project

1. Sign up or log in to [Supabase](https://supabase.com)
2. Click "New Project"
3. Fill in:
   - Project name (e.g., "hootel-db")
   - Database password (save this - you'll need it!)
   - Region (choose closest to your users)
4. Click "Create new project" and wait for setup to complete

### 2. Get Your Database Credentials

Once your project is ready:

1. Go to Project Settings (gear icon)
2. Navigate to "Database" section
3. Find your connection details:
   - **Host**: `db.[YOUR-PROJECT-REF].supabase.co`
   - **Database name**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: The password you set during project creation

### 3. Configure Your Environment

Create a `.env` file in your project root (copy from `.env.template`):

#### Option A: Using DATABASE_URL (Recommended)

```env
DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
```

Replace:
- `[YOUR-PASSWORD]` with your database password
- `[YOUR-PROJECT-REF]` with your project reference ID

#### Option B: Using Individual Parameters

```env
DB_NAME="postgres"
DB_USER="postgres"
DB_PASSWORD="your_password_here"
DB_HOST="db.xxxxx.supabase.co"
DB_PORT="5432"
```

### 4. Run Database Migrations

With your Supabase database configured, run Django migrations:

```bash
python manage.py migrate
```

### 5. Create a Superuser (Optional)

To access Django admin:

```bash
python manage.py createsuperuser
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

## Important Notes

### SSL Connection
The application automatically enables SSL when connecting to Supabase for security. This is configured in `settings.py`.

### Connection Pooling
Supabase has connection limits based on your plan:
- Free tier: 60 concurrent connections
- Pro tier: 200 concurrent connections

The application is configured with connection pooling (`conn_max_age=600`) to efficiently manage connections.

### Database Backups
Supabase automatically handles daily backups on paid plans. Free tier includes point-in-time recovery for 24 hours.

## Troubleshooting

### Connection Refused Error
- Verify your database credentials are correct
- Check that your Supabase project is active (not paused)
- Ensure your IP isn't blocked (Supabase allows all IPs by default)

### SSL Error
- The application automatically requires SSL for Supabase connections
- If you get SSL errors, ensure you're using the latest version of `psycopg2-binary`

### Migration Issues
- Ensure your database user has sufficient privileges
- Check Supabase dashboard for any database issues or maintenance

## Local Development Alternative

To use a local PostgreSQL database instead:

1. Install PostgreSQL locally
2. Update `.env`:
```env
DB_NAME="hootel_db"
DB_USER="your_local_user"
DB_PASSWORD="your_local_password"
DB_HOST="localhost"
DB_PORT="5432"
```

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong passwords** for your database
3. **Enable Row Level Security (RLS)** in Supabase for additional security
4. **Regularly update** your dependencies, especially `psycopg2-binary`

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Django Database Documentation](https://docs.djangoproject.com/en/5.2/ref/databases/)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)