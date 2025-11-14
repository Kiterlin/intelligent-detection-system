# Phase 2 Implementation Plan: Advanced Features & ML Closed-Loop

**Timeline**: 6-8 weeks
**Started**: 2025-11-14
**Goal**: Implement all 7 features from 功能扩展需求.md with balanced approach

---

## Stage 1: User Dashboard (Feature 1) - Foundation
**Goal**: Create user-facing dashboard with statistics and quick actions
**Status**: Not Started

### Backend Tasks
- [ ] Create dashboard stats endpoint `GET /api/v1/dashboard/stats`
- [ ] Implement aggregation queries (total detections, weekly count, object stats)
- [ ] Add model usage statistics calculation
- [ ] Implement Redis caching for dashboard data
- [ ] Add cache invalidation on new detections
- [ ] Write unit tests for dashboard API

### Frontend Tasks
- [ ] Create `/dashboard` route and page component
- [ ] Implement statistics cards (4 key metrics)
- [ ] Add ECharts pie chart for model usage
- [ ] Build recent activity list component
- [ ] Add quick action buttons (image/video detection)
- [ ] Ensure mobile responsive layout
- [ ] Write E2E tests for dashboard

### Success Criteria
- [x] Dashboard loads in <500ms (with cache)
- [x] Displays accurate statistics from detection_history
- [x] Charts render correctly with sample data
- [x] Mobile responsive layout
- [x] All tests passing

### Tests
- Unit tests for aggregation logic
- Cache behavior tests
- E2E navigation tests

---

## Stage 2: Dataset Management (Feature 5) - Data Organization
**Goal**: Enable project-based batch detection workflow
**Status**: Not Started

### Backend Tasks
- [ ] Create database models: Dataset, DataFile, BatchJob
- [ ] Write Alembic migration for new tables
- [ ] Implement Dataset CRUD APIs
- [ ] Implement file upload to dataset API
- [ ] Create batch detection endpoint using Celery Group
- [ ] Implement batch job progress tracking
- [ ] Write unit tests for batch operations

### Frontend Tasks
- [ ] Create dataset list page with CRUD operations
- [ ] Build dataset detail page
- [ ] Implement drag-drop file upload to dataset
- [ ] Create batch detection trigger UI
- [ ] Build batch job progress dashboard
- [ ] Add file management within dataset
- [ ] Write E2E tests for batch workflow

### Success Criteria
- [x] Can create dataset and upload 10+ files
- [x] Batch detection processes all files correctly
- [x] Progress updates in real-time
- [x] Individual file results accessible
- [x] All tests passing

### Tests
- Batch job orchestration tests
- File upload tests
- Progress tracking tests

---

## Stage 3: Alert System (Feature 3) - Intelligence Layer
**Goal**: Transform system into proactive security sentinel
**Status**: Not Started

### Backend Tasks
- [ ] Create AlertRule model and migration
- [ ] Implement Alert CRUD APIs
- [ ] Build rule engine to evaluate conditions
- [ ] Add email notification action (SMTP)
- [ ] Add webhook notification action
- [ ] Integrate rule checking into detection Celery task
- [ ] Write unit tests for rule engine

### Frontend Tasks
- [ ] Create alert rules management page
- [ ] Build rule builder UI (condition editor)
- [ ] Implement action configuration UI
- [ ] Create alert history/logs viewer
- [ ] Add rule toggle on/off controls
- [ ] Write E2E tests for alert workflow

### Success Criteria
- [x] Can create complex rules (e.g., "if shark detected and confidence > 0.8")
- [x] Detection triggers alerts correctly
- [x] Email/webhook delivery confirmed
- [x] Rules can be toggled on/off
- [x] All tests passing

### Tests
- Rule engine unit tests (complex conditions)
- Notification integration tests
- Rule evaluation tests

---

## Stage 4: Comparison Tool (Feature 2) - Analysis
**Goal**: Enable side-by-side detection result comparison
**Status**: Not Started

### Backend Tasks
- [ ] Create comparison endpoint `GET /api/v1/history/compare`
- [ ] Implement object matching algorithm (IOU-based)
- [ ] Build diff calculation logic
- [ ] Write unit tests for matching algorithm

### Frontend Tasks
- [ ] Create comparison page with multi-select
- [ ] Build side-by-side image/video viewer
- [ ] Implement synchronized zoom/pan
- [ ] Create statistics comparison table
- [ ] Build diff visualization (color-coded objects)
- [ ] Write E2E tests for comparison workflow

### Success Criteria
- [x] Can select 2+ history records for comparison
- [x] Images display side-by-side with sync controls
- [x] Diff analysis shows unique/common objects
- [x] Works for both images and video
- [x] All tests passing

### Tests
- Object matching algorithm tests
- Comparison API tests
- UI interaction tests

---

## Stage 5: Report Engine (Feature 4) - Data Value
**Goal**: Generate professional PDF/HTML reports from detection data
**Status**: Not Started

### Backend Tasks
- [ ] Create Report model and migration
- [ ] Install dependencies: WeasyPrint, matplotlib, Jinja2
- [ ] Create report generation Celery task
- [ ] Build chart generation logic (matplotlib/plotly)
- [ ] Create Jinja2 HTML templates
- [ ] Implement WeasyPrint PDF conversion
- [ ] Create report download endpoint
- [ ] Write unit tests for report generation

### Frontend Tasks
- [ ] Create report creation wizard
- [ ] Build report list page with status tracking
- [ ] Add download buttons (PDF/HTML)
- [ ] Create report preview modal
- [ ] Write E2E tests for report workflow

### Success Criteria
- [x] Can generate report for date range
- [x] PDF contains: cover, stats, charts, high-risk targets
- [x] Generation completes in <2 min for 100 detections
- [x] Reports downloadable and readable
- [x] All tests passing

### Tests
- Template rendering tests
- PDF generation tests
- Async task tests

### Dependencies
- WeasyPrint
- matplotlib
- Jinja2

---

## Stage 6: Annotation Tool (Feature 6) - Data Collection
**Goal**: Enable users to correct/refine detection results
**Status**: Not Started

### Backend Tasks
- [ ] Create Annotation model and migration
- [ ] Implement Annotation CRUD APIs
- [ ] Create export annotations endpoint
- [ ] Write unit tests for annotation APIs

### Frontend Tasks
- [ ] Research and integrate label-studio-frontend
- [ ] Create annotation page
- [ ] Load detection results as pre-annotations
- [ ] Implement bounding box editor
- [ ] Build save corrected annotations feature
- [ ] Write E2E tests for annotation workflow

### Success Criteria
- [x] Can open any detection result in annotation tool
- [x] Pre-loaded boxes from model displayed
- [x] User can adjust/delete/add boxes
- [x] Corrected annotations saved to database
- [x] All tests passing

### Tests
- Annotation save/load tests
- Library integration tests

### Dependencies
- label-studio-frontend (or similar)

---

## Stage 7: Model Training (Feature 7) - Closed Loop
**Goal**: Train custom YOLO models from corrected annotations
**Status**: Not Started

### Backend Tasks
- [ ] Create TrainingJob model and migration
- [ ] Implement training job CRUD APIs (admin only)
- [ ] Build annotation export to YOLO format
- [ ] Create training Celery task (dedicated GPU queue)
- [ ] Implement real-time log streaming
- [ ] Add model auto-registration on completion
- [ ] Write unit tests for training workflow

### Frontend Tasks (Admin Panel)
- [ ] Create training job creation form
- [ ] Build job list with status monitoring
- [ ] Implement real-time log viewer
- [ ] Add training job cancel functionality
- [ ] Write E2E tests for training workflow

### Success Criteria
- [x] Can start training job from admin panel
- [x] Training runs successfully with corrected data
- [x] Logs stream to frontend in real-time
- [x] New model automatically usable after completion
- [x] All tests passing

### Tests
- Data export tests
- YOLO format conversion tests
- Model registration tests

### Dependencies
- GPU availability
- YOLO training workflow validation

---

## Implementation Timeline

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1-2  | Stage 1 & 2 | Dashboard + Dataset Management |
| 3    | Stage 3 | Alert System |
| 4    | Stage 4 | Comparison Tool |
| 5    | Stage 5 | Report Engine |
| 6    | Stage 6 | Annotation Tool |
| 7-8  | Stage 7 | Model Training + Integration Testing |

---

## Technical Decisions

1. **Annotation Library**: label-studio-frontend (most mature, YOLO-friendly)
2. **Report PDF**: WeasyPrint (Python-native, no headless browser)
3. **Charts**: Matplotlib for PDF, ECharts for web
4. **Caching**: Redis for dashboard stats
5. **Celery Queues**: Separate queues for detection, reports, training

---

## Risk Mitigation

1. **Scope Risk**: Each stage independently deliverable
2. **Complexity Risk**: Most complex stages (6-7) tackled last
3. **Performance Risk**: Heavy tasks use dedicated Celery queues
4. **Testing Risk**: Incremental testing, follow existing patterns

---

## Definition of Done (Per Stage)

- [ ] Backend APIs implemented with tests
- [ ] Frontend pages/components implemented
- [ ] Database migrations applied and tested
- [ ] All tests passing (pytest + E2E)
- [ ] Code follows ESLint rules
- [ ] Stage documented in completion report
- [ ] Committed to git with clear messages

---

## Progress Tracking

- **Completed Stages**: 0/7
- **Current Stage**: None
- **Blocked Items**: None
- **Next Actions**: Start Stage 1 - User Dashboard
