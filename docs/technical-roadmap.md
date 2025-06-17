# Micronutrient Radar • Technical Roadmap

Version 1.0 · March 2024  
Author: Engineering Team Manager  
Audience: Engineering, Product, QA, DevOps

---

## 1. Overview
This document outlines the technical plan and phased roadmap for the Micronutrient Radar product. It details key deliverables, technical milestones, dependencies, and risk management strategies to ensure successful and timely delivery.

---

## 2. Phases & Milestones

### Phase 0: Project Bootstrap
- Stack selection (frontend, backend, cloud, CI/CD)
- Repository setup & branching strategy
- Initial infrastructure (dev/staging/prod environments)
- Team onboarding

### Phase 1: Core Food Image Processing & Task Pipeline
- ✅ Implement image upload and camera capture
- ✅ Set up Celery task infrastructure
  - ✅ Configure Redis broker and backend
  - ✅ Set up task monitoring with Flower
  - ✅ Implement task status tracking
  - ✅ Add retry logic and error handling
- ✅ Integrate LLM-based food recognition pipeline
  - ✅ Create food recognition Celery task
  - ✅ Implement task result caching
  - ✅ Add task status polling
- Implement confidence scoring & review UI
- Unit and integration tests for task pipeline

### Phase 2: Nutrition Mapping & Data Model
- ✅ Implement LLM-based nutrient estimation pipeline
  - ✅ Create nutrient estimation Celery task
  - ✅ Implement task orchestration between recognition and estimation
  - ✅ Add comprehensive error handling
  - ✅ Implement retry logic for failed API calls
- Design and implement nutrient caching system
  - Implement Redis-based cache (v1)
  - Migrate to persistent database storage (v2)
  - Add cache invalidation strategy
  - Implement cache warming for common foods
- ✅ Core data model implementation
  - ✅ User, FoodImage, FoodItem models
  - ✅ NutrientProfile model with caching
  - ✅ NutrientLedger for aggregation
  - ✅ TaskResult model for Celery task tracking
- Secure storage and encryption
- ✅ API endpoints for CRUD operations
- ✅ Data validation and error handling
- Unit conversion system (metric/imperial)
- Performance optimization
  - Implement batch processing for nutrient estimation
  - Add parallel processing for multiple items
  - Optimize LLM prompts for accuracy
  - Configure Celery worker concurrency

### Phase 2.1: Enhanced Data Model & Caching (Current Focus)
1. User Food History Database
   - Track when users eat meals (timestamp-based meal tracking)
   - Store what they ate (via food images)
   - Keep track of nutrients (per-meal nutrient totals)
   - Support basic meal type categorization (breakfast, lunch, dinner, snack)
   - Add API endpoints for history retrieval and analysis

2. Two-Tier Cache System
   - Implement global food cache for common items
   - Add user-specific cache based on history
   - Create cache lookup service
   - Implement cache warming strategy
   - Add cache invalidation and update mechanisms

3. Smart Task Pipeline Integration
   - Modify food image processing flow:
     1. Check user's personal cache
     2. Check global cache
     3. Fall back to OpenAI if needed
     4. Update both caches with new results
     5. Add to user's food history
   - Implement background tasks:
     - Daily nutrient aggregation
     - Cache warming based on user patterns
     - User preference updates
   - Add monitoring and analytics for cache hit rates

### Phase 3: Analytics, Radar Chart & Recommendations
- Nutrient aggregation logic (rolling 7-day window)
- Radar chart visualization (responsive, accessible)
- Gap-filler recommendation engine
- Weekly summary job (Celery periodic task)
  - PNG generation
  - Email/push delivery
- Shareable radar export (server-side PNG)

### Phase 4: User Experience & Feedback Loop
- Onboarding questionnaire & profile management
- User correction loop
  - Manual nutrient edits
  - Feedback to matcher
  - Confidence score adjustments
- Progress tracking and notifications
  - Real-time task status updates
  - Error notifications
  - Success confirmations
- Accessibility (WCAG 2.2 AA compliance, alt-table views)
- Internationalization (units, currency, date formats, RTL support)

### Phase 5: Monitoring, Scaling & Security
- Logging, metrics, and alerting
  - Structured logs
  - Celery task monitoring
  - Error tracking
  - Performance metrics
- Performance and load testing
  - Celery worker scaling
  - Queue management
  - Load distribution
- Auto-scaling and queue management
  - Celery worker auto-scaling
  - Queue prioritization
  - Task routing
- Security hardening
  - Encryption
  - Key rotation
  - Rate limiting
  - MFA
- GDPR/export/delete flows

### Phase 6: Beta & Launch
- Internal testflight/staging
- QA hardening, bug triage, and P0 fixes
- Documentation (API, user, internal)
- Production launch

---

## 3. Key Deliverables
- Functional ingestion and OCR pipeline
- Secure, scalable backend and data model
- Accurate nutrition mapping and aggregation
- Actionable, accessible user insights (radar, recommendations)
- Automated weekly summary delivery
- Robust monitoring, alerting, and compliance
- Comprehensive documentation

---

## 4. Technical Dependencies
- OpenAI/LLM provider (for food recognition and nutrient estimation)
- Redis (for Celery broker and result backend)
- Firebase Cloud Messaging (push)
- SendGrid (email)
- Cloud provider (for scaling, storage, backups)

---

## 5. Risk Management
| Risk | Mitigation |
|------|------------|
| LLM accuracy on food recognition and nutrient estimation | - Multi-tier confidence scoring<br>- User review UI<br>- Nutrient caching<br>- Model fine-tuning<br>- Regular validation against scientific sources |
| API rate limits (LLM) | - Celery task queuing<br>- Task rate limiting<br>- Caching<br>- Batching<br>- Monitoring<br>- Fallback logic |
| Task processing failures | - Automatic retries<br>- Error tracking<br>- Task monitoring<br>- Fallback strategies<br>- Queue management |
| Data privacy & PII exposure | - Client-side image processing by default<br>- Encryption<br>- Data retention policies |
| Scaling bottlenecks | - Celery worker auto-scaling<br>- Queue monitoring<br>- Load testing<br>- Batch processing |
| Accessibility gaps | - Early audits<br>- Manual and automated testing<br>- Progressive enhancement |
| Delayed external dependencies | - Mocking<br>- Feature flags<br>- Parallel development<br>- Fallback strategies |
| Nutrient estimation accuracy | - Regular validation against scientific sources<br>- User feedback loop<br>- Confidence scoring<br>- Expert review process |
| Processing latency | - Progress indicators<br>- Background task processing<br>- Incremental results display<br>- Caching strategy |

---

## 6. Timeline (Draft)
| Phase | Duration | Target Completion |
|-------|----------|------------------|
| 0 | 1 week | March 2024 |
| 1 | 2 weeks | March 2024 |
| 2 | 2 weeks | April 2024 |
| 3 | 2 weeks | April 2024 |
| 4 | 2 weeks | May 2024 |
| 5 | 2 weeks | May 2024 |
| 6 | 1 week | May 2024 |

---

## 7. Documentation & Communication
- Weekly engineering standups
- Sprint demo and review sessions
- Living documentation in repo (README, API docs, architecture diagrams)
- Slack/Teams for async updates

---

*End of Technical Roadmap v1.0* 