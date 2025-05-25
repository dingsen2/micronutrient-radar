# Product Specification • **Micronutrient Radar**

Version 1.0 · March 2024  
Author: Product Management (PM)  
Audience: Engineering, Design, Data, QA, DevOps

---

## 0 · Purpose & Scope
**Problem** — Most consumers meet calorie/protein goals yet remain chronically low on potassium, iron, magnesium, vitamin D, and B-12. Existing nutrition trackers demand per-meal logging or barcode scans, causing >80 % drop-off after one week.

**Solution** — *Micronutrient Radar* passively converts grocery receipts into a weekly micronutrient ledger, visualises gaps in a radar chart, and suggests three concrete foods to close those gaps.

---

## 1 · Goals & Success Metrics
| Goal | KPI | Success Target (90 days post-launch) |
|------|-----|--------------------------------------|
| **Habit formation** | Weekly Active Scanners (WAS) | ≥ 35 % of signed-up users scan a receipt at least once per week |
| **Insight clarity** | "Actionable" rating in NPS follow-up | ≥ 70 % mark insights 4 ★ or 5 ★ |
| **Data accuracy** | Manual correction rate | ≤ 10 % of auto-parsed items are corrected by user |
| **Engagement** | Radar share events (copy link / screenshot) | ≥ 15 % of weekly summaries shared |

---

## 2 · Personas
1. **Fitness-Minded Professional** (age 25-40)  
   *Goal:* Optimise micronutrients without tedious logging.  
2. **New Parent Meal-Planner** (age 30-45)  
   *Goal:* Ensure balanced nutrition for family; minimise food waste.  
3. **Nutrient-Deficient Patient** (any age)  
   *Goal:* Doctor advised more iron/B-12; needs progress feedback.

---

## 3 · High-Level User Journey
1. **Sign-up** → completes short questionnaire (age, gender, diet style, supplement use).  
2. **First grocery run** → snaps a receipt photo in app / uploads PDF email receipt.  
3. **System parses receipt** → displays item list for optional edits.  
4. **Micronutrient Radar** auto-generates → user sees radar chart + "Top 3 foods to add."  
5. **Weekly cadence** → Sunday evening e-mail & push summarise progress; user taps to view detailed chart.  
6. **Long-term** → trends page shows 4-week moving average & badges (e.g., "Iron Adequate 3 weeks").

---

## 4 · Functional Requirements

### 4.1 Food Image Ingestion
- Accept JPEG/PNG upload or live camera capture
- Max file size: 10 MB; multiple images per meal allowed
- Support for both individual food items and complete meals

### 4.2 LLM-based Food Recognition Pipeline
- Extract food items and portions from images
- Process both individual food items and complete meals
- Confidence thresholds:
  - High (≥ 80%): Auto-process
  - Medium (60-79%): "Yellow" review flag; user can edit
  - Low (< 60%): "Red" review flag; requires user input
- Error handling:
  - Retry failed recognition attempts (max 3)
  - Log confidence scores for model improvement
  - Track failure patterns by food type/image quality

### 4.3 Food → Nutrition Mapping
- Attempt match in order:  
  1. Exact food item match via LLM
  2. String fuzzy match (≥ 0.8 similarity)  
  3. Prompt LLM: *"Return best match USDA FoodData Central item id for: '[FOOD ITEM]'."*  
- Output: nutrient vector covering at least these 10 micros: Iron, Potassium, Magnesium, Calcium, Vitamin D, Vitamin B-12, Folate, Zinc, Selenium, Fiber.

### 4.4 Aggregation & Radar Chart
- Aggregate nutrients over a **rolling 7-day window**.  
- Compute % RDA based on age + gender defaults from NIH tables.  
- Render interactive radar (5 spokes by default; expand to 10 on tap).  
- Show textual "Scorecard" below radar (✔ adequate / ⚠ low).

### 4.5 Gap-Filler Recommendations
- Rule set: if % RDA < 70 %, surface food items richest in that nutrient (**per 100 kcal** ranking).  
- Limit to 3 suggestions; each includes portion size guidance and swap tip (e.g., "Swap iceberg for spinach (+iron, +folate)").  
- Track CTA clicks for analytics.

### 4.6 Onboarding Questionnaire
- Required fields: Age range, Sex at birth, Diet style (omnivore, vegetarian, vegan, pescatarian), Known deficiencies, Supplements.  
- Optional allergies for later roadmap.

### 4.7 Weekly Summary Delivery
- Every Sunday 18:00 local time, generate radar PNG + bulleted gaps + link to app.  
- Channel cascade: Push → if unopened in 4 h → E-mail fallback.

### 4.8 User Correction Loop
- Any item can be long-pressed → "Edit nutrients" → opens modal to pick correct match (search FDC API).  
- Edits feed back into SKU-matching service as supervised training data.

---

## 5 · Non-Functional Requirements
| Category | Requirement |
|----------|-------------|
| **Performance** | - Receipt parse turnaround ≤ 5 s (P95) on Wi-Fi, ≤ 12 s on 4G<br>- API response time < 200ms (P95)<br>- Page load time < 2s (P95) |
| **Privacy** | - All OCR runs client-side **by default**; cloud OCR only with opt-in toggle<br>- Data retention: 2 years max<br>- Right to be forgotten: 30-day deletion window |
| **Security** | - Data encrypted at rest (AES-256) & in transit (TLS 1.3)<br>- Key rotation: Every 90 days<br>- Rate limiting: 100 requests/minute per IP<br>- Session timeout: 24 hours<br>- MFA optional for all users |
| **Scalability** | - Design for 50k weekly receipts in Year 1<br>- Components requiring 10× headroom:<br>  - OCR processing queue<br>  - USDA FDC API cache<br>  - Weekly summary generation<br>- Auto-scaling triggers:<br>  - CPU > 70% for 5 minutes<br>  - Memory > 80% for 5 minutes<br>  - Queue length > 1000 items |
| **Accessibility** | - WCAG 2.2 AA compliance for colour contrast<br>- Radar has alt-table view<br>- Screen reader support for all features<br>- Keyboard navigation support |
| **Internationalisation** | - Support metric & imperial units<br>- Currency symbol agnostic<br>- Date format based on user locale<br>- RTL language support |

---

## 6 · External Interfaces & Dependencies
| Service | Purpose | Contract Notes |
|---------|---------|----------------|
| **USDA FoodData Central API** | Nutrient vectors | Cache for 24 h; respect rate limits (3 K/day per key). |
| **OpenAI / LLM provider** | Food recognition & mapping | Response time budget 1 s; must support function-call JSON mode. |
| **Push Gateway** | Notifications | Use Firebase Cloud Messaging unless alternative chosen. |
| **E-mail** | Weekly summary | SendGrid free tier (100 emails/day) initial. |

---

## 7 · Data Model (Logical)
```plaintext
User
  ├─ id (uuid)
  ├─ version (int)  # Schema version for migrations
  ├─ demographics {age_range, sex, diet_style}
  ├─ settings {units: metric|imperial}
  ├─ created_at (timestamp)
  ├─ updated_at (timestamp)
  ├─ last_login (timestamp)
  └─ indexes: [id, email]

FoodImage
  ├─ id (uuid)
  ├─ user_id (uuid, indexed)
  ├─ datetime (timestamp, indexed)
  ├─ image_url (encrypted)
  ├─ status {processed|needs_review|failed}
  ├─ recognition_confidence (float)
  ├─ created_at (timestamp)
  ├─ updated_at (timestamp)
  └─ indexes: [user_id, datetime]

FoodItem
  ├─ id (uuid)
  ├─ food_image_id (uuid, indexed)
  ├─ description (text)
  ├─ quantity (float)
  ├─ fdc_id (nullable, indexed)
  ├─ confidence (float)
  ├─ is_estimated (boolean)
  ├─ created_at (timestamp)
  ├─ updated_at (timestamp)
  └─ indexes: [food_image_id, fdc_id]

NutrientLedger (materialised weekly view)
  ├─ user_id (uuid, indexed)
  ├─ week_start (date, indexed)
  ├─ nutrient {iron: mg, potassium: mg, ...}
  ├─ percent_rda {iron: %, ...}
  ├─ last_updated (timestamp)
  ├─ data_source {image|manual|estimated}
  └─ indexes: [user_id, week_start]
```

---

## 8 · Privacy & Compliance
- **No health diagnoses** → avoids HIPAA classification (but treat as sensitive).  
- GDPR ready: user may request export/delete; plan simple CSV exporter v1.  
- Consent checkbox for "Use anonymised data to improve matching."  
- **PII redaction** before storage; log redaction unit tests required.

---

## 9 · Milestones & Timeline (draft)
| Sprint # | Duration | Objective | Owner |
|----------|----------|-----------|-------|
| 0 | 1 wk | Project bootstrap, choose stack, set up repo & CI | Eng Lead |
| 1 | 2 wk | Receipt capture UX + offline OCR POC | Front-end |
| 2 | 2 wk | SKU-to-FDC matcher v0 + nutrient aggregation | Back-end |
| 3 | 1 wk | Radar chart UI & RDA calculations | FE + Data |
| 4 | 1 wk | Gap suggestion prompt + rules | Data |
| 5 | 1 wk | Weekly summary job + e-mail template | DevOps |
| 6 | 1 wk | QA hardening, A11y, P0 bug fix | QA |
| **Beta Launch** | — | Internal testflight / staging link | All |

---

## 10 · Testing Requirements
| Category | Requirements |
|----------|-------------|
| **Unit Testing** | - Minimum 80% code coverage for core business logic<br>- All utility functions must have unit tests<br>- Mock external service calls |
| **Integration Testing** | - End-to-end receipt processing flow<br>- API integration tests with USDA FDC<br>- OCR accuracy validation suite |
| **Performance Testing** | - Load test with 100 concurrent users<br>- OCR processing time < 5s (P95)<br>- API response time < 200ms (P95) |
| **Security Testing** | - Quarterly penetration testing<br>- OWASP Top 10 compliance check<br>- Data encryption validation |
| **Accessibility Testing** | - Automated WCAG 2.2 AA compliance checks<br>- Manual testing with screen readers<br>- Color contrast validation |

## 11 · Monitoring & Observability
| Component | Requirements |
|-----------|-------------|
| **Logging** | - Structured JSON logging<br>- Log levels: ERROR, WARN, INFO, DEBUG<br>- Log retention: 30 days |
| **Metrics** | - Receipt processing success rate<br>- OCR confidence distribution<br>- API latency percentiles<br>- User engagement metrics |
| **Alerts** | - P95 latency > 1s<br>- Error rate > 1%<br>- OCR confidence < 60%<br>- API availability < 99.9% |
| **Error Tracking** | - Integration with error tracking service<br>- Error categorization and prioritization<br>- User impact assessment |

## 12 · Deployment & Infrastructure
| Aspect | Requirements |
|--------|-------------|
| **Environments** | - Development (dev)<br>- Staging (staging)<br>- Production (prod) |
| **Deployment** | - Blue-green deployment strategy<br>- Automated rollback on failure<br>- Zero-downtime deployments |
| **Database** | - Automated backups (daily)<br>- Point-in-time recovery<br>- Migration strategy with versioning |
| **Scaling** | - Auto-scaling based on CPU/Memory<br>- Read replicas for high-traffic periods<br>- CDN for static assets |

## 13 · Documentation Requirements
| Type | Requirements |
|------|-------------|
| **API Documentation** | - OpenAPI/Swagger specification<br>- Authentication flows<br>- Rate limiting details<br>- Error codes and handling |
| **User Documentation** | - In-app help center<br>- FAQ section<br>- Video tutorials<br>- Troubleshooting guides |
| **Internal Documentation** | - Architecture diagrams<br>- System dependencies<br>- Deployment procedures<br>- Incident response playbooks |

## 14 · Open Questions
1. Do we support multiple food images per day with partial overlaps?  
   *Answer: Yes, system will deduplicate items and merge nutrients within 24h window*
2. How do we handle restaurant meals (nutrients unknown)?  
   *Answer: Flag as "estimated" and use generic restaurant item database*
3. Which 5 v1 micronutrients are *most actionable*?  
   *Answer: Iron, Vitamin D, B12, Magnesium, and Potassium (based on common deficiencies)*
4. Marketing wants shareable radar—export PNG server-side or client canvas?  
   *Answer: Server-side for consistency and reduced client load*
5. Monetisation: affiliate links in v1 or wait for ≥10 k MAU?
   *Answer: Wait for 10k MAU to maintain user trust*
6. What is the backup strategy for LLM service?  
   *Answer: Fallback to alternative LLM provider if primary fails, with user consent*
7. How do we handle seasonal produce variations?  
   *Answer: Use USDA seasonal data to adjust nutrient values*

---

*End of Spec v1.0*
