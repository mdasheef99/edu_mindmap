# Mobile Features: System-Level Features

## Document Overview

This document specifies system-level functionality for the mobile application, including authentication, data sync, offline mode, notifications, settings, export/import, performance optimization, and privacy compliance.

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
- **Category Invisibility**: Kantian diagnostic categories never visible to students

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
| Conflict resolution | Sync dialog | Advanced | Shows conflicting changes, pick version | Sync service |
| Sync history | Settings → "Sync" → "History" | Advanced | Shows recent sync events | Sync service |

### 7.3 Offline Mode

*Offline capabilities are Basic tier priority based on Indian student device market research (see `docs/research/indian-student-market-analysis.md`). Rural connectivity gaps (58.8% mobile penetration vs. 125.3% urban) and competitor offline offerings (Khan Academy, BYJU's) make offline mode essential for target market.*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Offline data access | Automatic | Basic | Cached boards available offline | Local storage |
| Offline editing | Automatic | Basic | Edits queued for sync when online | Local storage |
| Offline indicator | Header → offline badge | Basic | Shows when no network connection | Network detection |
| Sync queue | Settings → "Offline" → "Pending" | Advanced | Shows queued changes with sync status | Local storage |
| Selective offline boards | Board menu → "Available Offline" | Advanced | Downloads full board for offline use | Local storage |
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
| **Storage** | 32GB (8GB available) | Minimum for app + offline cached boards |
| **GPU** | OpenGL ES 3.0 | Required for React Native Skia rendering |

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
| **DPDP Act 2023 (India)** | Consent before data processing | Explicit opt-in consent dialog on first launch |
| **DPDP Act 2023 (India)** | Right to erasure | "Delete My Data" feature with 72-hour processing |
| **DPDP Act 2023 (India)** | Parental consent for minors | Verified parental consent for users under 18 |
| **DPDP Act 2023 (India)** | Data breach notification | In-app and SMS notification within 72 hours |
| **General** | Data minimization | Collect only data necessary for learning features |
| **General** | Purpose limitation | Data used only for stated educational purposes |

**Data Retention Policy**:
- Active account data: Retained while account is active
- Exploration session data: 2 years for learning analytics
- Deleted account data: Purged within 30 days of deletion request
- Anonymous aggregate data: Retained indefinitely for platform improvement
