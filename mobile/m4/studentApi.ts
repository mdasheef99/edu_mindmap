export interface StudentApiArgs {
  apiBaseUrl: string;
  accessToken: string;
  timeoutMs?: number;
}

export interface ElectricityLaunchPath {
  classId: string;
  classLabel: string;
  examId: string;
  examName: string;
  subjectId: string;
  subjectName: string;
  chapterId: string;
  chapterTitle: string;
  conceptEntryId: string;
  conceptTitle: string;
}

export interface StartSessionArgs extends StudentApiArgs {
  launchPath: ElectricityLaunchPath;
  behavioralAnalyticsConsent: boolean;
}

export interface StartedSession {
  sessionId: string;
}

export interface DashboardSession {
  sessionId: string;
  chapterId: string;
  chapterTitle: string;
  lastActiveAt: string;
  status: string;
}

export interface StudentDashboard {
  continueLearning: DashboardSession | null;
  recentSessions: DashboardSession[];
}

export interface BootstrapStudentAuthResult {
  userId: string;
  tenantId: string;
  role: string;
  behavioralAnalyticsConsentGranted: boolean;
}

interface ClassRow {
  class_id?: string;
  class_level_id?: string;
  label: string;
}

interface ExamRow {
  exam_id: string;
  label?: string;
  name?: string;
}

interface SubjectRow {
  subject_id: string;
  label?: string;
  name?: string;
}

interface ChapterRow {
  chapter_id: string;
  title: string;
}

interface ConceptEntryRow {
  concept_entry_id: string;
  label?: string;
  title?: string;
}

export async function bootstrapStudentAuth(args: StudentApiArgs): Promise<BootstrapStudentAuthResult> {
  const body = await postJson<{
    user_id: string;
    tenant_id: string;
    role: string;
    behavioral_analytics_consent_granted: boolean;
  }>(args, '/v1/student/auth/bootstrap', {});
  return {
    userId: body.user_id,
    tenantId: body.tenant_id,
    role: body.role,
    behavioralAnalyticsConsentGranted: body.behavioral_analytics_consent_granted,
  };
}

export async function loadElectricityLaunchPath(args: StudentApiArgs): Promise<ElectricityLaunchPath> {
  const classRows = await getJson<{ items?: ClassRow[]; classes?: ClassRow[] }>(
    args,
    '/v1/student/curriculum/classes',
  );
  const classRow = requireMatch(listFrom(classRows, 'classes'), (row) => row.label === 'Class 10');
  const classId = classRow.class_id ?? requireId(
      classRow.class_level_id,
      'Class 10',
    );

  const examRows = await getJson<{ items?: ExamRow[]; exams?: ExamRow[] }>(
    args,
    `/v1/student/curriculum/exams?class_id=${encodeURIComponent(classId)}`,
  );
  const examRow = requireMatch(listFrom(examRows, 'exams'), (row) => displayName(row) === 'CBSE');
  const examId = examRow.exam_id;

  const subjectRows = await getJson<{ items?: SubjectRow[]; subjects?: SubjectRow[] }>(
    args,
    `/v1/student/curriculum/subjects?class_id=${encodeURIComponent(classId)}&exam_id=${encodeURIComponent(examId)}`,
  );
  const subjectRow = requireMatch(
    listFrom(subjectRows, 'subjects'),
    (row) => displayName(row) === 'Science',
  );
  const subjectId = subjectRow.subject_id;

  const chapterRows = await getJson<{ items?: ChapterRow[]; chapters?: ChapterRow[] }>(
    args,
    `/v1/student/curriculum/chapters?class_id=${encodeURIComponent(classId)}&exam_id=${encodeURIComponent(examId)}&subject_id=${encodeURIComponent(subjectId)}`,
  );
  const chapterRow = requireMatch(
    listFrom(chapterRows, 'chapters'),
    (row) => row.title === 'Electricity',
  );
  const chapterId = chapterRow.chapter_id;

  const conceptRows = await getJson<{ items?: ConceptEntryRow[]; concept_entries?: ConceptEntryRow[] }>(
    args,
    `/v1/student/chapters/${encodeURIComponent(chapterId)}/concept-entries`,
  );
  const conceptRow = requireMatch(
    listFrom(conceptRows, 'concept_entries'),
    (row) => displayName(row).toLowerCase().includes('electricity'),
  );
  const conceptEntryId = conceptRow.concept_entry_id;

  return {
    classId,
    classLabel: classRow.label,
    examId,
    examName: displayName(examRow),
    subjectId,
    subjectName: displayName(subjectRow),
    chapterId,
    chapterTitle: chapterRow.title,
    conceptEntryId,
    conceptTitle: displayName(conceptRow),
  };
}

export async function startElectricitySession(
  args: StartSessionArgs,
): Promise<StartedSession> {
  const body = await postJson<{ session_id: string }>(args, '/v1/student/sessions', {
    exam_id: args.launchPath.examId,
    subject_id: args.launchPath.subjectId,
    chapter_id: args.launchPath.chapterId,
    concept_entry_id: args.launchPath.conceptEntryId,
    behavioral_analytics_consent: args.behavioralAnalyticsConsent,
  });
  return { sessionId: body.session_id };
}

export async function loadStudentDashboard(args: StudentApiArgs): Promise<StudentDashboard> {
  const body = await getJson<{
    continue_learning?: DashboardSessionRow | null;
    recent_sessions?: DashboardSessionRow[];
  }>(args, '/v1/student/dashboard');
  return {
    continueLearning: body.continue_learning ? mapDashboardSession(body.continue_learning) : null,
    recentSessions: (body.recent_sessions ?? []).map(mapDashboardSession),
  };
}

export async function resumeStudentSession(
  args: StudentApiArgs & { sessionId: string },
): Promise<StartedSession> {
  const body = await postJson<{ session_id: string }>(
    args,
    `/v1/student/sessions/${encodeURIComponent(args.sessionId)}/resume`,
    {},
  );
  return { sessionId: body.session_id };
}

interface DashboardSessionRow {
  session_id: string;
  chapter_id: string;
  chapter_title: string;
  last_active_at: string;
  status: string;
}

function mapDashboardSession(row: DashboardSessionRow): DashboardSession {
  return {
    sessionId: row.session_id,
    chapterId: row.chapter_id,
    chapterTitle: row.chapter_title,
    lastActiveAt: row.last_active_at,
    status: row.status,
  };
}

async function getJson<T>(args: StudentApiArgs, path: string): Promise<T> {
  const response = await fetchWithTimeout(args, path, {
    method: 'GET',
    headers: authHeaders(args.accessToken),
  });
  return parseJson<T>(response);
}

async function postJson<T>(
  args: StudentApiArgs,
  path: string,
  body: Record<string, unknown>,
): Promise<T> {
  const response = await fetchWithTimeout(args, path, {
    method: 'POST',
    headers: authHeaders(args.accessToken),
    body: JSON.stringify(body),
  });
  return parseJson<T>(response);
}

async function parseJson<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(`Student API failed: ${response.status}${errorDetail(body)}`);
  }
  return body as T;
}

async function fetchWithTimeout(
  args: StudentApiArgs,
  path: string,
  init: RequestInit,
): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), args.timeoutMs ?? 15000);
  try {
    return await fetch(`${trimTrailingSlash(args.apiBaseUrl)}${path}`, {
      ...init,
      signal: controller.signal,
    });
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Student API request timed out');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

function errorDetail(body: unknown): string {
  if (!body || typeof body !== 'object') return '';
  const detail = (body as { detail?: unknown; message?: unknown }).detail
    ?? (body as { message?: unknown }).message;
  if (typeof detail === 'string' && detail.trim()) return `: ${detail}`;
  return '';
}

function authHeaders(accessToken: string): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${accessToken}`,
  };
}

function requireMatch<T>(rows: T[], predicate: (row: T) => boolean): T {
  const match = rows.find(predicate);
  if (!match) {
    throw new Error('Required M4 Electricity launch path row was not found');
  }
  return match;
}

function listFrom<T>(body: { items?: T[] } & Record<string, unknown>, key: string): T[] {
  const named = body[key];
  if (Array.isArray(named)) return named as T[];
  return body.items ?? [];
}

function displayName(row: { label?: string; name?: string; title?: string }): string {
  return row.label ?? row.name ?? row.title ?? '';
}

function requireId(value: string | undefined, label: string): string {
  if (!value) {
    throw new Error(`Required M4 Electricity launch path ID was not found for ${label}`);
  }
  return value;
}

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '');
}
