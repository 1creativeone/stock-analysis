# Deployment Guide

## Quick Deploy Options

### 1. Docker (Recommended)

**Prerequisites:**
- Docker installed
- Docker Compose installed (optional)

**Option A: Docker Compose (Easiest)**
```bash
# Clone repository
git clone <your-repo>
cd stock-analysis

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Option B: Docker CLI**
```bash
# Build image
docker build -t stock-analysis .

# Run container
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  --name stock-analysis \
  stock-analysis

# View logs
docker logs -f stock-analysis

# Stop
docker stop stock-analysis
docker rm stock-analysis
```

**Access:** http://localhost:8501

---

### 2. Streamlit Cloud (Free)

**Steps:**
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repository
4. Select `dashboard.py` as main file
5. Deploy!

**Pros:**
- Free hosting
- Auto-deploy on git push
- HTTPS included

**Cons:**
- Resource limits
- Public only (private requires paid plan)

---

### 3. Railway.app

**Steps:**
1. Create account at [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select repository
4. Add start command: `streamlit run dashboard.py --server.port=$PORT`
5. Deploy!

**Pros:**
- Free tier ($5 credit/month)
- Easy setup
- Automatic HTTPS

---

### 4. Render.com

**Option A: Web Service**

Create `render.yaml`:
```yaml
services:
  - type: web
    name: stock-analysis
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
```

**Option B: Docker**
```yaml
services:
  - type: web
    name: stock-analysis
    env: docker
    dockerfilePath: ./Dockerfile
```

Deploy: `render deploy`

---

### 5. Heroku

**Create `Procfile`:**
```
web: streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0
```

**Deploy:**
```bash
heroku create your-app-name
git push heroku main
heroku open
```

---

### 6. DigitalOcean App Platform

**Steps:**
1. Create DigitalOcean account
2. App Platform → Create App
3. Connect GitHub
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `streamlit run dashboard.py --server.port=8080`
5. Deploy!

**Pricing:** $5-12/month

---

## Environment Variables

Set these for email alerts:

```bash
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### Docker
```bash
docker run -e EMAIL_SENDER=... -e EMAIL_PASSWORD=... ...
```

### Streamlit Cloud
Add in Settings → Secrets:
```toml
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
```

---

## Production Checklist

- [ ] Set environment variables
- [ ] Configure email alerts
- [ ] Set up data persistence (volumes)
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test error handling
- [ ] Set up logging
- [ ] Configure rate limiting (if needed)
- [ ] Add authentication (if needed)

---

## Scaling Considerations

### Performance
- Cache data locally
- Use Redis for session state (optional)
- Consider serverless for scanner
- Schedule scans during off-peak hours

### Storage
- Data directory can grow large
- Implement retention policy
- Use object storage (S3, GCS) for historical data

### Security
- Use secrets manager for credentials
- Enable authentication for dashboard
- Whitelist IPs if needed
- Regular security updates

---

## Monitoring

### Health Checks
```bash
# Docker
curl http://localhost:8501/_stcore/health

# Production
curl https://your-app.com/_stcore/health
```

### Logging
```bash
# Docker
docker logs -f stock-analysis

# Docker Compose
docker-compose logs -f app
```

### Metrics
- Response time
- Memory usage
- Scan duration
- Error rate
- User count

---

## Troubleshooting

### Port already in use
```bash
# Change port
streamlit run dashboard.py --server.port=8502
```

### Memory issues
```bash
# Limit Docker memory
docker run -m 1g ...
```

### Slow scans
- Reduce ticker list
- Increase cache retention
- Use faster instance type

### Module not found
```bash
# Rebuild with no cache
docker build --no-cache -t stock-analysis .
```

---

## Backup Strategy

### Daily Backups
```bash
# Backup results
tar -czf backup-$(date +%Y%m%d).tar.gz results/ data/

# Upload to S3/GCS
aws s3 cp backup-*.tar.gz s3://your-bucket/backups/
```

### Automated Backups
Add to crontab:
```bash
0 2 * * * /path/to/backup-script.sh
```

---

## Updates

### Pull Latest Code
```bash
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

### Rolling Updates
```bash
# Build new image
docker build -t stock-analysis:v2 .

# Run new container
docker run -d --name stock-analysis-new stock-analysis:v2

# Test
curl http://localhost:8502/_stcore/health

# Switch traffic
docker stop stock-analysis
docker rm stock-analysis
docker rename stock-analysis-new stock-analysis
```

---

## Support

For issues:
- Check logs first
- Review environment variables
- Test locally
- Check GitHub issues
- Create new issue with logs

---

## License

MIT License - See LICENSE file
