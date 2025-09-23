# Trading Tracker Application

A desktop application for tracking and managing trading signals from Telegram groups.

## Features

- Real-time signal tracking from Telegram groups
- Dynamic keyword-based signal filtering
- Signal management and organization
- User-friendly interface
- Automatic signal updates

## Prerequisites

Before running the application, you only need:
Python 3.8 or higher installed
## Building and Running the Application

### Option 1: Using the Build Script (Recommended)

1. Run the build script:
```bash
.\build.bat
```

This will automatically:
- Install all required dependencies
- Create the application icon
- Build the executable file
- Generate the application in the `application` directory

2. After building, run the application:
```bash
cd application
Telegram_4_Trading.exe
```

### Option 2: Manual Build

If you prefer to build manually:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the build command:
```bash
python build.py
```

## Configuration

Before using the application, you need to configure your Telegram credentials:

1. Open `utils/telegram_client.py`
2. Replace the placeholder values with your Telegram API credentials:
   ```python
   api_id = "YOUR_API_ID"
   api_hash = "YOUR_API_HASH"
   ```

## Usage

1. **Initial Setup**
   - Launch the application
   - Enter your Telegram credentials when prompted
   - Complete the Telegram authentication process

2. **Managing Groups**
   - Add Telegram groups to track
   - Configure keywords for signal filtering
   - Monitor group activity

3. **Signal Management**
   - View incoming signals in real-time
   - Filter signals based on configured keywords
   - Track signal status and performance

## Troubleshooting

1. **Authentication Issues**
   - Ensure your Telegram API credentials are correct
   - Check your internet connection
   - Verify your phone number format

2. **Build Issues**
   - Ensure Python 3.8 or higher is installed
   - Check if you have write permissions in the directory
   - Verify internet connection for dependency installation

3. **Runtime Issues**
   - Check application logs
   - Verify Telegram group access
   - Ensure proper file permissions

## Support

For issues and support:
1. Check the troubleshooting section
2. Review the application logs
3. Contact the development team
