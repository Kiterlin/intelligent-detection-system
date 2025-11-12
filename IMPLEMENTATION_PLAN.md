# Phase 3: AI Detection Core Implementation Plan

**Start Date**: 2025-11-12
**Estimated Duration**: 3-5 days
**Goal**: Implement complete AI object detection functionality with YOLO models

---

## Stage 1: Environment Setup & Dependencies
**Goal**: Install and configure all required AI and async processing libraries
**Success Criteria**:
- All Python packages installed successfully
- Celery worker can start and connect to Redis
- PyTorch and YOLO can be imported without errors

**Tests**:
- Import test: `python -c "import torch; import ultralytics; import cv2; import celery"`
- Celery ping test: `celery -A app.celery_app inspect ping`

**Status**: ✅ Completed (2025-11-12)

---

## Stage 2: Database Model Extension
**Goal**: Create DetectionHistory table to store all detection records
**Success Criteria**:
- DetectionHistory model created with all required fields
- Alembic migration generated and applied
- CRUD operations work correctly
- Pydantic schemas defined

**Tests**:
- Create a detection history record programmatically
- Query detection history with filters
- Update detection status
- Delete detection record

**Status**: ✅ Completed (2025-11-12)

---

## Stage 3: YOLO Model Loader Service
**Goal**: Implement efficient model loading and detection inference service
**Success Criteria**:
- ModelLoader singleton caches loaded models
- Can load .pt/.pth files from uploads/models/
- DetectionService preprocesses images correctly
- YOLO inference returns valid detection results
- Can draw bounding boxes on images

**Tests**:
- Load a YOLO model and verify it's cached
- Run inference on test image
- Verify detection results format (boxes, classes, confidence)
- Test image annotation with bounding boxes

**Status**: ✅ Completed (2025-11-12)

---

## Stage 4: Image Detection API
**Goal**: Expose synchronous image detection endpoint
**Success Criteria**:
- POST /api/v1/detect/image accepts image uploads
- Supports configurable confidence and IOU thresholds
- Returns detection results (bounding boxes, classes, scores)
- Saves annotated image to storage
- Records detection in DetectionHistory table

**Tests**:
- Upload image via API and get detection results
- Verify annotated image is saved correctly
- Check DetectionHistory record is created
- Test with different threshold parameters
- Test error handling (invalid image, no active model)

**Status**: ✅ Completed (2025-11-12)

---

## Stage 5: Video Detection with Celery
**Goal**: Implement asynchronous video detection using Celery tasks
**Success Criteria**:
- POST /api/v1/detect/video creates async task and returns task_id
- Celery task processes video frame-by-frame
- Progress updates available via status endpoint
- Generates annotated output video
- Updates DetectionHistory with results

**Tests**:
- Submit video for detection
- Query task status and verify progress updates
- Wait for completion and verify output video exists
- Check DetectionHistory record has correct statistics
- Test cancellation/failure scenarios

**Status**: ✅ Completed (2025-11-12)

---

## Stage 6: Detection History Management
**Goal**: Implement complete history CRUD and file download APIs
**Success Criteria**:
- GET /api/v1/detect/history with pagination and filters
- GET /api/v1/detect/history/{id} returns detailed record
- DELETE /api/v1/detect/history/{id} removes record and files
- GET /api/v1/detect/download/{id} serves result files
- Proper authorization (users can only access their own records)

**Tests**:
- List history with various filters (date range, type, status)
- Get history detail and verify all fields
- Download result image/video
- Delete history and verify files are removed
- Test unauthorized access (different user's records)

**Status**: ✅ Completed (2025-11-12)

---

## Technical Decisions

### Model Loading Strategy
- Use singleton pattern for ModelLoader to prevent duplicate loading
- Cache models in memory with LRU eviction if needed
- Load only the active model from database on startup

### File Storage
- Input files: `uploads/detections/input/{user_id}/{timestamp}_{filename}`
- Output files: `uploads/detections/output/{user_id}/{timestamp}_{filename}`

### Video Processing
- Extract frames at configurable FPS (default: original FPS)
- Process frames in batches for efficiency
- Use OpenCV for video I/O
- Update progress every N frames (e.g., every 10 frames)

### Error Handling
- Invalid file format → 400 Bad Request
- No active model → 503 Service Unavailable
- Detection failure → 500 Internal Server Error with details
- All errors logged with context for debugging

### Performance Considerations
- Use GPU if available (torch.cuda.is_available())
- Process images in batches when possible
- Limit concurrent video detection tasks (Celery max workers)
- Set reasonable file size limits (images: 10MB, videos: 200MB)

---

## Dependencies to Add

```txt
# AI & Computer Vision
torch>=2.1.0
torchvision>=0.16.0
ultralytics>=8.0.0
opencv-python>=4.8.0
pillow>=10.0.0

# Async Task Processing
celery>=5.3.0
redis>=5.0.0

# Additional utilities
python-multipart  # For file uploads (if not already added)
```

---

## Configuration Updates Needed

### backend/app/core/config.py
Add settings for:
- Redis URL
- Celery broker/backend URLs
- Detection file size limits
- Default detection parameters
- Model cache settings

### New files to create
- `backend/app/celery_app.py` - Celery application instance
- `backend/app/services/model_loader.py` - Model loading service
- `backend/app/services/detection.py` - Detection inference service
- `backend/app/models/detection_history.py` - DetectionHistory model
- `backend/app/schemas/detection.py` - Detection schemas
- `backend/app/crud/detection.py` - Detection CRUD operations
- `backend/app/api/v1/detect.py` - Detection endpoints
- `backend/app/tasks/detection.py` - Celery detection tasks

---

## Rollback Plan

If critical issues arise:
1. Revert to last working commit
2. Review error logs and stack traces
3. Check similar implementations in other projects
4. Consider simpler alternatives (e.g., synchronous video processing for MVP)

---

## Definition of Done

- [ ] All 6 stages completed
- [ ] All tests passing
- [ ] API documentation updated
- [ ] No linting errors
- [ ] Celery worker runs stably
- [ ] Can successfully detect objects in both images and videos
- [ ] Detection history properly managed
- [ ] Code committed with clear messages
- [ ] Ready for Phase 4 (frontend UI)
