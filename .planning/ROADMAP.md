# Roadmap

**Project:** AI Virtual Try-On + Smart Styling Platform
**Granularity:** Fine
**Status:** Initialized

## Phases

- [ ] **Phase 1: Core VTO Engine** - Implement the diffusion-based inference pipeline for realistic garment overlay.
- [ ] **Phase 2: Async Infrastructure & API Gateway** - Build the scalable backend to handle long-running AI tasks.
- [ ] **Phase 3: User Experience & Photo Management** - Create the frontend for users to upload photos and view try-on results.
- [ ] **Phase 4: Product Catalog & Search** - Implement the searchable selection of garments for try-on.
- [ ] **Phase 5: Smart Styling Recommendations** - Integrate the RAG-based engine for "Complete the Look" advice.
- [ ] **Phase 6: Merchant Dashboard** - Deliver the interface for merchants to manage inventory and view analytics.

## Phase Details

### Phase 1: Core VTO Engine
**Goal**: Establish a functional local pipeline for high-fidelity virtual try-on.
**Depends on**: Nothing
**Requirements**: VTO-01
**Success Criteria** (what must be TRUE):
  1. System can take a user image and a garment image as input and output a merged try-on image.
  2. Garment textures and logos are preserved in the output using IDM-VTON.
  3. Body segmentation (SAM 2) prevents garment bleeding into the background.
**Plans**: TBD

### Phase 2: Async Infrastructure & API Gateway
**Goal**: Enable reliable, non-blocking execution of GPU-intensive tasks.
**Depends on**: Phase 1
**Requirements**: PLAT-01
**Success Criteria** (what must be TRUE):
  1. API returns a task ID immediately upon submission of a try-on request.
  2. Celery workers successfully pull tasks from Redis and execute the Phase 1 pipeline.
  3. Client can poll a status endpoint to retrieve the final generated image URL.
**Plans**: TBD

### Phase 3: User Experience & Photo Management
**Goal**: Allow users to interact with the try-on system through a web interface.
**Depends on**: Phase 2
**Requirements**: VTO-02
**Success Criteria** (what must be TRUE):
  1. User can upload a portrait photo through a web form with real-time validation (size/aspect ratio).
  2. User can view the processed try-on result in the browser once generation is complete.
  3. User can toggle between different uploaded garments to see them on their photo.
**Plans**: TBD
**UI hint**: yes

### Phase 4: Product Catalog & Search
**Goal**: Provide a curated and searchable set of garments for the try-on experience.
**Depends on**: Phase 3
**Requirements**: STYL-01
**Success Criteria** (what must be TRUE):
  1. User can browse a paginated gallery of men's shirts.
  2. User can search for specific items using text keywords.
  3. Selecting an item from the catalog automatically triggers the try-on workflow.
**Plans**: TBD
**UI hint**: yes

### Phase 5: Smart Styling Recommendations
**Goal**: Enhance the user experience with AI-driven fashion advice.
**Depends on**: Phase 4
**Requirements**: STYL-02
**Success Criteria** (what must be TRUE):
  1. User sees "Complete the Look" suggestions for matching items (pants/shoes) when a shirt is selected.
  2. Recommendations are generated via semantic retrieval from Weaviate based on the selected item.
  3. Suggestions include a brief AI-generated reasoning for the match (powered by Claude).
**Plans**: TBD
**UI hint**: yes

### Phase 6: Merchant Dashboard
**Goal**: Empower merchants to manage their garment inventory and monitor platform performance.
**Depends on**: Phase 5
**Requirements**: PLAT-02
**Success Criteria** (what must be TRUE):
  1. Merchant can log in and view a list of their uploaded garments.
  2. Merchant can upload a new garment image and define its metadata (price, category).
  3. Dashboard displays a metric for "Total Try-Ons" per garment.
**Plans**: TBD
**UI hint**: yes

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core VTO Engine | 0/1 | Not started | - |
| 2. Async Infrastructure | 0/1 | Not started | - |
| 3. User Experience | 0/1 | Not started | - |
| 4. Product Catalog | 0/1 | Not started | - |
| 5. Smart Styling | 0/1 | Not started | - |
| 6. Merchant Dashboard | 0/1 | Not started | - |
