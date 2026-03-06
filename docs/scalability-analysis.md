# Scalability Analysis: Technical Stack Evaluation

**Purpose**: Evaluate whether the recommended technical stack can scale to serve the Indian student market  
**Market Context**: 248 million K-12 students, 22.7M NEET + 13.1M JEE aspirants, $7.5B EdTech market  
**Document Version**: 1.0  
**Date**: January 2025

**Referenced Documents**:
- `docs/research/indian-student-market-analysis.md` - Market size, demographics, and device specifications (consolidated)
- `docs/system-architecture.md` - Backend architecture
- `docs/architecture-feature-mapping.md` - Frontend architecture (Hybrid Native Views + Skia Edges + D3-Force + Zustand)

---

## 1. Executive Summary

### Overall Verdict

**The current technical stack can scale to 1M users with modifications, but requires significant architectural changes for 10M+ users.**

The recommended stack (React Native Hybrid Views + Skia Edges + FastAPI + Supabase + Direct LLM APIs) is appropriate for MVP and early growth. The primary bottleneck is **LLM API costs and rate limits**, not database or client-side performance.

### Scalability Scorecard

| Component | 100K Users | 1M Users | 10M+ Users |
|-----------|------------|----------|------------|
| **Client-side (Hybrid Views + Skia Edges)** | ✅ Ready | ✅ Ready | ✅ Ready |
| **Supabase PostgreSQL** | ✅ Ready | ⚠️ Upgrade needed | ❌ Major changes |
| **Redis Caching** | ⚠️ Add service | ⚠️ Cluster needed | ⚠️ Cluster needed |
| **LLM APIs** | ❌ Bottleneck | ❌ Critical | ❌ Self-host required |
| **Offline Sync** | ✅ Ready | ⚠️ Jitter needed | ❌ Dedicated service |
| **CDN** | ⚠️ Add CDN | ✅ Required | ✅ Required |
| **Cost Viability** | ⚠️ Marginal | ✅ With caching | ⚠️ Self-host LLMs |

### Key Findings

1. **Client-side scales horizontally by design** - Each device runs independently
2. **LLM costs are the critical constraint** - Without caching, costs exceed revenue by 2.5x
3. **Supabase scales to 1M** with Team tier; 10M requires Enterprise or self-hosted
4. **Offline-first architecture is correct** - But needs sync storm handling at scale
5. **CDN is missing** from current stack - Critical for 1M+ users

---

## 2. Client-Side Scalability Assessment

### Architecture Under Evaluation

| Layer | Technology | Purpose |
|-------|------------|---------|
| Rendering | Hybrid: RN Animated.View (nodes) + Skia (edges) | 60fps rendering; native Views for nodes, Skia for Bézier edge curves |
| Layout | D3-Force | Physics-based node positioning |
| State (Canonical) | Zustand | Permanent data (nodes, edges) |
| State (Transient) | Reanimated SharedValues | 60fps UI updates |
| Gestures | React Native Gesture Handler | UI-thread gesture processing |
| Persistence | AsyncStorage | Local session storage |

*Source: `docs/architecture-feature-mapping.md`*

### Horizontal Scaling Characteristics

**The client-side architecture is inherently scalable because:**

- Each mobile device runs independently - no shared client resources
- "Millions of concurrent users" doesn't affect individual device performance
- Performance targets are per-device, not aggregate

**Verdict**: ✅ **Client-side scales horizontally by design**

### Memory Budget on 4GB RAM Devices

| Component | Memory Usage | Notes |
|-----------|--------------|-------|
| Hybrid rendering (65 node Views + Skia edge canvas) | 56-61 MB | Animated.View nodes + Skia edge layer (65-node hard limit per `mobile-features-core-ui.md` Section 3.6) |
| D3-Force simulation | 5-10 MB | Layout calculations |
| Zustand state | 5-10 MB | Node/edge data |
| App overhead | 10-15 MB | React Native runtime |
| **Total** | **76-96 MB** | Well within 150MB budget |

*Target from `docs/research/indian-student-market-analysis.md`: 150MB maximum footprint*
*Node limit from `docs/mobile-features-core-ui.md` §3.6: 65-node hard limit (warning at 50, performance mode at 40+)*

### Performance Targets

| Metric | Target | Achievable on 4GB? |
|--------|--------|-------------------|
| Frame rate | 60fps | ✅ Yes (with LOD) |
| Memory footprint | ≤150MB | ✅ Yes (~86MB typical) |
| Initial load time | <3 seconds | ✅ Yes (on 4G) |
| Node limit | 65 | ✅ Enforced in state (per `mobile-features-core-ui.md` §3.6) |

### Potential Client-Side Issues at Scale

| Issue | Impact | Mitigation |
|-------|--------|------------|
| App bundle size | Slow download on 2G/3G | Code splitting, lazy loading |
| AsyncStorage limits | 6MB default on Android | Use MMKV or SQLite for larger data |
| Background sync | Battery drain | Batch syncs, WiFi-only option |
| Offline storage growth | Device storage limits | Implement data eviction policy |

---

## 3. Backend Scalability Assessment

### 3.1 Supabase PostgreSQL Scaling

#### Tier Comparison

| Tier | RAM | vCPUs | Connections | Price | User Capacity |
|------|-----|-------|-------------|-------|---------------|
| **Pro** | 8GB | 2 | 500 | $25/mo | ~100K users |
| **Team** | 16GB | 4 | 1,000 | $599/mo | ~1M users |
| **Enterprise** | Custom | Custom | Custom | Custom | 10M+ users |

#### Concurrent User Calculations

**Assumptions**:
- DAU = 30% of registered users
- Peak concurrent = 20% of DAU
- Connection pooling ratio = 1:100 (PgBouncer)

| Scale | Registered | DAU | Peak Concurrent | Connections Needed |
|-------|------------|-----|-----------------|-------------------|
| 100K | 100,000 | 30,000 | 6,000 | ~60 |
| 1M | 1,000,000 | 300,000 | 60,000 | ~600 |
| 10M | 10,000,000 | 3,000,000 | 600,000 | ~6,000 |

**Verdict**:
- ✅ **100K**: Pro tier sufficient (500 connections > 60 needed)
- ⚠️ **1M**: Team tier needed (1,000 connections > 600 needed)
- ❌ **10M**: Enterprise or self-hosted required (6,000 connections)

### 3.2 Redis Caching Requirements

**Current Stack Gap**: Supabase does not include Redis natively. External service required.

#### Redis Use Cases

| Use Case | Priority | Data Type |
|----------|----------|-----------|
| LLM response caching | Critical | JSON responses |
| Session state | High | User session data |
| Rate limiting | High | Request counters |
| Real-time features | Medium | Pub/sub messages |

#### External Redis Options

| Provider | Model | Capacity | Price | Recommended For |
|----------|-------|----------|-------|-----------------|
| **Upstash** | Serverless | Pay-per-request | ~$0.20/100K requests | 100K users |
| **Redis Cloud** | Dedicated | Up to 500GB | $50-500/mo | 1M users |
| **Self-hosted** | Cluster | Unlimited | Infrastructure cost | 10M+ users |

**Verdict**: ⚠️ **External Redis required from Phase 1**

### 3.3 LLM API Rate Limits and Costs (CRITICAL BOTTLENECK)

#### Rate Limit Analysis

| Provider | Tier | Requests/Minute | Tokens/Minute |
|----------|------|-----------------|---------------|
| **Anthropic** | Tier 1 | 60 | 40,000 |
| **Anthropic** | Tier 2 | 1,000 | 80,000 |
| **Anthropic** | Tier 3 | 2,000 | 160,000 |
| **Anthropic** | Tier 4 | 4,000 | 400,000 |
| **OpenAI** | Tier 1 | 60 | 60,000 |
| **OpenAI** | Tier 5 | 10,000 | 2,000,000 |

#### Peak Hour Query Volume

*Peak hours: 6 PM - 11 PM (5 hours) per `docs/indian-student-market-analysis.md`*

| Scale | Peak Concurrent | 10% Making AI Queries | Queries/Hour | Queries/Minute |
|-------|-----------------|----------------------|--------------|----------------|
| 100K | 6,000 | 600 | 3,600 | 60 |
| 1M | 60,000 | 6,000 | 36,000 | 600 |
| 10M | 600,000 | 60,000 | 360,000 | 6,000 |

**Rate Limit Verdict**:
- ⚠️ **100K**: Tier 1 limit (60 RPM) is borderline
- ❌ **1M**: Exceeds Tier 4 (4,000 RPM) - Enterprise limits needed
- ❌ **10M**: Exceeds all standard limits - Self-hosted LLMs required

### 3.4 Peak Hour Capacity Planning

#### Traffic Pattern Assumptions

| Time Period | % of Daily Traffic | Notes |
|-------------|-------------------|-------|
| 6 AM - 12 PM | 15% | Morning study |
| 12 PM - 6 PM | 25% | Afternoon/after school |
| **6 PM - 11 PM** | **50%** | **Peak study hours** |
| 11 PM - 6 AM | 10% | Late night |

#### Infrastructure Sizing for Peak

| Scale | Peak Concurrent | DB Connections | Redis Ops/sec | LLM Queries/sec |
|-------|-----------------|----------------|---------------|-----------------|
| 100K | 6,000 | 60 | 1,000 | 1 |
| 1M | 60,000 | 600 | 10,000 | 10 |
| 10M | 600,000 | 6,000 | 100,000 | 100 |

---

## 4. Cost Implications Analysis

### 4.1 Revenue Model

*Based on `docs/indian-student-market-analysis.md`*

| Parameter | Value | Source |
|-----------|-------|--------|
| Freemium conversion rate | 2-5% (using 3%) | Industry benchmark |
| Free tier | ₹0 | Core features |
| Basic tier | ₹199/month | Unlimited chapters |
| Pro tier | ₹499/month | Full AI access |
| Average ARPU | ~₹300/month (~$3.50) | Weighted average |

### 4.2 Revenue Projections

| Scale | Registered | Paying (3%) | Monthly Revenue (₹) | Monthly Revenue ($) |
|-------|------------|-------------|---------------------|---------------------|
| 100K | 100,000 | 3,000 | ₹9,00,000 | $10,800 |
| 1M | 1,000,000 | 30,000 | ₹90,00,000 | $108,000 |
| 10M | 10,000,000 | 300,000 | ₹9,00,00,000 | $1,080,000 |

### 4.3 Infrastructure Cost Projections

#### Phase 1: 100K Users

| Component | Monthly Cost | Notes |
|-----------|--------------|-------|
| Supabase Pro | $25 | 8GB RAM, 500 connections |
| Redis (Upstash) | $50 | Serverless, ~5M requests |
| LLM APIs (no caching) | **$27,000** | 300K queries/day × $0.003/query |
| Hosting (FastAPI) | $100 | Render/Railway |
| CDN | $50 | Cloudflare Pro |
| **Total** | **$27,225** | |
| **Revenue** | $10,800 | |
| **Margin** | **-152%** | ❌ **Unsustainable** |

#### The LLM Cost Crisis

**Without caching, LLM costs exceed revenue by 2.5x at every scale.**

| Scale | LLM Cost (no cache) | Revenue | Deficit |
|-------|---------------------|---------|---------|
| 100K | $27,000/mo | $10,800/mo | -$16,200 |
| 1M | $270,000/mo | $108,000/mo | -$162,000 |
| 10M | $2,700,000/mo | $1,080,000/mo | -$1,620,000 |

**Root Cause Analysis**:
- 10 AI queries/user/day assumption
- 30% of users active daily
- 1,000 tokens/query average
- $0.003/1K tokens (Claude Sonnet pricing)

### 4.4 Revised Cost Model with Caching

**Target: 80% cache hit rate** (only 20% of queries hit LLM)

| Component | Without Caching | With 80% Cache | Savings |
|-----------|-----------------|----------------|---------|
| LLM queries | 100% | 20% | 80% |
| Cost multiplier | 1.0x | 0.2x | 5x reduction |

#### Revised Phase 1: 100K Users (with caching)

| Component | Monthly Cost | Notes |
|-----------|--------------|-------|
| Supabase Pro | $25 | |
| Redis (Upstash) | $100 | More storage for cache |
| LLM APIs (80% cached) | **$5,400** | 20% of original |
| Hosting (FastAPI) | $100 | |
| CDN | $50 | |
| **Total** | **$5,675** | |
| **Revenue** | $10,800 | |
| **Margin** | **+47%** | ✅ **Viable** |

#### Revised Phase 2: 1M Users (with caching)

| Component | Monthly Cost | Notes |
|-----------|--------------|-------|
| Supabase Team | $599 | 16GB RAM, 1000 connections |
| Redis Cloud | $300 | Dedicated instance |
| LLM APIs (80% cached) | **$54,000** | 20% of original |
| Hosting (FastAPI) | $500 | Multiple instances |
| CDN | $200 | |
| Celery workers | $300 | Async processing |
| **Total** | **$55,899** | |
| **Revenue** | $108,000 | |
| **Margin** | **+48%** | ✅ **Viable** |

### 4.5 Additional Cost Optimization Strategies

| Strategy | Cost Reduction | Implementation | Status |
|----------|----------------|----------------|--------|
| Use Claude Haiku for classification | 10x cheaper | Separate model per task | ✅ Adopted (see `system-architecture.md` §Stage 2) |
| Query limits for free tier | 50% fewer queries | 10 AI queries/day limit | Planned |
| Semantic caching (pgvector) | Additional 10-20% | Similar query matching | Planned |
| Self-hosted models at 10M | 80%+ savings | Llama 3, Mistral deployment | Future |

*Model split architecture: Claude Sonnet for question generation (Stage 1), Claude Haiku for post-hoc classification (Stage 2). Classification is a constrained structured-output task that doesn't require Sonnet's capabilities. Requires classification accuracy benchmarking before production deployment.*

---

## 5. Geographic Distribution Challenges

### India's Connectivity Landscape

*Source: `docs/research/indian-student-market-analysis.md`*

| Metric | Urban | Rural | Gap |
|--------|-------|-------|-----|
| School internet access | 47.29% | 18.47% | 28.82% |
| Mobile penetration | 125.3% | 58.8% | 66.5% |
| Median download speed | 40-168 Mbps | 20-40 Mbps | Variable |
| Bottom 10th percentile | 5-15 Mbps | 2-5 Mbps | Significant |

### 5.1 Offline-First Architecture Assessment

**Current Stack Capabilities**:

| Feature | Status | Implementation |
|---------|--------|----------------|
| Local persistence | ✅ MVP | AsyncStorage |
| Offline editing | ✅ MVP | Queue edits locally |
| Offline indicator | ✅ MVP | Network state detection |
| Sync on reconnect | ✅ MVP | Background sync |

**Verdict**: ✅ **Offline-first is correctly prioritized**

### 5.2 Sync Storm Problem

**Scenario**: Millions of rural users go offline during power outages or connectivity gaps. When connectivity returns, all attempt to sync simultaneously.

**Impact at Scale**:

| Scale | Offline Users (est. 30%) | Reconnect Window (1 hour) | Sync Requests/sec |
|-------|--------------------------|--------------------------|-------------------|
| 100K | 30,000 | 3,600 sec | 8 |
| 1M | 300,000 | 3,600 sec | 83 |
| 10M | 3,000,000 | 3,600 sec | 833 |

**Mitigation: Jittered Sync**

```python
# Spread reconnection syncs over 60 seconds
import random

def schedule_sync():
    jitter = random.uniform(0, 60)  # 0-60 second delay
    await asyncio.sleep(jitter)
    await perform_sync()
```

**With jitter, 833 req/sec becomes ~14 req/sec** (60x reduction)

### 5.3 CDN Requirements

**Current Gap**: No CDN mentioned in existing architecture.

**Required CDN Coverage**:

| Asset Type | Size | Cache Duration | Priority |
|------------|------|----------------|----------|
| App bundle (JS) | 5-10 MB | Per version | Critical |
| Curriculum data | 1-5 MB | 24 hours | High |
| Images/icons | 2-5 MB | 7 days | High |
| PYQ content | Variable | 24 hours | Medium |

**Recommended CDN**: Cloudflare (free tier for 100K, Pro for 1M+)

**India Edge Locations**:
- Mumbai (primary)
- Chennai
- Delhi
- Bangalore
- Hyderabad

### 5.4 Regional Database Considerations

**Current Setup**: Supabase ap-south-1 (Mumbai)

| Scale | Database Strategy | Latency Impact |
|-------|-------------------|----------------|
| 100K | Single region (Mumbai) | Acceptable |
| 1M | Add read replica (Chennai) | Improved for South India |
| 10M | Multi-region + sharding | Required for scale |

**LLM API Latency**:

| Provider | Location | Latency from India |
|----------|----------|-------------------|
| Anthropic | US | 200-300ms |
| OpenAI | US | 200-300ms |
| Azure OpenAI | India (preview) | 50-100ms |

**Mitigation**: Aggressive caching reduces latency impact for cached queries.

---

## 6. Bottleneck Identification by Scale

### 6.1 Phase 1: 100K Users

| Component | Status | Bottleneck? | Required Modification |
|-----------|--------|-------------|----------------------|
| Client (Hybrid Views + Skia Edges) | ✅ Ready | No | None |
| Supabase Pro | ✅ Ready | No | None |
| Redis | ⚠️ Missing | Minor | Add Upstash/Redis Cloud |
| LLM APIs | ❌ Problem | **YES** | Implement 80% caching |
| Offline sync | ✅ Ready | No | None |
| CDN | ⚠️ Missing | Minor | Add Cloudflare |

**Phase 1 Modifications Required**:

1. **Add Redis** (Upstash serverless)
   - LLM response caching
   - Session state
   - Rate limiting

2. **Implement LLM caching** (80%+ hit rate)
   - Cache by question hash
   - TTL: 30 days
   - Semantic similarity matching (Phase 2)

3. **Add CDN** (Cloudflare)
   - Static assets
   - App bundle
   - Curriculum data

4. **Query limits for free tier**
   - 10 AI queries/day
   - Upgrade prompts at limit

5. **Use cheaper models for classification**
   - Claude Haiku for post-hoc classification
   - Claude Sonnet for question generation only

### 6.2 Phase 2: 1M Users

| Component | Status | Bottleneck? | Required Modification |
|-----------|--------|-------------|----------------------|
| Client (Hybrid Views + Skia Edges) | ✅ Ready | No | None |
| Supabase | ⚠️ Upgrade | Approaching | Upgrade to Team tier |
| Redis | ⚠️ Scale | Moderate | Dedicated Redis instance |
| LLM APIs | ❌ Critical | **YES** | Enterprise rate limits |
| Offline sync | ⚠️ Scale | Moderate | Jittered sync |
| CDN | ✅ Required | No | Already in place |
| Database | ⚠️ Read load | Moderate | Add read replica |

**Phase 2 Modifications Required**:

1. **Upgrade Supabase to Team** ($599/mo)
   - 1,000 connections
   - 16GB RAM
   - Dedicated resources

2. **Add PgBouncer connection pooling**
   - Reduce connection overhead
   - Handle connection spikes

3. **Implement jittered sync**
   - 0-60 second random delay
   - Prevents sync storms

4. **Negotiate enterprise LLM rate limits**
   - Anthropic Enterprise tier
   - OpenAI Enterprise tier
   - Consider Azure OpenAI (India region)

5. **Add Celery workers**
   - Async LLM processing
   - Background classification
   - Podcast generation queue

6. **Implement semantic caching**
   - pgvector for embeddings
   - Similar query matching
   - Additional 10-20% cache hit improvement

7. **Add database read replica**
   - Chennai region for South India
   - Reduce read load on primary

### 6.3 Phase 3: 10M+ Users

| Component | Status | Bottleneck? | Required Modification |
|-----------|--------|-------------|----------------------|
| Client (Hybrid Views + Skia Edges) | ✅ Ready | No | None |
| Supabase | ❌ Limit | **CRITICAL** | Enterprise or self-hosted |
| Redis | ⚠️ Scale | Moderate | Redis Cluster |
| LLM APIs | ❌ Critical | **CRITICAL** | Self-hosted models |
| Offline sync | ❌ Scale | **CRITICAL** | Dedicated sync service |
| Database | ❌ Scale | **CRITICAL** | Sharding + replicas |

**Phase 3 Modifications Required**:

1. **Database migration**
   - Self-hosted PostgreSQL (Patroni cluster)
   - OR Supabase Enterprise
   - Read replicas in Mumbai, Chennai, Delhi
   - Sharding by user_id or region

2. **Self-hosted LLM deployment**
   - Llama 3 70B or Mistral Large
   - GPU infrastructure (A100s)
   - 80%+ cost reduction
   - No rate limits

3. **Dedicated sync microservice**
   - RabbitMQ or Kafka for queue
   - Separate service for sync processing
   - Conflict resolution engine

4. **Multi-region deployment**
   - Mumbai (primary)
   - Chennai (South)
   - Delhi (North)
   - Load balancing across regions

5. **Redis Cluster**
   - 6+ node cluster
   - Cross-region replication
   - 100K+ ops/sec capacity

6. **Rate limiting per user tier**
   - Token bucket algorithm
   - Different limits for Free/Basic/Pro
   - DDoS protection


