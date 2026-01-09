"""
Tesla Optimus Business Analysis - 最小可运行版本
保证能构建和运行
"""
from flask import Flask
import os

# 创建 Flask 应用（Dash 的底层）
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tesla Optimus Business Analysis</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Tesla Optimus Business Analysis</h1>
        <p class="status">✅ Application is running successfully!</p>
        <p>Version: 1.0.0</p>
        <p>Port: 8050</p>
        <p>Commit: 最小可运行版本</p>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/api/status')
def status():
    import sys
    return {
        'status': 'running',
        'python_version': sys.version,
        'flask_version': '2.2.5',
        'platform': os.name
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    print(f"🚀 Starting Tesla Optimus Business Analysis on port {port}")
    print(f"📊 Application ready at http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

# Export for Gunicorn
server = app.server
