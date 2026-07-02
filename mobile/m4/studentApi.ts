export interface StudentApiArgs {
  apiBaseUrl: string;
  accessToken: string;
  timeoutMs?: number;
}

export interface ElectricityLaunchPath {
  classId: string;
  examId: string;
  subjectId: string;
  chapterId: string;
  conceptEntryId: string;
}

export interface StartSessionArgs extends StudentApiArgs {
  launchPath: ElectricityLaunchPath;
}

export interface StartedSession {
  sessionId: string;
}

interface ClassRow {
  class_id: string;
  label: string;
}

interface ExamRow {
  exam_id: string;
  label: string;
}

interface SubjectRow {
  subject_id: string;
  label: string;
}

interface ChapterRow {
  chapter_id: string;
  title: string;
}

interface ConceptEntryRow {
  concept_entry_id: string;
  label: string;
}

export async function loadElectricityLaunchPath(
  args: StudentApiArgs,
): Promise<ElectricityLaunchPath> {
  const classRows = await getJson<{ classes: ClassRow[] }>(
    args,
    '/v1/student/curriculum/classes',
  );
  const classId = requireMatch(classRows.classes, (row) => row.label === 'Class 10').class_id;

  const examRows = await getJson<{ exams: ExamRow[] }>(
    args,
    `/v1/student/curriculum/exams?class_id=${encodeURIComponent(classId)}`,
  );
  const examId = requireMatch(examRows.exams, (row) => row.label === 'CBSE').exam_id;

  const subjectRows = await getJson<{ subjects: SubjectRow[] }>(
    args,
    `/v1/student/curriculum/subjects?class_id=${encodeURIComponent(classId)}&exam_id=${encodeURIComponent(examId)}`,
  );
  const subjectId = requireMatch(subjectRows.subjects, (row) => row.label === 'Science').subject_id;

  const chapterRows = await getJson<{ chapters: ChapterRow[] }>(
    args,
    `/v1/student/curriculum/chapters?class_id=${encodeURIComponent(classId)}&exam_id=${encodeURIComponent(examId)}&subject_id=${encodeURIComponent(subjectId)}`,
  );
  const chapterId = requireMatch(
    chapterRows.chapters,
    (row) => row.title === 'Electricity',
  ).chapter_id;

  const conceptRows = await getJson<{ concept_entries: ConceptEntryRow[] }>(
    args,
    `/v1/student/chapters/${encodeURIComponent(chapterId)}/concept-entries`,
  );
  const conceptEntryId = requireMatch(
    conceptRows.concept_entries,
    (row) => row.label.toLowerCase().includes('electricity'),
  ).concept_entry_id;

  return { classId, examId, subjectId, chapterId, conceptEntryId };
}

export async function startElectricitySession(
  args: StartSessionArgs,
): Promise<StartedSession> {
  const body = await postJson<{ session_id: string }>(args, '/v1/student/sessions', {
    exam_id: args.launchPath.examId,
    subject_id: args.launchPath.subjectId,
    chapter_id: args.launchPath.chapterId,
    concept_entry_id: args.launchPath.conceptEntryId,
  });
  return { sessionId: body.session_id };
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
  body: Record<string, string>,
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

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '');
}
