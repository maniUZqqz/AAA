# UpMarket — Database Design

Engine: **SQLite (Django's built-in database)** — decision D2, revised 2026-08-27. Zero setup on both machines; file location overridable via `SQLITE_PATH`. Models/migrations stay engine-agnostic, so a later move to PostgreSQL (if concurrent load ever demands it) only touches the `DATABASES` setting.

## 1. Existing Models (in `Main/myproject/Analysis`) — to be ported

- `Store(name, description, category, logo, owner→User, is_active, timestamps)`
- `Product(name, description, price, store→Store, is_available, timestamps)`
- `ProductFeature(product, key, value)`
- `ProductImage(product, image, is_main, created_at)`
- `ProductAnalysis(product 1:1, marketing, video_script, image_prompt, captions)` — free-text; superseded by structured intelligence below.

These are a reasonable seed; the target schema extends them per domain.

## 2. Target Schema by Domain

### accounts
- `User` (Django auth) + `UserProfile(user, display_name, phone, …)`

### stores (tenant boundary)
- `Store(owner→User, name, slug, business_type, description, target_audience, contact JSON, logo, colors JSON, social_links JSON, is_active, timestamps)`
- `StoreProfile(store 1:1, brand_voice, tone, content_style, visual_preferences JSON, shipping_policy, return_policy, refund_policy, payment_info, business_rules, working_hours JSON, ai_preferences JSON, publishing_preferences JSON)`

### products
- `Category(store, name, parent nullable)`
- `Product(store, category, name, slug, sku, description, short_description, brand, price, compare_at_price, currency, stock_quantity, stock_status, tags JSON, shipping_info JSON, marketing_notes, is_available, timestamps)`
- `ProductVariant(product, name, attributes JSON, price_override, stock_quantity, sku)`
- `ProductAttribute(product, key, value)`  ← generalizes current `ProductFeature`
- `ProductImage(product, image, is_main, alt_text, order, created_at)`

### ai
- `PromptVersion(prompt_id, version, model, params JSON, schema JSON, checksum, created_at)` — mirror of code registry for traceability
- `AIRequest(store, task_type, model, prompt_id, prompt_version, status, attempts, latency_ms, error, created_at)`
- `AIResponse(request 1:1, raw_output, parsed JSON, valid bool)`
- `ProductIntelligence(product 1:1, summary, target_audience JSON, selling_points JSON, weaknesses JSON, objections JSON, marketing_angles JSON, recommended_tone, content_ideas JSON, use_cases JSON, source_request→AIRequest, timestamps)` ← replaces free-text `ProductAnalysis`
- `MarketResearch(store, product nullable, sources JSON[{url, fetched_at}], observations JSON, conclusions JSON, confidence, created_at)` — observed facts kept separate from model conclusions

### customers (sales agent)
- `Customer(store, external_id, name, phone, channel, metadata JSON)`
- `Conversation(store, customer, state: AI|HUMAN|ESCALATED|RESOLVED, started_at, last_activity)`
- `Message(conversation, role: CUSTOMER|AI|HUMAN, text, intent, grounding JSON [product ids used], created_at)`
- `Order(store, customer, status, items…)` / `OrderItem(order, product, variant, qty, unit_price)` — created only from real DB data

### jobs
- `Job(store, type, state, priority, progress_step, total_steps, current_step_label, retry_count, error, related_object GenericFK, celery_task_id, timestamps)`
- States: `QUEUED → RUNNING → COMPLETED | FAILED | CANCELLED` (+ per-pipeline step labels)

### content
- `Asset(store, type: IMAGE|POSTER|CAPTION|SCRIPT|VIDEO_SEGMENT|VIDEO|AUDIO|FRAME, file, metadata JSON, source: GENERATED|UPLOADED, job→Job, prompt_version, model, workflow_version, parent→Asset nullable, status: DRAFT|PROCESSING|READY|APPROVED|REJECTED|FAILED|PUBLISHED|ARCHIVED, created_at)`
- `Caption(asset 1:1, platform: INSTAGRAM|TELEGRAM|LINKEDIN, tone, text, hashtags JSON, length_variant)`
- `VideoScript(campaign, concept, objective, total_duration, cta, raw JSON)`
- `VideoScene(script, index, duration, visual_prompt, motion_prompt, narration, transition: CONTINUE|TRANSITION|NEW_SCENE)`
- `VideoSegment(campaign, scene 1:1, index, status, retry_count, source_image→Asset, source_frame→Asset, video→Asset, final_frame→Asset, workflow_version, generation_metadata JSON, error, timestamps)`

### campaigns
- `Campaign(store, product, goal, audience, strategy JSON, status, approval_state, timestamps)` — groups strategy, poster, product image, captions, script, video, audio; each linked Asset carries its own status

### publishing
- `PublishJob(store, campaign, platform, payload JSON, n8n_delivery_status, attempts, last_error, published_at)`

## 3. Principles

- Core business entities = relational, queryable columns. JSON only for AI metadata, workflow metadata, flexible model-specific settings.
- Every store-owned table carries `store` FK; all querysets filter by it (tenancy at the ORM/permission layer).
- Generated files never exist without an `Asset` row; filenames are UUID-based, never user input.
- Indexes: FKs, `(store, created_at)` on hot tables, `Job.state`, `Asset.(store, type, status)`.
- Migration path: port existing `Analysis` models into `stores`/`products` apps in Phase 2–3; existing SQLite data is test data and may be discarded.
