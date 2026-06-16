# Mobile Features: System-Level Features

## Document Overview

This document specifies system-level functionality for the mobile application, including authentication, data sync, broader offline continuity references, notifications, settings, export/import, performance optimization, and privacy compliance.

**Part of**: Mobile Feature Specification (split for AI agent optimization)
**Related files**:
- [Core UI Components](mobile-features-core-ui.md) - Curriculum, nodes, canvas, panels, navigation
- [AI Integration Features](mobile-features-ai-integration.md) - AI-powered capabilities
- [Enhancements & Summaries](mobile-features-enhancements.md) - Feature priorities and recommendations
- [Master Index](mobile-features-index.md) - Complete navigation guide

**Priority / tier labels (non-binding)**:
Treat all priority labels as **capability tiers**, not timeline commitments.

- **Basic**: Essential for the first usable release of the mobile app.
- **Advanced**: Enhancement features beyond the core experience.
- **Teacher**: Teacher/admin-only capabilities (not student-facing).
- **Exclude**: Not suitable for mobile or deferred indefinitely.

**Design Principles**:
- **Organic-First**: Students explore naturally; system observes invisibly
- **Syllabus-Driven**: All content anchored to curriculum (Class, Exam, Subject, Chapter)
- **Curiosity-Driven**: Exploration guided by student interest, not forced paths
- **Category Invisibility**: Internal analytic categories never visible to students

---

## 7. System-Level Features

App-wide functionality that operates across all screens.

### 7.1 Authentication

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Mobile number login | Login screen | Basic | OTP-based verification (SMS/WhatsApp) | Auth service, SMS gateway |
| Mobile number signup | Signup screen | Basic | Mobile number + OTP verification | Auth service, SMS gateway |
| Social login (Google) | Login screen → "Continue with Google" | Advanced | OAuth flow | Auth service, Google |
| Social login (Apple) | Login screen → "Continue with Apple" | Advanced | Sign in with Apple (iOS required) | Auth service, Apple |
| Account recovery | Login screen → "Can't access account?" | Basic | OTP to registered mobile number | Auth service, SMS gateway |
| Logout | Settings → "Log Out" | Basic | Clears local session | Auth service |
| Session persistence | Automatic | Basic | Stays logged in across app restarts | Secure storage |
| Biometric unlock | Settings → "Security" | Advanced | Face ID / Fingerprint | Biometric hardware |

### 7.2 Data Sync

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Auto-sync on change | Automatic | Basic | Syncs after each edit (debounced) | Network, authentication |
| Sync status indicator | Header → cloud icon | Basic | Shows syncing/synced/offline | Network |
| Manual sync trigger | Pull-to-refresh | Basic | Forces sync check | Network, authentication |
| Conflict resolution | N/A | Exclude for MVP | No offline concurrent editing or queued writes in current scope | N/A |
| Sync history | Settings → "Sync" → "History" | Advanced | Shows recent sync events | Sync service |

### 7.3 Basic Offline Access

*Current MVP scope includes only basic offline access to previously stored session/board state and content already generated online so learners can reopen and resume later. Broader offline capability remains later-phase only and should not be read into this section. This section explicitly excludes offline editing, queued sync, conflict resolution, explicit offline downloads, offline video behavior, podcast offline playback, and AI generation without network. Offline review events such as dwell/revisit are not buffered in MVP and should be treated as an accepted analytics blind spot unless a later minimal event buffer is specified.*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Basic offline data access | Automatic | Basic | Previously stored session/board content can be reopened locally | Local storage |
| Offline editing | N/A | Exclude | Not part of the current clarified scope | N/A |
| Offline indicator | Header → offline badge | Advanced | Shows when no network connection while viewing previously stored content | Network detection |
| Sync queue | N/A | Exclude | Not part of the current clarified scope | N/A |
| Selective offline boards | N/A | Exclude | Explicit offline-download behavior is not currently established | N/A |
| Offline AI (limited) | N/A | Exclude | Requires network for AI features | N/A |

### 7.4 Notifications

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Push notifications | System notifications | Advanced | Learning reminders, streak alerts | Notification service |
| Quiz reminders | Notification → "Time to quiz!" | Advanced | Configurable timing | Quiz system |
| Learning streak alerts | Notification → streak status | Advanced | Daily engagement prompts | Analytics |
| In-app notifications | Notification center (bottom sheet) | Advanced | Activity feed | Notification service |
| Notification preferences | Settings → "Notifications" | Advanced | Enable/disable by type | Settings |

### 7.5 Settings and Preferences

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Dark mode | Settings → "Appearance" | Basic | System/Light/Dark toggle | None |
| Text size | Settings → "Accessibility" | Advanced | Small/Medium/Large/XL | None |
| Haptic feedback | Settings → "Haptics" | Advanced | Enable/disable touch feedback | Haptic hardware |
| Auto-save interval | Settings → "Editor" | Exclude | Always auto-save on mobile | None |
| Default node type | Settings → "Editor" | Advanced | Sets FAB default action | None |
| Clear cache | Settings → "Storage" → "Clear Cache" | Basic | Frees local storage | None |

### 7.6 Export and Import

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Export board as image | Board menu → "Export" → "Image" | Advanced | PNG/JPG to device gallery | File system |
| Export board as PDF | Board menu → "Export" → "PDF" | Advanced | PDF generation | File system |
| Share board link | Board menu → "Share" | Advanced | Generates shareable URL | Share service |
| Import board | N/A | Exclude | Use web for complex imports | N/A |
| Export all data | Settings → "Data" → "Export" | Advanced | Full data backup | File system |

### 7.7 Performance and Optimization

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Lazy loading | Automatic | Basic | Loads nodes as they enter viewport | None |
| Image compression | Automatic | Basic | Compresses images for mobile | None |
| Content caching | Automatic | Basic | Caches frequently accessed content | Local storage |
| Background sync | Automatic | Advanced | Syncs when app is backgrounded | Background tasks |
| Memory management | Automatic | Basic | Unloads off-screen nodes | None |
| Reduced animations | Settings → "Accessibility" → "Reduce Motion" | Advanced | Disables non-essential animations | None |


#### 7.7.1 Minimum Device Target Specifications

*Based on Indian student device market research (see `docs/research/indian-student-market-analysis.md`)*

| Specification | Minimum Requirement | Rationale |
|---------------|---------------------|-----------|
| **Android Version** | Android 11 (API 30) | ~95% coverage of Indian Android users (Android 11+ = 90%+) |
| **RAM** | 4GB | Entry-level segment floor; budget devices (₹10,000-₹20,000) have 4-6GB |
| **Screen Size** | 6.5" HD+ (720×1600) | Standard for budget smartphones in Indian market |
| **Storage** | 32GB (8GB available) | Minimum for app + locally persisted session data |
| **GPU** | OpenGL ES 3.0 | Required for Skia edge rendering (Bézier curves) in the hybrid architecture |

**Performance Optimization Targets**:
- **Memory budget**: 150MB maximum app footprint (allows headroom on 4GB devices)
- **Viewport culling**: Aggressive culling at node count >30 on low-RAM devices
- **LOD thresholds**: Simplified rendering (rectangles only) below 0.5 zoom on budget devices
- **Texture atlas**: Single 1024×1024 spritesheet for all icons (reduces draw calls)

### 7.8 Privacy and Compliance

*Data protection and regulatory compliance (Basic tier)*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Privacy policy display | Settings → "Privacy" → "Privacy Policy" | Basic | In-app WebView with full policy | None |
| Data collection consent | First launch → consent dialog | Basic | Clear opt-in for data collection | Consent service |
| Parental consent (minors) | Signup → age verification → parent mobile number | Basic | Required for users under 18 via parent OTP | Auth service, SMS gateway |
| Data export request | Settings → "Privacy" → "Export My Data" | Basic | Generates downloadable data package | Data service |
| Data deletion request | Settings → "Privacy" → "Delete My Data" | Basic | Initiates account and data deletion | Auth service, data service |
| Consent management | Settings → "Privacy" → "Manage Consent" | Basic | Toggle data collection categories | Consent service |
| Data residency indicator | Settings → "Privacy" → "Data Location" | Basic | Shows where data is stored | None |

**Compliance Framework**:

| Regulation | Requirement | Implementation |
|------------|-------------|----------------|
| **DPDP Act 2023 (India)** | Data localization for Indian users | Data stored in India-region servers for Indian users |
| **DPDP Act 2023 (India)** | Consent before data processing | Backend consent records gate processing by consent kind |
| **DPDP Act 2023 (India)** | Behavioral analytics consent for minors | Teacher-support analytics are built only when active guardian consent exists |
| **DPDP Act 2023 (India)** | Right to erasure | Request routed to backend compliance workflow; tenancy-table PII and pseudonymous event handling follow legal policy |
| **DPDP Act 2023 (India)** | Parental consent for minors | Verified parental/guardian consent via parent OTP or approved signed-form reference |
| **DPDP Act 2023 (India)** | Data breach notification | In-app and SMS notification within 72 hours |
| **General** | Data minimization | Collect only data necessary for learning features |
| **General** | Purpose limitation | Data used only for stated educational purposes |

**Backend consent-gated analytics model**:
- Consent is stored as a backend entity, not as a mobile-only checkbox.
- Data-processing consent and behavioral-analytics consent are distinct.
- Students without active behavioral-analytics consent may still use the student product, but classification/projection workers skip them and teacher views render consent-pending/withdrawn states.
- Consent withdrawal stops future analytic inclusion and requires projection rebuild/replay without the withdrawn student where applicable.
- Raw PII remains in tenancy/consent tables only; event payloads carry pseudonymous identifiers.
