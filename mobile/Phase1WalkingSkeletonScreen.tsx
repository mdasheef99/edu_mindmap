import React, { useState } from "react";
import { Button, SafeAreaView, Text, View } from "react-native";

type StudentSession = {
  session_id: string;
  status: string;
};

export function Phase1WalkingSkeletonScreen({ apiBaseUrl }: { apiBaseUrl: string }) {
  const [session, setSession] = useState<StudentSession | null>(null);
  const [status, setStatus] = useState("ready");

  async function startSession() {
    setStatus("starting");
    const response = await fetch(`${apiBaseUrl}/v1/student/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        exam_id: "00000000-0000-4000-8000-000000000001",
        subject_id: "00000000-0000-4000-8000-000000000002",
        chapter_id: "00000000-0000-4000-8000-000000000003",
        concept_entry_id: "00000000-0000-4000-8000-000000000004",
        chapter_analysis_id: "00000000-0000-4000-8000-000000000005",
      }),
    });
    const body = await response.json();
    setSession(body);
    setStatus(response.ok ? "session started" : "failed");
  }

  return (
    <SafeAreaView>
      <View style={{ padding: 24, gap: 12 }}>
        <Text>Phase 1 Walking Skeleton</Text>
        <Text>Status: {status}</Text>
        <Text>Session: {session?.session_id ?? "none"}</Text>
        <Button title="Start test session" onPress={startSession} />
      </View>
    </SafeAreaView>
  );
}