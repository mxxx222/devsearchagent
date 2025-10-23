#!/usr/bin/env python3
"""
Run script for the Search Dashboard web application.
This script starts the Flask development server on localhost.
"""

import os
import sys
from app import app

def main():
    """Main function to run the Flask application."""
    port = int(os.environ.get('PORT', 8000))
    print("🚀 Starting Search Dashboard...")
    print(f"📊 Dashboard will be available at: http://localhost:{port}")
    print("❌ Press Ctrl+C to stop the server")

    # Ensure we're in development mode
    os.environ['FLASK_ENV'] = 'development'

    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()