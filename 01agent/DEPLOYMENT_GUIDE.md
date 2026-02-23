# 01Agent Complete Deployment Guide

## 🚀 Production Deployment

This guide covers deploying the complete 01Agent ecosystem including the desktop application, backend API, AI agent, and landing page.

## 📋 Prerequisites

### System Requirements
- **Node.js**: 16.x or higher
- **Python**: 3.8 or higher
- **npm**: 8.x or higher
- **Git**: Latest version
- **Docker**: Optional, for containerized deployment

### Platform Support
- **Windows**: 10/11 (64-bit)
- **macOS**: 10.14 or later
- **Linux**: Ubuntu 18.04+ or equivalent

## 🏗️ Build Process

### 1. Complete Build
```bash
# Build entire project
node build-complete-project.js

# Or build individual components
cd desktop && npm run clean-build
cd backend && pip install -r requirements.txt
cd desktop/aiagent && pip install -r requirements.txt
```

### 2. Verify Build
```bash
# Check build output
ls -la build-output/01agent-complete/

# Review build report
cat build-output/build-report.md
```

## 🌐 Landing Page Deployment

### Static Hosting (Recommended)
```bash
# Deploy to Netlify
netlify deploy --prod --dir=landing-page

# Deploy to Vercel
vercel --prod landing-page

# Deploy to GitHub Pages
# Push landing-page/ to gh-pages branch
```

### Custom Server
```bash
# Using nginx
sudo cp -r landing-page/* /var/www/html/
sudo systemctl reload nginx

# Using Apache
sudo cp -r landing-page/* /var/www/html/
sudo systemctl reload apache2
```

### CDN Configuration
```nginx
# nginx.conf
server {
    listen 80;
    server_name 01agent.ai;
    
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }
    
    # Enable gzip compression
    gzip on;
    gzip_types text/css application/javascript application/json;
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🔧 Backend API Deployment

### Production Server Setup
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with production values

# Run with gunicorn
pip install gunicorn
gunicorn main:app --workers 4 --bind 0.0.0.0:8000
```

### Docker Deployment
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "main:app", "--workers", "4", "--bind", "0.0.0.0:8000"]
```

```bash
# Build and run
docker build -t 01agent-backend backend/
docker run -p 8000:8000 01agent-backend
```

### Database Setup
```bash
# PostgreSQL (recommended for production)
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb 01agent

# Update .env
DATABASE_URL=postgresql://user:password@localhost/01agent

# Run migrations
cd backend
alembic upgrade head
```

### Reverse Proxy (nginx)
```nginx
# /etc/nginx/sites-available/01agent-api
server {
    listen 80;
    server_name api.01agent.ai;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🖥️ Desktop Application Distribution

### Windows Distribution
```bash
# Build Windows executable
cd desktop
npm run build:win

# Create installer
npm run dist

# Sign executable (optional)
signtool sign /f certificate.p12 /p password dist/01Agent-Setup.exe
```

### macOS Distribution
```bash
# Build macOS app
cd desktop
npm run build:mac

# Sign and notarize (for App Store)
codesign --deep --force --verify --verbose --sign "Developer ID" dist/01Agent.app
xcrun notarytool submit dist/01Agent.dmg --keychain-profile "notarytool-profile"
```

### Linux Distribution
```bash
# Build Linux AppImage
cd desktop
npm run build:linux

# Create .deb package
npm install -g electron-installer-debian
electron-installer-debian --src dist/linux-unpacked/ --dest dist/installers/
```

### Auto-updater Setup
```javascript
// main.js
const { autoUpdater } = require('electron-updater');

autoUpdater.setFeedURL({
  provider: 'github',
  owner: '01agent',
  repo: '01agent'
});

autoUpdater.checkForUpdatesAndNotify();
```

## 🤖 AI Agent Deployment

### Standalone Deployment
```bash
# Package AI agent
cd desktop/aiagent
pip install pyinstaller
pyinstaller --onefile enhanced_main.py

# Deploy to server
scp dist/enhanced_main user@server:/opt/01agent/
```

### Service Configuration
```ini
# /etc/systemd/system/01agent.service
[Unit]
Description=01Agent AI Service
After=network.target

[Service]
Type=simple
User=01agent
WorkingDirectory=/opt/01agent
ExecStart=/opt/01agent/enhanced_main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable 01agent
sudo systemctl start 01agent
```

## 🔒 Security Configuration

### SSL/TLS Setup
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d 01agent.ai -d api.01agent.ai

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Fail2ban (optional)
sudo apt install fail2ban
```

### Environment Security
```bash
# Secure .env files
chmod 600 backend/.env
chmod 600 desktop/aiagent/.env

# Use secrets management (production)
# AWS Secrets Manager, Azure Key Vault, etc.
```

## 📊 Monitoring & Logging

### Application Monitoring
```bash
# Install monitoring tools
npm install -g pm2

# Start backend with PM2
cd backend
pm2 start "gunicorn main:app --workers 4 --bind 0.0.0.0:8000" --name 01agent-api
pm2 startup
pm2 save
```

### Log Management
```bash
# Centralized logging with rsyslog
sudo apt install rsyslog

# Log rotation
sudo nano /etc/logrotate.d/01agent
```

### Health Checks
```bash
# Create health check endpoint
curl -f http://localhost:8000/health || exit 1

# Monitor with cron
*/5 * * * * /usr/local/bin/health-check.sh
```

## 🚀 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy 01Agent

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Build project
      run: node build-complete-project.js
      
    - name: Deploy to production
      run: |
        # Deploy commands here
        echo "Deploying to production..."
```

### Automated Testing
```bash
# Run tests before deployment
npm test
python -m pytest backend/tests/
python -m pytest desktop/aiagent/tests/
```

## 📈 Performance Optimization

### Frontend Optimization
```bash
# Optimize React build
cd desktop/01agent-app
npm run build
npm run analyze

# Enable compression
gzip_static on;
```

### Backend Optimization
```python
# Use Redis for caching
pip install redis
# Configure in backend/config/settings.py
```

### Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_threads_user_id ON threads(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
```

## 🔄 Backup & Recovery

### Database Backup
```bash
# Automated PostgreSQL backup
pg_dump 01agent > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup script
#!/bin/bash
BACKUP_DIR="/backups/01agent"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump 01agent | gzip > "$BACKUP_DIR/backup_$DATE.sql.gz"
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +7 -delete
```

### Application Backup
```bash
# Backup configuration and data
tar -czf 01agent_backup_$(date +%Y%m%d).tar.gz \
  backend/.env \
  desktop/aiagent/.env \
  /var/log/01agent/ \
  /opt/01agent/
```

## 🌍 Multi-Region Deployment

### Load Balancer Configuration
```nginx
upstream 01agent_backend {
    server backend1.01agent.ai:8000;
    server backend2.01agent.ai:8000;
    server backend3.01agent.ai:8000;
}

server {
    listen 443 ssl;
    server_name api.01agent.ai;
    
    location / {
        proxy_pass http://01agent_backend;
    }
}
```

### CDN Setup
```bash
# CloudFlare configuration
# 1. Add domain to CloudFlare
# 2. Configure DNS records
# 3. Enable caching rules
# 4. Set up SSL/TLS
```

## 📱 Mobile App Deployment (Future)

### React Native Setup
```bash
# Initialize React Native project
npx react-native init 01AgentMobile
cd 01AgentMobile

# Install dependencies
npm install @react-native-async-storage/async-storage
npm install react-native-vector-icons
```

## 🎯 Post-Deployment Checklist

### Verification Steps
- [ ] Landing page loads correctly
- [ ] Backend API responds to health checks
- [ ] Desktop app downloads and installs
- [ ] AI agent processes tasks successfully
- [ ] SSL certificates are valid
- [ ] Monitoring systems are active
- [ ] Backup systems are configured
- [ ] Performance metrics are within targets

### Performance Targets
- [ ] Landing page loads in < 2 seconds
- [ ] API response time < 200ms
- [ ] Desktop app startup < 3 seconds
- [ ] AI agent task completion 60-80% faster
- [ ] 99.9% uptime SLA

### Security Verification
- [ ] All endpoints use HTTPS
- [ ] Authentication is working
- [ ] Rate limiting is active
- [ ] Input validation is in place
- [ ] Logs don't contain sensitive data

## 🆘 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Clear caches
npm cache clean --force
pip cache purge

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### Performance Issues
```bash
# Check system resources
htop
df -h
free -m

# Monitor application
pm2 monit
tail -f /var/log/01agent/app.log
```

#### SSL Issues
```bash
# Test SSL configuration
openssl s_client -connect 01agent.ai:443
curl -I https://01agent.ai

# Renew certificates
sudo certbot renew --dry-run
```

## 📞 Support

For deployment support:
- **Documentation**: https://docs.01agent.ai/deployment
- **Community**: https://community.01agent.ai
- **Enterprise Support**: enterprise@01agent.ai
- **GitHub Issues**: https://github.com/01agent/01agent/issues

---

**01Agent Deployment Guide v2.0.0**  
Last updated: December 2024  
Built with ❤️ for maximum productivity