import React, { useMemo, useState } from "react";
import { Button, Modal, ScrollView, Text, TextInput, View } from "react-native";

type PhraseOption = {
  option_id: string;
  text: string;
  rank_position: number;
  action_type: "elaborate" | "custom" | "recommended";
};

type PhraseOfferSet = {
  offer_set_id: string;
  session_id: string;
  source_node_id: string;
  thread_context_id: string;
  selected_phrase: string;
  actions: PhraseOption[];
  recommended_questions: PhraseOption[];
};

type ReaderNode = {
  sessionId: string;
  nodeId: string;
  threadContextId: string;
  content: string;
};

type Props = {
  visible: boolean;
  apiBaseUrl: string;
  node: ReaderNode;
  authorizationToken?: string;
  onClose: () => void;
  onBranchCreated?: (childNodeId: string) => void;
};

export function PhraseSelectionReaderSheet({
  visible,
  apiBaseUrl,
  node,
  authorizationToken,
  onClose,
  onBranchCreated,
}: Props) {
  const [selection, setSelection] = useState({ start: 0, end: 0 });
  const [offerSet, setOfferSet] = useState<PhraseOfferSet | null>(null);
  const [status, setStatus] = useState("select a phrase");
  const selectedPhrase = useMemo(
    () => node.content.slice(selection.start, selection.end).trim(),
    [node.content, selection],
  );
  const sentences = useMemo(() => {
    const parts: { text: string; start: number; end: number }[] = [];
    let cursor = 0;
    for (const raw of node.content.split("\n\n")) {
      const start = node.content.indexOf(raw, cursor);
      const end = start + raw.length;
      parts.push({ text: raw.trim(), start, end });
      cursor = end;
    }
    return parts;
  }, [node.content]);

  async function requestPhraseOptions() {
    if (!selectedPhrase) return;
    setStatus("loading phrase options");
    try {
      const response = await fetch(`${apiBaseUrl}/v1/student/offer-sets/phrase`, {
        method: "POST",
        headers: headers(authorizationToken),
        body: JSON.stringify({
          session_id: node.sessionId,
          source_node_id: node.nodeId,
          thread_context_id: node.threadContextId,
          selected_phrase: selectedPhrase,
          source_excerpt: node.content,
          selection_start: selection.start,
          selection_end: selection.end,
        }),
      });
      if (response.ok) {
        setOfferSet(await response.json());
        setStatus("choose an action");
      } else {
        setStatus("phrase options failed");
      }
    } catch {
      setStatus("phrase options failed");
    }
  }

  async function chooseOption(option: PhraseOption) {
    if (!offerSet) return;
    setStatus("creating branch");
    try {
      const response = await fetch(
        `${apiBaseUrl}/v1/student/offer-sets/${offerSet.offer_set_id}/choices`,
        {
          method: "POST",
          headers: headers(authorizationToken),
          body: JSON.stringify({
            session_id: offerSet.session_id,
            source_node_id: offerSet.source_node_id,
            outcome: "selected",
            selected_option_id: option.option_id,
            selected_option_text: option.text,
            thread_context_id: offerSet.thread_context_id,
          }),
        },
      );
      if (response.ok) {
        const body = await response.json();
        setStatus("branch created");
        if (body.child_node_id) onBranchCreated?.(body.child_node_id);
      } else {
        setStatus("branch failed");
      }
    } catch {
      setStatus("branch failed");
    }
  }

  async function dismissOfferSet() {
    if (offerSet) {
      try {
        await fetch(`${apiBaseUrl}/v1/student/offer-sets/${offerSet.offer_set_id}/choices`, {
          method: "POST",
          headers: headers(authorizationToken),
          body: JSON.stringify({
            session_id: offerSet.session_id,
            source_node_id: offerSet.source_node_id,
            outcome: "dismissed",
            thread_context_id: offerSet.thread_context_id,
          }),
        });
      } catch {
        // Network failure must not prevent the modal from closing.
      }
    }
    setOfferSet(null);
    onClose();
  }

  return (
    <Modal animationType="slide" visible={visible} onRequestClose={dismissOfferSet}>
      <ScrollView style={{ padding: 20 }}>
        <Text>Reader</Text>
        <Text>Status: {status}</Text>
        <TextInput
          testID="passage-input"
          multiline
          showSoftInputOnFocus={false}
          contextMenuHidden={false}
          maxLength={node.content.length}
          value={node.content}
          onSelectionChange={(event) => setSelection(event.nativeEvent.selection)}
          style={{ minHeight: 180, padding: 12 }}
        />
        <Text>Quick select a sentence:</Text>
        {sentences.map((sentence) => (
          <Button
            key={sentence.start}
            title={sentence.text}
            onPress={() => setSelection({ start: sentence.start, end: sentence.end })}
          />
        ))}
        <Text>Selected: {selectedPhrase || "none"}</Text>
        <Button title="Use selected phrase" onPress={requestPhraseOptions} />
        {offerSet ? (
          <View>
            <Text>Actions for “{offerSet.selected_phrase}”</Text>
            {[...offerSet.actions, ...offerSet.recommended_questions].map((option) => (
              <Button key={option.option_id} title={option.text} onPress={() => chooseOption(option)} />
            ))}
          </View>
        ) : null}
        <Button title="Close" onPress={dismissOfferSet} />
      </ScrollView>
    </Modal>
  );
}

function headers(authorizationToken?: string) {
  return {
    "Content-Type": "application/json",
    ...(authorizationToken ? { Authorization: `Bearer ${authorizationToken}` } : {}),
  };
}