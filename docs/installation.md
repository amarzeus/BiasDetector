# Installation Guide

## System Requirements

### Backend Server
- Python 3.8 or higher
- 2GB RAM minimum
- 1GB free disk space
- Internet connection for API access

### Browser Extension
- Chrome 88+ or Firefox 78+
- 512MB RAM recommended
- Stable internet connection

## Quick Installation

### 1. Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/BiasDetector.git
cd BiasDetector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

### 2. Browser Extension

#### Chrome Web Store (Recommended)
1. Visit the [Chrome Web Store](https://chrome.google.com/webstore)
2. Search for "BiasDetector"
3. Click "Add to Chrome"
4. Accept permissions

#### Manual Installation (Development)
1. Download latest release or clone repository
2. Open Chrome/Firefox extensions page
3. Enable Developer Mode
4. Load unpacked from 'extension' folder
5. Verify icon in toolbar

## Detailed Setup Guide

### Backend Installation

1. **Prerequisites**
   - Python 3.8+
   - pip (Python package manager)
   - git

2. **Environment Setup**
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/BiasDetector.git
   cd BiasDetector
   
   # Create virtual environment
   python -m venv venv
   
   # Activate environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configuration**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   echo "SESSION_SECRET=your_session_secret" >> .env
   ```

4. **Start Server**
   ```bash
   # Development mode
   python main.py --dev
   
   # Production mode
   python main.py
   ```

### Extension Setup

1. **Development Build**
   ```bash
   cd extension
   npm install
   npm run build
   ```

2. **Browser Installation**
   - Open extensions page
   - Enable developer mode
   - Load unpacked extension
   - Select build directory

3. **Configuration**
   - Click extension icon
   - Open Settings
   - Enter API key (optional)
   - Customize preferences

## Production Deployment

### Server Deployment

1. **Setup Web Server**
   ```bash
   # Install nginx
   sudo apt install nginx
   
   # Configure nginx
   sudo nano /etc/nginx/sites-available/biasdetector
   ```

2. **nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/biasdetector /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. **SSL Setup**
   ```bash
   sudo apt install certbot
   sudo certbot --nginx
   ```

### Monitoring Setup

1. **System Service**
   ```bash
   sudo nano /etc/systemd/system/biasdetector.service
   ```
   ```ini
   [Unit]
   Description=BiasDetector Server
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/BiasDetector
   Environment="PATH=/path/to/BiasDetector/venv/bin"
   ExecStart=/path/to/BiasDetector/venv/bin/python main.py

   [Install]
   WantedBy=multi-user.target
   ```

2. **Start Service**
   ```bash
   sudo systemctl start biasdetector
   sudo systemctl enable biasdetector
   ```

## Verification

1. **Backend Check**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Extension Test**
   - Open extension
   - Click "Run Tests"
   - Verify all pass

## Troubleshooting

### Common Issues

1. **Port in Use**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 PID
   ```

2. **Permission Errors**
   ```bash
   sudo chown -R www-data:www-data /path/to/BiasDetector
   sudo chmod -R 755 /path/to/BiasDetector
   ```

3. **Module Not Found**
   ```bash
   pip install -r requirements.txt
   ```

### Support Resources

- Documentation: [docs.biasdetector.dev](https://docs.biasdetector.dev)
- GitHub Issues: [github.com/biasdetector/issues](https://github.com/biasdetector/issues)
- Community Forum: [forum.biasdetector.dev](https://forum.biasdetector.dev)
- Email: support@biasdetector.dev

---

For more details, visit [biasdetector.dev](https://biasdetector.dev)
