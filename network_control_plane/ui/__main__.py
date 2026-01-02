"""Web UI entry point."""
import os
from .app import create_app

if __name__ == '__main__':
    app = create_app()
    # Use PORT environment variable or default to 5001 if 5000 is busy
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)

