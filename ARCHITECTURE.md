# 🏗️ Архитектура Universal HTML Renderer API

## Общая схема

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client Applications                          │
├─────────────────────────────────────────────────────────────────┤
│  Web App  │  Mobile App  │  CLI Tool  │  Other Services        │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP Requests
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Server (Port 8000)                                     │
│  ├── POST /scrape          (Single URL rendering)              │
│  ├── POST /scrape/batch    (Batch rendering)                   │
│  ├── GET  /health          (Health check)                      │
│  ├── GET  /stats           (Statistics)                        │
│  ├── GET  /docs            (Swagger UI)                        │
│  └── GET  /redoc           (ReDoc)                             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Core Engine                                │
├─────────────────────────────────────────────────────────────────┤
│  Universal Renderer (main_controller.py)                       │
│  ├── Detection Engine (detection_engine.py)                    │
│  ├── Local Renderer (universal_renderer.py)                    │
│  └── Browserbase Client (browserbase_client.py)                │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Rendering Levels                              │
├─────────────────────────────────────────────────────────────────┤
│  Level 2: Local Browser (Playwright Chromium)                  │
│  ├── Fast rendering for simple pages                           │
│  ├── Low cost                                                  │
│  └── High availability                                         │
│                                                                 │
│  Level 3: Browserbase (Cloud Browser Service)                  │
│  ├── Bypass complex blocking                                   │
│  ├── High reliability                                          │
│  └── Paid service                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Детальная архитектура

### 1. API Layer (FastAPI)

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Server                           │
├─────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                     │
│  ├── POST /scrape                                               │
│  │   ├── Input: {"url": "https://example.com"}                 │
│  │   └── Output: {html_content, metadata, analysis}            │
│  │                                                             │
│  ├── POST /scrape/batch                                         │
│  │   ├── Input: {"urls": ["url1", "url2", ...]}               │
│  │   └── Output: {results: [...], summary}                    │
│  │                                                             │
│  ├── GET /health                                                │
│  │   └── Output: {status, version, capabilities}              │
│  │                                                             │
│  └── GET /stats                                                 │
│      └── Output: {performance_metrics, configuration}          │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Core Engine

```
┌─────────────────────────────────────────────────────────────────┐
│                    Universal Renderer                           │
├─────────────────────────────────────────────────────────────────┤
│  Process Flow:                                                  │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │ 1. Receive  │───▶│ 2. Local     │───▶│ 3. Detection    │    │
│  │    URL      │    │    Render    │    │    Analysis     │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│                                 │                               │
│                                 ▼                               │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │ 6. Return   │◀───│ 5. Browserbase│◀───│ 4. Escalation   │    │
│  │    Result   │    │    Render    │    │    Decision     │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Detection Engine

```
┌─────────────────────────────────────────────────────────────────┐
│                    Detection Engine                             │
├─────────────────────────────────────────────────────────────────┤
│  Blocking Detection Rules:                                      │
│  ├── Title Keywords: ["Access Denied", "Blocked", ...]         │
│  ├── URL Patterns: ["/blocked", "/challenge", ...]             │
│  ├── HTML Selectors: [".blocked", "#challenge", ...]           │
│  └── Content Phrases: ["Please verify", "Captcha", ...]        │
│                                                                 │
│  Analysis Process:                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │ 1. Parse    │───▶│ 2. Apply     │───▶│ 3. Calculate    │    │
│  │    Content  │    │    Rules     │    │    Confidence   │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│                                 │                               │
│                                 ▼                               │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │ 6. Return   │◀───│ 5. Generate  │◀───│ 4. Make         │    │
│  │    Analysis │    │    Reasons   │    │    Decision     │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Rendering Levels

```
┌─────────────────────────────────────────────────────────────────┐
│                    Rendering Levels                             │
├─────────────────────────────────────────────────────────────────┤
│  Level 2: Local Browser (Baseline)                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Playwright Chromium                                        │ │
│  │  ├── Headless mode                                          │ │
│  │  ├── Custom user agent                                      │ │
│  │  ├── Resource blocking (images, fonts)                     │ │
│  │  ├── Context reuse                                          │ │
│  │  └── Timeout: 30s                                           │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Level 3: Browserbase (Fallback)                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Cloud Browser Service                                      │ │
│  │  ├── Residential proxies                                    │ │
│  │  ├── Anti-detection                                         │ │
│  │  ├── Global locations                                       │ │
│  │  ├── High success rate                                      │ │
│  │  └── Paid service                                           │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Инфраструктура

### Docker Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Infrastructure                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Docker Compose                                             │ │
│  │  ├── api-server (Port 8000)                                │ │
│  │  │   ├── FastAPI application                               │ │
│  │  │   ├── Health checks                                     │ │
│  │  │   ├── Auto-restart                                      │ │
│  │  │   └── Resource limits                                   │ │
│  │  │                                                         │ │
│  │  └── cli-service (Profile: cli)                            │ │
│  │      ├── CLI interface                                     │ │
│  │      ├── Batch processing                                  │ │
│  │      └── On-demand usage                                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Docker Image                                               │ │
│  │  ├── Python 3.11-slim                                      │ │
│  │  ├── Playwright Chromium                                   │ │
│  │  ├── System dependencies                                   │ │
│  │  ├── Security user                                         │ │
│  │  └── Health check tools                                    │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Monitoring & Logging

```
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring & Logging                         │
├─────────────────────────────────────────────────────────────────┤
│  Health Monitoring:                                             │
│  ├── GET /health - Service status                              │
│  ├── GET /stats - Performance metrics                          │
│  ├── Docker health checks                                      │
│  └── Auto-restart on failure                                   │
│                                                                 │
│  Logging:                                                       │
│  ├── Structured JSON logs                                      │
│  ├── Multiple log levels (DEBUG, INFO, WARNING, ERROR)        │
│  ├── Request/response logging                                  │
│  ├── Performance metrics                                       │
│  └── Error tracking                                            │
│                                                                 │
│  Metrics:                                                       │
│  ├── Render time per URL                                       │
│  ├── Success/failure rates                                     │
│  ├── Escalation frequency                                      │
│  ├── Resource usage                                            │
│  └── Detection accuracy                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Single URL Rendering

```
1. Client Request
   └── POST /scrape {"url": "https://example.com"}
       │
       ▼
2. API Validation
   └── Validate URL format
   └── Check request limits
       │
       ▼
3. Universal Renderer
   └── Initialize renderer
   └── Set configuration
       │
       ▼
4. Local Rendering (Level 2)
   └── Launch Playwright browser
   └── Navigate to URL
   └── Wait for page load
   └── Extract content
       │
       ▼
5. Detection Analysis
   └── Parse HTML content
   └── Apply blocking rules
   └── Calculate confidence score
       │
       ▼
6. Decision Making
   ├── If blocked → Escalate to Browserbase (Level 3)
   └── If not blocked → Return local result
       │
       ▼
7. Response Generation
   └── Format JSON response
   └── Include metadata
   └── Add analysis results
       │
       ▼
8. Client Response
   └── Return structured JSON
```

### Batch Rendering

```
1. Client Request
   └── POST /scrape/batch {"urls": ["url1", "url2", ...]}
       │
       ▼
2. API Validation
   └── Validate URL list (max 50)
   └── Check request limits
       │
       ▼
3. Parallel Processing
   └── Process each URL concurrently
   └── Apply same rendering logic
   └── Collect results
       │
       ▼
4. Response Aggregation
   └── Combine individual results
   └── Generate summary statistics
   └── Format batch response
       │
       ▼
5. Client Response
   └── Return batch results with summary
```

## Security & Performance

### Security Measures

```
┌─────────────────────────────────────────────────────────────────┐
│                        Security                                 │
├─────────────────────────────────────────────────────────────────┤
│  Container Security:                                            │
│  ├── Non-root user execution                                   │
│  ├── Minimal base image                                        │
│  ├── No unnecessary packages                                   │
│  └── Resource limits                                           │
│                                                                 │
│  API Security:                                                  │
│  ├── Input validation                                          │
│  ├── Rate limiting (configurable)                             │
│  ├── CORS configuration                                        │
│  └── Error handling                                            │
│                                                                 │
│  Network Security:                                              │
│  ├── Internal container communication                          │
│  ├── Port exposure control                                     │
│  └── Health check endpoints                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Performance Optimization

```
┌─────────────────────────────────────────────────────────────────┐
│                    Performance                                  │
├─────────────────────────────────────────────────────────────────┤
│  Browser Optimization:                                          │
│  ├── Headless mode                                             │
│  ├── Resource blocking (images, fonts)                        │
│  ├── Context reuse                                             │
│  └── Connection pooling                                        │
│                                                                 │
│  API Optimization:                                              │
│  ├── Async request handling                                    │
│  ├── Connection reuse                                          │
│  ├── Response compression                                      │
│  └── Caching strategies                                        │
│                                                                 │
│  Resource Management:                                           │
│  ├── Memory limits                                             │
│  ├── CPU limits                                                │
│  ├── Timeout controls                                          │
│  └── Auto-cleanup                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Scalability

### Horizontal Scaling

```
┌─────────────────────────────────────────────────────────────────┐
│                    Scalability                                  │
├─────────────────────────────────────────────────────────────────┤
│  Load Balancer                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  nginx/HAProxy                                              │ │
│  │  ├── Round-robin distribution                              │ │
│  │  ├── Health check routing                                  │ │
│  │  ├── SSL termination                                       │ │
│  │  └── Rate limiting                                         │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  API Server Instances                                       │ │
│  │  ├── Instance 1 (Port 8001)                                │ │
│  │  ├── Instance 2 (Port 8002)                                │ │
│  │  ├── Instance 3 (Port 8003)                                │ │
│  │  └── Instance N (Port 800N)                                │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Monitoring & Alerting

```
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring                                   │
├─────────────────────────────────────────────────────────────────┤
│  Metrics Collection:                                            │
│  ├── Prometheus metrics                                        │
│  ├── Custom business metrics                                   │
│  ├── System resource metrics                                   │
│  └── Application performance metrics                           │
│                                                                 │
│  Visualization:                                                 │
│  ├── Grafana dashboards                                        │
│  ├── Real-time monitoring                                      │
│  ├── Historical analysis                                       │
│  └── Alert configuration                                       │
│                                                                 │
│  Alerting:                                                      │
│  ├── High error rates                                          │
│  ├── Performance degradation                                   │
│  ├── Resource exhaustion                                       │
│  └── Service unavailability                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

**🎯 Эта архитектура обеспечивает высокую производительность, надежность и масштабируемость вашего API-сервиса!**