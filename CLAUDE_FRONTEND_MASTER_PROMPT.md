# CLAUDE FRONTEND MASTER PROMPT — DoctorOS-AI

> **Instructions for Claude:** You are building the complete frontend for **DoctorOS-AI**, an AI-powered medical practice management platform. The backend is a fully implemented FastAPI application. You have been provided two companion documents:
>
> 1. **PROJECT_FRONTEND_HANDOFF.md** — Full project context, architecture, data models, and feature descriptions
> 2. **FRONTEND_API_CONTRACT.md** — Exhaustive specification of every backend endpoint, request/response schemas, and authentication details
>
> **Read both documents completely before writing any code.** They are your single source of truth.

---

## 1. What You Are Building

A modern, professional healthcare SaaS frontend for DoctorOS-AI. This platform enables physicians to:

- Manage patients and appointments
- Record clinical visits with medications
- Upload and process medical documents (with OCR and AI extraction)
- Review AI-extracted medical entities and lab results
- Ask AI-powered questions about a patient's medical history (RAG)
- Conduct multi-turn clinical conversations with an AI assistant
- Generate and view AI-powered clinical summaries
- View unified patient timelines

The frontend must feel like a production-grade medical application: clean, trustworthy, precise, and safe. Every piece of AI-generated content must be clearly labeled, every citation must be preserved, and every clinical value must be displayed with absolute accuracy.

---

## 2. Critical Rules — Read Before Writing Any Code

These rules are **non-negotiable**. Violating any of them will produce a broken or dangerous application.

### Code Architecture Rules

1. **Read both documentation files completely before writing any code.** Do not start coding until you understand the full scope, every endpoint, and every schema.

2. **NEVER invent backend endpoints.** Only use endpoints documented in `FRONTEND_API_CONTRACT.md`. If a feature seems to need an endpoint that doesn't exist, do NOT create a mock or guess — clearly mark it as "Backend API not yet implemented" in the UI.

3. **NEVER modify the backend** unless explicitly requested by the user. The backend is complete and tested.

4. **Keep ALL API calls centralized in service modules** (`src/api/`). No component should ever call `fetch()` or `axios` directly. Every HTTP request flows through the centralized API client.

5. **Implement JWT authentication properly:**
   - Store the access token after login
   - Attach `Authorization: Bearer {token}` to every API request via an Axios interceptor
   - Handle 401 responses globally by redirecting to login
   - The token expires after **30 minutes** — there is NO refresh token mechanism; the user must re-authenticate
   - Protect all routes except `/login`

6. **Respect patient-level authorization.** A doctor can only access patients they have an active appointment with. If the backend returns `403`, display a clear message: *"You need an appointment with this patient to access their records."* Never assume a patient ID grants access.

7. **Build reusable, composable components.** Buttons, cards, tables, modals, badges, form inputs — all should be shared components in `src/components/`.

8. **Preserve medical data accuracy.** Never truncate, round, modify, or reformat medical values (lab results, medication dosages, vital signs). Display them exactly as the backend returns them.

9. **Make the application responsive.** It must work well on desktop (1280px+) and tablet (768px+). Mobile is not required but should not be broken.

10. **Implement proper loading, error, and empty states for EVERY API call.** No screen should ever show a blank white page while data loads. No failed request should silently swallow errors.

### Medical Safety Rules

11. **Clearly label ALL AI-generated content.** Every RAG answer, chat response, and clinical summary must display a visible badge or banner: *"AI-Generated Content — Requires Clinical Review"*.

12. **Preserve citations and source references.** RAG answers and chat messages include citations referencing source documents. These must be displayed as clickable references, never stripped or hidden.

13. **Never store API secrets, JWT secrets, or backend credentials in frontend code.** The frontend only stores the user's access token.

14. **Never bypass backend authorization.** Do not attempt to access endpoints without a valid token or circumvent 403 responses.

15. **Never assume a patient ID grants access.** Always handle 403 gracefully.

16. **Never expose another patient's records.** Always confirm the UI context matches the patient whose data is being displayed.

17. **Clearly identify frontend screens that require backend APIs not yet implemented.** Display "Coming Soon" or "Not Yet Available" with an explanation rather than broken functionality.

---

## 3. Recommended Tech Stack

Use the following stack unless the user explicitly requests alternatives:

| Layer | Technology | Notes |
|---|---|---|
| **Framework** | React 18+ with TypeScript | Strict mode, functional components only |
| **Build Tool** | Vite | Fast dev server, optimized builds |
| **Routing** | React Router v6+ | Nested routes, route guards |
| **Styling** | Tailwind CSS | Utility-first, responsive design |
| **HTTP Client** | Axios | Interceptors for auth headers and error handling |
| **State Management** | React Context or Zustand | Auth state, patient context |
| **Forms** | React Hook Form | Validation, error messages |
| **Icons** | Lucide React or Heroicons | Consistent, medical-appropriate icons |
| **Markdown Rendering** | react-markdown + remark-gfm | For clinical summary display |
| **Notifications** | react-hot-toast or sonner | Toast notifications for actions |

---

## 4. Project Structure

Organize the project as follows:

```
src/
├── api/                    # Centralized API client and service modules
│   ├── client.ts           # Axios instance with JWT interceptor, base URL config, error handling
│   ├── authApi.ts          # POST /auth/login, GET /auth/me
│   ├── patientApi.ts       # GET /patients/, POST /patients/, GET /patients/{id}
│   ├── appointmentApi.ts   # POST /appointments/, PATCH /appointments/{id}/status
│   ├── visitApi.ts         # POST /visits/
│   ├── documentApi.ts      # POST /documents/upload/{patient_id}, GET /documents/patient/{patient_id}, POST /documents/{id}/process
│   ├── reviewApi.ts        # GET /review/pending/entities, GET /review/pending/lab-results, POST /review/entities/{id}/review, POST /review/lab-results/{id}/review
│   ├── ragApi.ts           # POST /patients/{id}/ask
│   ├── conversationApi.ts  # POST /patients/{id}/chat, GET /patients/{id}/conversations, GET /patients/{id}/conversations/{id}
│   ├── summaryApi.ts       # GET /patients/{id}/summary, POST /patients/{id}/summary
│   └── timelineApi.ts      # GET /patients/{id}/timeline
│
├── components/             # Reusable UI components
│   ├── ui/                 # Primitives: Button, Input, Select, Badge, Card, Modal, Table, Spinner, Skeleton
│   ├── forms/              # Form field wrappers, validation displays
│   ├── medical/            # Citation, AILabel, LabValueDisplay, MedicationCard, TimelineEntry
│   └── layout/             # Sidebar, Topbar, PageHeader, EmptyState, ErrorFallback
│
├── contexts/               # React context providers
│   ├── AuthContext.tsx      # Auth state, login/logout, token management
│   └── PatientContext.tsx   # Currently selected patient context
│
├── hooks/                  # Custom React hooks
│   ├── useAuth.ts          # Auth context consumer
│   ├── useApi.ts           # Generic API call hook with loading/error/data states
│   └── usePatient.ts       # Patient context consumer
│
├── layouts/                # Layout components
│   └── AppLayout.tsx       # Sidebar + topbar + main content area
│
├── pages/                  # Page-level components (one per route)
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── PatientListPage.tsx
│   ├── PatientProfilePage.tsx
│   ├── AppointmentCreatePage.tsx
│   ├── VisitCreatePage.tsx
│   ├── DocumentManagementPage.tsx
│   ├── ReviewDashboardPage.tsx
│   ├── RAGAssistantPage.tsx
│   ├── ChatPage.tsx
│   └── ClinicalSummaryPage.tsx
│
├── types/                  # TypeScript interfaces matching backend schemas
│   ├── auth.ts             # LoginResponse, UserRead
│   ├── patient.ts          # PatientCreate, PatientRead, PatientUpdate
│   ├── appointment.ts      # AppointmentCreate, AppointmentRead, AppointmentStatus
│   ├── visit.ts            # VisitCreate, VisitRead, MedicationEntry
│   ├── document.ts         # DocumentRead, ProcessingStatus
│   ├── review.ts           # PendingEntity, PendingLabResult, ReviewAction
│   ├── rag.ts              # RAGQuestion, RAGAnswer, Citation
│   ├── conversation.ts     # ChatMessage, ConversationRead, ConversationDetail
│   ├── summary.ts          # ClinicalSummary
│   └── timeline.ts         # TimelineEntry, TimelineResponse
│
├── utils/                  # Helpers, formatters, validators
│   ├── formatDate.ts       # Date/time formatting
│   ├── formatMedical.ts    # Medical value formatting (preserve precision!)
│   └── constants.ts        # App-wide constants
│
├── App.tsx                 # Route definitions
├── main.tsx                # Entry point
└── index.css               # Tailwind directives
```

---

## 5. Development Phases

Build the application in this order. Complete each phase before starting the next. Each phase should produce working, testable functionality.

---

### Phase 1: Foundation

**Goal:** A working app shell with authentication, protected routing, and a sidebar layout.

**Tasks:**
1. **Project scaffolding** — Initialize with Vite + React + TypeScript + Tailwind CSS. Configure `tsconfig.json` with strict mode and path aliases (`@/` → `src/`).

2. **API client** (`src/api/client.ts`):
   - Create an Axios instance with `baseURL` pointing to the backend (default: `http://localhost:8000`)
   - Add a **request interceptor** that attaches `Authorization: Bearer {token}` from stored token
   - Add a **response interceptor** that catches 401 errors and redirects to `/login`
   - Export the configured instance for use by all service modules

3. **Auth API service** (`src/api/authApi.ts`):
   - `login(email, password)` → POST `/auth/login`
     - ⚠️ **CRITICAL:** This endpoint expects `application/x-www-form-urlencoded` form data, NOT JSON
     - Field names are `username` (which is the email) and `password`
     - Use `URLSearchParams` or Axios `params` with appropriate content type
   - `getMe()` → GET `/auth/me` → returns current user info

4. **Auth context** (`src/contexts/AuthContext.tsx`):
   - Store access token (in `localStorage` or React state)
   - Provide `login()`, `logout()`, `isAuthenticated`, and `user` state
   - On app load, check for existing token and validate with `GET /auth/me`
   - On logout, clear token and redirect to `/login`

5. **Login page** (`src/pages/LoginPage.tsx`):
   - Email and password fields with form validation
   - Submit button with loading state
   - Error display for invalid credentials (backend returns 401)
   - Redirect to dashboard on successful login
   - Clean, centered design with DoctorOS branding

6. **Protected route wrapper**:
   - Component that checks `isAuthenticated` before rendering children
   - Redirects unauthenticated users to `/login`
   - Shows loading spinner while checking auth state

7. **App layout** (`src/layouts/AppLayout.tsx`):
   - **Sidebar**: Navigation links — Dashboard, Patients, Review Dashboard
   - **Topbar**: App title/logo, user info, logout button
   - **Main content area**: Renders child routes
   - Sidebar should be collapsible on smaller screens

---

### Phase 2: Dashboard & Patient Management

**Goal:** Doctors can see their dashboard, browse patients, create new patients, and view patient profiles.

**Tasks:**

1. **Dashboard page** (`src/pages/DashboardPage.tsx`):
   - Fetch data from `GET /doctor/dashboard` (returns doctor info, stats)
   - Fetch patients from `GET /patients/`
   - Display: Welcome greeting with doctor name, patient count, quick action buttons (Create Patient, Upload Document)
   - Cards showing summary statistics

2. **Patient list page** (`src/pages/PatientListPage.tsx`):
   - Fetch from `GET /patients/` with `skip` and `limit` query parameters
   - Search bar (client-side filtering, or if backend supports it, via query params)
   - Paginated table: Name, Date of Birth, Gender, Contact info
   - "Create Patient" button → opens create form
   - Click on a patient row → navigates to patient profile

3. **Create patient form**:
   - POST to `/patients/` with `PatientCreate` schema
   - Fields: first_name, last_name, date_of_birth, gender, phone, email, address, emergency_contact_name, emergency_contact_phone
   - Required field validation, date picker for DOB
   - Success → redirect to patient profile; Error → display error message

4. **Patient profile page** (`src/pages/PatientProfilePage.tsx`):
   - Fetch from `GET /patients/{id}`
   - Tabbed interface:
     - **Overview**: Basic info, demographics, emergency contact
     - **Medical History**: Conditions (from patient data or extracted entities)
     - **Visits**: List of visits (from timeline or dedicated fetch)
     - **Medications**: Current and past medications
     - **Allergies**: Known allergies
     - **Lab Results**: Lab values with reference ranges
     - **Documents**: Document list with upload option
     - **Timeline**: Unified chronological view
     - **AI Assistant**: RAG Q&A and Chat
     - **Clinical Summary**: Generated summary view
   - ⚠️ **Patient edit functionality**: The backend has a `PatientUpdate` schema but **NO update endpoint is implemented**. Either omit the edit button entirely or show it as disabled with a "Coming Soon" tooltip. **Do NOT create a fake edit form.**

---

### Phase 3: Clinical Data Management

**Goal:** Doctors can create appointments, update appointment status, record visits, and view timelines.

**Tasks:**

1. **Appointment creation**:
   - Form: patient_id, appointment_date (datetime picker), reason, notes
   - POST to `/appointments/`
   - Display success confirmation
   - ⚠️ There is **no list appointments endpoint**. Appointments appear in the patient timeline. Do not build an appointments list page unless the user specifically requests it.

2. **Appointment status update**:
   - PATCH to `/appointments/{id}/status` with new status
   - Status values: `scheduled`, `checked_in`, `in_progress`, `completed`, `cancelled`, `no_show`
   - Display current status as a colored badge
   - Dropdown or button group to change status

3. **Visit creation** (`src/pages/VisitCreatePage.tsx`):
   - Form: patient_id, appointment_id (optional), visit_date, chief_complaint, subjective, objective, assessment, plan, notes
   - **Medications sub-form**: Dynamic list of medications, each with:
     - name, dosage, frequency, route, start_date, end_date (optional), active (boolean), notes
   - POST to `/visits/`
   - Complex form — use React Hook Form with field arrays for medications

4. **Patient timeline** (tab within Patient Profile):
   - Fetch from `GET /patients/{id}/timeline`
   - Display chronological entries: appointments, visits, documents, lab results, medications
   - Each entry type has a distinct icon and color
   - Entries are clickable to expand details
   - Timeline renders in reverse chronological order (newest first)

---

### Phase 4: Document Management

**Goal:** Doctors can upload documents, trigger processing, and review AI-extracted data.

**Tasks:**

1. **Document upload**:
   - Drag-and-drop zone + file picker button
   - POST to `/documents/upload/{patient_id}` as `multipart/form-data`
   - ⚠️ The form field name for the file is `file`
   - Show upload progress
   - Supported types indicated (PDF, images, etc.)
   - On success, show the returned document metadata

2. **Document list** (tab within Patient Profile → Documents):
   - Fetch from `GET /documents/patient/{patient_id}`
   - Display as cards or table: filename, upload date, processing status, file type
   - **Processing status badges**:
     - `pending` → gray/neutral
     - `processing` → blue/animated
     - `completed` → green
     - `failed` → red
   - Action button: "Process Document" → POST to `/documents/{id}/process` (triggers OCR and extraction)

3. **Review dashboard** (`src/pages/ReviewDashboardPage.tsx`):
   - Two sections:
     - **Pending Entities**: Fetch from `GET /review/pending/entities` — shows extracted medical entities (conditions, medications, allergies, procedures) awaiting review
     - **Pending Lab Results**: Fetch from `GET /review/pending/lab-results` — shows extracted lab values awaiting review
   - Each item displays: extracted value, source document, confidence score (if available), patient name
   - **Review actions** for each item:
     - **Approve**: Accept the extraction as-is → POST `/review/entities/{id}/review` or `/review/lab-results/{id}/review` with `action: "approve"`
     - **Reject**: Discard the extraction → same endpoint with `action: "reject"`
     - **Correct**: Modify the extracted value and approve → same endpoint with `action: "correct"` and corrected data
   - Correct action should open an inline edit form or modal

---

### Phase 5: AI Features

**Goal:** Doctors can ask questions about patients, have conversations, and see cited sources.

**Tasks:**

1. **RAG Q&A interface** (tab within Patient Profile → AI Assistant):
   - Text input for the doctor's question
   - POST to `/patients/{id}/ask` with `{ question: "..." }`
   - Display the answer with:
     - 🤖 **AI-Generated badge** prominently displayed
     - Answer text (may contain markdown — render it)
     - **Citations section**: List of cited sources with document references
     - Each citation should be clickable (linking to the document or showing document info)
     - Disclaimer: *"This AI-generated response is for informational purposes and requires clinical judgment."*

2. **Citation component** (`src/components/medical/Citation.tsx`):
   - Renders a citation reference (e.g., `[1]`, `[2]`)
   - On click, shows a popover or navigates to the source document
   - Displays: document filename, relevant text excerpt, page number (if available)

3. **Chat interface** (`src/pages/ChatPage.tsx` or tab within Patient Profile):
   - **Conversation sidebar**: List of past conversations
     - Fetch from `GET /patients/{id}/conversations`
     - Each shows: title (auto-generated from first question, up to 60 chars), created date, message count
     - Click to load conversation detail
   - **New conversation button**: Starts a fresh chat
   - **Message thread**:
     - POST to `/patients/{id}/chat` with `{ message: "...", conversation_id: "..." }` (omit `conversation_id` for new conversation)
     - Display messages in alternating user/assistant bubbles
     - Assistant messages include:
       - 🤖 AI-Generated label
       - Rendered markdown content
       - Citations (same citation component as RAG)
   - **Conversation detail view**:
     - Fetch from `GET /patients/{id}/conversations/{conversation_id}`
     - Renders full message history
     - Continue button to add more messages to the conversation

---

### Phase 6: Clinical Summary

**Goal:** Doctors can generate and view AI-powered clinical summaries for patients.

**Tasks:**

1. **Summary viewer** (tab within Patient Profile → Clinical Summary):
   - Fetch from `GET /patients/{id}/summary`
   - If a summary exists, display:
     - 🤖 **AI-Generated badge**
     - Summary content rendered as markdown
     - Generated timestamp
     - Citation references (timeline records used as sources)
     - Disclaimer: *"This AI-generated summary requires clinical review."*
   - If no summary exists, show an empty state: *"No clinical summary has been generated yet."*

2. **Generate/Regenerate**:
   - "Generate Summary" button (when no summary exists)
   - "Regenerate Summary" button (when summary exists, with confirmation modal)
   - POST to `/patients/{id}/summary`
   - Show loading state during generation (this may take several seconds)
   - On success, display the new summary

---

### Phase 7: Polish & Production Readiness

**Goal:** The application feels complete, handles all edge cases, and is accessible.

**Tasks:**

1. **Empty states** for every list/table:
   - No patients → "No patients yet. Create your first patient to get started."
   - No documents → "No documents uploaded. Upload a medical document to begin."
   - No conversations → "No conversations yet. Ask your first question."
   - No pending reviews → "All caught up! No pending reviews."
   - Pattern: Illustration/icon + descriptive text + action button

2. **Loading states**:
   - Skeleton loaders for content areas (not just spinners)
   - Page-level loading indicators
   - Button loading states (spinner + disabled during API calls)
   - File upload progress bar

3. **Error handling**:
   - Error boundaries around major page sections
   - API error display: Show meaningful messages from backend error responses
   - Network error handling: "Unable to connect to server"
   - 403 errors: "You need an appointment with this patient to access their records"
   - 404 errors: "Patient/resource not found"
   - Toast notifications for action success/failure

4. **Toast notifications**:
   - Success: Patient created, document uploaded, review submitted, etc.
   - Error: Failed operations with retry suggestions
   - Info: Processing started, etc.

5. **Responsive design**:
   - Sidebar collapses to hamburger menu on tablet
   - Tables switch to card layout on smaller screens
   - Forms remain usable on tablet widths
   - Test at 1280px, 1024px, and 768px breakpoints

6. **Accessibility**:
   - ARIA labels on all interactive elements
   - Keyboard navigation (Tab, Enter, Escape for modals)
   - Focus management (focus trap in modals, focus return on close)
   - Color contrast compliance (WCAG AA minimum)
   - Screen reader text for status badges and icons

---

## 6. Screen Architecture — Detailed Specifications

### Screen 1: Login Page
- **Route:** `/login`
- **Layout:** Centered card, no sidebar
- **Elements:**
  - App logo and name
  - Email input (type="email", required)
  - Password input (type="password", required)
  - "Sign In" button (full width, loading state)
  - Error message area (red text below form)
- **API:** POST `/auth/login` (form-data: `username` + `password`)
- **Behavior:**
  - On success → store token → redirect to `/dashboard`
  - On 401 → show "Invalid email or password"
  - If already authenticated → redirect to `/dashboard`

### Screen 2: Dashboard
- **Route:** `/dashboard`
- **Layout:** AppLayout with sidebar
- **Elements:**
  - Greeting: "Welcome, Dr. {last_name}"
  - Stats cards: Total patients, recent activity
  - Quick actions: "Create Patient", "Upload Document", "Review Pending"
  - Recent patients list (last 5–10)
- **API:** GET `/doctor/dashboard`, GET `/patients/?limit=10`

### Screen 3: Patient List
- **Route:** `/patients`
- **Layout:** AppLayout
- **Elements:**
  - Page header: "Patients" + "Create Patient" button
  - Search bar (filters by name)
  - Table columns: Name, DOB, Gender, Phone, Email
  - Pagination controls (Previous/Next, page size selector)
  - Click row → navigate to `/patients/{id}`
- **API:** GET `/patients/?skip={offset}&limit={pageSize}`

### Screen 4: Patient Profile
- **Route:** `/patients/:id`
- **Layout:** AppLayout
- **Elements:**
  - Patient header: Full name, DOB, gender, contact info
  - Tab navigation:
    - **Overview** — All demographics, emergency contact
    - **Medical History** — Extracted conditions (from review-approved entities)
    - **Visits** — Visit records with expandable details
    - **Medications** — Active and past medications table
    - **Allergies** — Allergy list with severity
    - **Lab Results** — Lab values with reference ranges, dates, monospace display
    - **Documents** — Document cards with upload and process actions
    - **Timeline** — Unified chronological view of all patient events
    - **AI Assistant** — RAG Q&A + Chat interface
    - **Clinical Summary** — AI-generated summary with citations
- **API:** GET `/patients/{id}` and tab-specific endpoints
- **Error:** Handle 403 — "You need an appointment with this patient"

### Screen 5: Appointment Management
- **Route:** Inline within Patient Profile or modal
- **Elements:**
  - Create form: date/time picker, reason, notes
  - Status display with change actions
- **API:** POST `/appointments/`, PATCH `/appointments/{id}/status`
- **⚠️ No list endpoint** — appointments are visible via timeline only

### Screen 6: Visit Recording
- **Route:** `/patients/:id/visits/new` or modal
- **Elements:**
  - Structured form: Chief complaint, Subjective, Objective, Assessment, Plan, Notes
  - Medications section with "Add Medication" button
  - Each medication row: name, dosage, frequency, route, dates, active toggle
  - Submit button with loading state
- **API:** POST `/visits/`

### Screen 7: Document Management
- **Route:** Tab within Patient Profile (Documents tab)
- **Elements:**
  - Upload dropzone (drag-and-drop + click to browse)
  - Document cards: filename, type, upload date, status badge
  - "Process" button for unprocessed documents
  - Processing status: pending → processing → completed/failed
- **API:** POST `/documents/upload/{patient_id}`, GET `/documents/patient/{patient_id}`, POST `/documents/{id}/process`

### Screen 8: Review Dashboard
- **Route:** `/reviews`
- **Layout:** AppLayout
- **Elements:**
  - Two-panel or tabbed layout:
    - **Pending Entities**: Cards/rows showing entity type, value, source document, patient
    - **Pending Lab Results**: Cards/rows showing test name, value, unit, reference range, patient
  - Each item has: Approve ✓, Reject ✗, Correct ✏️ action buttons
  - Correct action opens inline editor or modal
  - Empty state when no pending reviews
- **API:** GET `/review/pending/entities`, GET `/review/pending/lab-results`, POST `/review/entities/{id}/review`, POST `/review/lab-results/{id}/review`

### Screen 9: AI Assistant (RAG Q&A)
- **Route:** Tab within Patient Profile (AI Assistant tab)
- **Elements:**
  - Question input with "Ask" button
  - Answer card with:
    - 🤖 AI-Generated badge
    - Rendered markdown answer
    - Numbered citations `[1]`, `[2]`, etc.
    - Citations list: each links to source document with excerpt
    - Clinical disclaimer
  - History of past questions in the session (optional)
- **API:** POST `/patients/{id}/ask`

### Screen 10: Chat Interface
- **Route:** Tab within Patient Profile (AI Assistant tab, sub-tab) or dedicated route
- **Elements:**
  - Sidebar: Conversation list (title, date, message count) + "New Conversation" button
  - Main area: Message thread
    - User messages: Right-aligned, blue background
    - Assistant messages: Left-aligned, gray background, includes AI label + citations
  - Message input: Text area + "Send" button at bottom
  - Loading indicator while assistant responds
- **API:** GET `/patients/{id}/conversations`, GET `/patients/{id}/conversations/{conversation_id}`, POST `/patients/{id}/chat`

### Screen 11: Clinical Summary
- **Route:** Tab within Patient Profile (Clinical Summary tab)
- **Elements:**
  - If summary exists:
    - 🤖 AI-Generated badge
    - Rendered markdown content
    - "Generated on {timestamp}"
    - Citations/references section
    - "Regenerate" button (with confirmation)
    - Clinical disclaimer
  - If no summary:
    - Empty state illustration
    - "Generate Clinical Summary" button
    - Description: "AI will analyze this patient's complete medical history to generate a comprehensive clinical summary."
  - Loading state during generation
- **API:** GET `/patients/{id}/summary`, POST `/patients/{id}/summary`

---

## 7. Design Direction

### Visual Aesthetic
Professional healthcare SaaS — clean, minimal, and trustworthy. The UI should inspire confidence in both the data it displays and the AI features it provides.

### Color Palette
| Role | Color | Usage |
|---|---|---|
| **Primary** | Medical blue/teal (`#0F766E` or `#0D9488`) | Buttons, active states, links, sidebar accents |
| **Primary Light** | Light teal (`#CCFBF1`) | Hover states, selected backgrounds |
| **Background** | White (`#FFFFFF`) | Main content area |
| **Surface** | Light gray (`#F9FAFB`) | Cards, sidebar background, table headers |
| **Border** | Gray (`#E5E7EB`) | Dividers, card borders, input borders |
| **Text Primary** | Dark gray (`#111827`) | Headings, body text |
| **Text Secondary** | Medium gray (`#6B7280`) | Labels, secondary info |
| **Success** | Green (`#059669`) | Approved status, completed, success toasts |
| **Warning** | Amber (`#D97706`) | Pending status, attention needed |
| **Error** | Red (`#DC2626`) | Failed status, error messages, rejected |
| **Info** | Blue (`#2563EB`) | Processing status, informational badges |
| **AI Accent** | Purple (`#7C3AED`) | AI-generated content labels and accents |

### Typography
- **Font family:** System sans-serif stack (`Inter`, `ui-sans-serif`, `system-ui`, `-apple-system`)
- **Headings:** Bold, clear hierarchy (text-2xl → text-lg)
- **Body:** Regular weight, comfortable line height (1.5–1.75)
- **Medical values:** Monospace font (`font-mono`) for lab results, dosages, and numerical medical data
- **Minimum body text:** 14px (text-sm)

### Spacing & Layout
- **Grid system:** 8px base unit
- **Card padding:** 16px–24px (`p-4` to `p-6`)
- **Section gaps:** 24px–32px (`space-y-6` to `space-y-8`)
- **Sidebar width:** 256px (`w-64`), collapsible
- **Max content width:** 1280px for main content, centered
- **Generous whitespace** — never cram information together

### Component Patterns
- **Cards**: Used to group related data (patient info, stats, documents)
- **Tables**: Used for lists (patients, medications, lab results) — with striped rows and hover states
- **Badges/Pills**: Used for status indicators (processing, approved, rejected) — colored with rounded-full
- **Modals**: Used for confirmations (delete, regenerate) and quick actions (correct entity)
- **Tabs**: Used for patient profile sections — underlined style
- **Dropzone**: Used for file uploads — dashed border, icon center, hover highlight
- **Empty states**: Icon + text + CTA button, centered in the content area

### Medical Data Display Rules
- **Lab values**: Always use monospace font. Display value + unit + reference range. Color-code abnormal values (red for critical, yellow for borderline).
- **Medication dosages**: Never truncate. Display exact value as returned from backend.
- **Dates**: Consistent format throughout (e.g., "MMM DD, YYYY" for display, ISO for forms).
- **Status badges**: Consistent colors across the app (see color palette).

---

## 8. Authentication Flow — Implementation Detail

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTHENTICATION FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. User lands on app                                           │
│     → Check localStorage for existing token                    │
│     → If token exists → call GET /auth/me to validate          │
│     → If valid → proceed to dashboard                          │
│     → If invalid/expired → clear token → show login            │
│                                                                 │
│  2. User submits login form                                     │
│     → POST /auth/login                                          │
│     → Content-Type: application/x-www-form-urlencoded          │
│     → Body: username={email}&password={password}               │
│     → ⚠️ Field is "username" not "email"!                      │
│     → ⚠️ This is FORM DATA not JSON!                           │
│                                                                 │
│  3. On success (200)                                            │
│     → Response: { access_token: "...", token_type: "bearer" }  │
│     → Store access_token in localStorage                       │
│     → Set auth state → redirect to /dashboard                  │
│                                                                 │
│  4. Every subsequent API request                                │
│     → Axios interceptor adds header:                           │
│       Authorization: Bearer {access_token}                     │
│                                                                 │
│  5. On 401 response (anywhere in app)                          │
│     → Token has expired (30-minute lifetime)                   │
│     → Clear stored token                                       │
│     → Redirect to /login                                       │
│     → Show toast: "Session expired. Please sign in again."     │
│                                                                 │
│  6. No refresh token mechanism exists                          │
│     → User must re-enter credentials after expiry              │
│     → Do NOT implement refresh logic                           │
│                                                                 │
│  7. Logout                                                      │
│     → Clear token from localStorage                            │
│     → Clear auth state                                         │
│     → Redirect to /login                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Key Integration Warnings

These are the most common mistakes. Read carefully and avoid them.

> ⚠️ **Login is FORM DATA, not JSON.**
> `POST /auth/login` expects `Content-Type: application/x-www-form-urlencoded` with fields `username` (the user's email) and `password`. Sending JSON will result in a 422 error.

> ⚠️ **File uploads use multipart/form-data.**
> `POST /documents/upload/{patient_id}` expects `Content-Type: multipart/form-data` with the file in a field named `file`.

> ⚠️ **Patient edit does not work.**
> A `PatientUpdate` schema exists in the backend, but there is **no PUT/PATCH endpoint** for updating patients. Do not build an edit form. Display patient data as read-only or show "Edit (Coming Soon)".

> ⚠️ **No list appointments endpoint.**
> There is no `GET /appointments/` endpoint. Appointments are created (POST) and status-updated (PATCH), but listing is not available. Appointments appear in the patient timeline. Do not build an appointments list page.

> ⚠️ **No delete endpoints exist.**
> There are no DELETE endpoints for any resource (patients, appointments, visits, documents, etc.). Do not add delete buttons or functionality.

> ⚠️ **No user registration endpoint.**
> User accounts are created via CLI only. There is no signup page. Do not build a registration flow.

> ⚠️ **Conversation titles are auto-generated.**
> When a new chat conversation is created, the backend auto-generates a title from the first message (truncated to 60 characters). The frontend cannot set or modify the title.

> ⚠️ **Patient authorization requires an appointment.**
> If a doctor tries to access a patient they don't have an appointment with, the backend returns `403 Forbidden`. The frontend must handle this gracefully: display *"You need an appointment with this patient to access their records."* — do not show a generic "Access Denied" message.

> ⚠️ **Backend returns 422 for validation errors.**
> FastAPI returns 422 Unprocessable Entity with a detailed error body when request validation fails. Parse and display these errors clearly, mapping field names to form fields when possible.

---

## 10. API Client Implementation Reference

Here is a reference implementation for the API client. Adapt this to your specific needs:

```typescript
// src/api/client.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — attach JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — handle 401 globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

```typescript
// src/api/authApi.ts
import apiClient from './client';

export const authApi = {
  login: async (email: string, password: string) => {
    // ⚠️ FORM DATA, not JSON!
    const formData = new URLSearchParams();
    formData.append('username', email);  // Field is "username", value is email
    formData.append('password', password);
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data; // { access_token: string, token_type: string }
  },
  
  getMe: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};
```

```typescript
// src/api/documentApi.ts (file upload example)
import apiClient from './client';

export const documentApi = {
  upload: async (patientId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);  // ⚠️ Field name must be "file"
    
    const response = await apiClient.post(
      `/documents/upload/${patientId}`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          // Handle upload progress if needed
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 1)
          );
          console.log(`Upload progress: ${percentCompleted}%`);
        },
      }
    );
    return response.data;
  },
};
```

---

## 11. TypeScript Types Reference

Define TypeScript interfaces that match the backend schemas exactly. Here are the key types to implement:

```typescript
// src/types/auth.ts
interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface UserRead {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  specialty?: string;
  is_active: boolean;
}

// src/types/patient.ts
interface PatientCreate {
  first_name: string;
  last_name: string;
  date_of_birth: string; // ISO date string
  gender: string;
  phone?: string;
  email?: string;
  address?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
}

interface PatientRead extends PatientCreate {
  id: string;
  doctor_id: string;
  created_at: string;
  updated_at: string;
}

// src/types/appointment.ts
type AppointmentStatus = 
  | 'scheduled' 
  | 'checked_in' 
  | 'in_progress' 
  | 'completed' 
  | 'cancelled' 
  | 'no_show';

interface AppointmentCreate {
  patient_id: string;
  appointment_date: string; // ISO datetime string
  reason?: string;
  notes?: string;
}

interface AppointmentRead extends AppointmentCreate {
  id: string;
  doctor_id: string;
  status: AppointmentStatus;
  created_at: string;
  updated_at: string;
}
```

> **Important:** Refer to `FRONTEND_API_CONTRACT.md` for the complete and authoritative list of all request/response schemas. The types above are examples to establish the pattern — you must define types for ALL schemas documented in the contract.

---

## 12. Checklist Before Submitting

Before considering the frontend complete, verify every item:

- [ ] **Authentication works** — Login, token storage, auto-redirect on 401, logout
- [ ] **All API calls go through service modules** — No direct fetch/axios in components
- [ ] **Login uses form-data** — Not JSON
- [ ] **File upload uses multipart/form-data** — Field name is "file"
- [ ] **403 errors show patient-appointment message** — Not generic "Access Denied"
- [ ] **All AI content is labeled** — Badge on every RAG answer, chat response, and summary
- [ ] **Citations are displayed and clickable** — Not stripped or hidden
- [ ] **Clinical disclaimer shown** — On AI-generated content
- [ ] **No edit patient form** — Backend endpoint doesn't exist
- [ ] **No appointments list page** — Backend endpoint doesn't exist
- [ ] **No delete functionality** — Backend endpoints don't exist
- [ ] **No registration page** — Backend endpoint doesn't exist
- [ ] **Every list has an empty state** — With descriptive text and action
- [ ] **Every API call has loading state** — Skeletons or spinners
- [ ] **Every API call has error state** — Meaningful error messages
- [ ] **Medical values are not truncated** — Lab results, dosages displayed exactly
- [ ] **Responsive on desktop and tablet** — Tested at 1280px, 1024px, 768px
- [ ] **Accessible** — ARIA labels, keyboard navigation, focus management
- [ ] **No hardcoded secrets** — API URL from environment variable, no secrets in code
- [ ] **TypeScript strict mode** — No `any` types, all interfaces defined

---

*This prompt, combined with `PROJECT_FRONTEND_HANDOFF.md` and `FRONTEND_API_CONTRACT.md`, gives you everything you need to build the complete DoctorOS-AI frontend. Begin with Phase 1 and progress sequentially. Ask for clarification only if the documentation is ambiguous — it should cover all cases.*
