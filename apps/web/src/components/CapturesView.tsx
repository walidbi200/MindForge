import { useState, useEffect } from "react";

interface Capture {
  id: string;
  content: string;
  source_id: string | null;
  created_at: string;
  updated_at: string;
}

interface AIConceptSuggestion {
  name: string;
  description: string;
  confidence: number;
}

interface AIRelationshipSuggestion {
  from: string;
  to: string;
  type: string;
  confidence: number;
}

interface AIResponse {
  summary: string;
  concepts: AIConceptSuggestion[];
  relationships: AIRelationshipSuggestion[];
  questions: string[];
}

export function CapturesView() {
  const [captures, setCaptures] = useState<Capture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [aiLoading, setAiLoading] = useState<Record<string, boolean>>({});
  const [aiResponses, setAiResponses] = useState<Record<string, AIResponse>>({});

  const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  const fetchCaptures = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${baseUrl}/api/v1/captures?limit=50`);
      if (!res.ok) throw new Error("Failed to fetch captures");
      const data = await res.json();
      setCaptures(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCaptures();
  }, []);

  const handleProcessAI = async (captureId: string) => {
    setAiLoading(prev => ({ ...prev, [captureId]: true }));
    try {
      const res = await fetch(`${baseUrl}/api/v1/ai/analyze-capture/${captureId}`, {
        method: "POST",
      });
      
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to process capture with AI");
      }
      
      const data: AIResponse = await res.json();
      setAiResponses(prev => ({ ...prev, [captureId]: data }));
    } catch (err: any) {
      alert(`AI Error: ${err.message}`);
    } finally {
      setAiLoading(prev => ({ ...prev, [captureId]: false }));
    }
  };

  // Simple Create form
  const [content, setContent] = useState("");
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${baseUrl}/api/v1/captures`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      });
      if (!res.ok) throw new Error("Failed to create capture");
      setContent("");
      fetchCaptures();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Captures</h1>
        <p className="text-muted-foreground mt-2">
          Raw evidence, notes, and observations. Process with AI to extract structured knowledge.
        </p>
      </div>

      <div className="rounded-lg border bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">New Capture</h3>
        <form onSubmit={handleCreate} className="space-y-4">
          <textarea
            value={content}
            onChange={e => setContent(e.target.value)}
            className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[100px]"
            placeholder="Type your raw notes or paste text here..."
            required
          />
          <button
            type="submit"
            className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          >
            Save Capture
          </button>
        </form>
      </div>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading captures...</div>
      ) : captures.length === 0 ? (
        <div className="text-center py-12 border border-dashed rounded-lg bg-card/20">
          <p className="text-muted-foreground">No captures found.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {captures.map((capture) => (
            <div key={capture.id} className="rounded-lg border bg-card shadow-sm overflow-hidden">
              <div className="p-6 space-y-4">
                <div className="text-sm font-mono text-muted-foreground truncate">ID: {capture.id}</div>
                <div className="whitespace-pre-wrap">{capture.content}</div>
                
                <div className="pt-4 border-t border-border flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">
                    Created: {new Date(capture.created_at).toLocaleString()}
                  </span>
                  
                  <button
                    onClick={() => handleProcessAI(capture.id)}
                    disabled={aiLoading[capture.id]}
                    className="inline-flex items-center justify-center rounded-md text-sm font-medium border border-primary text-primary hover:bg-primary/10 h-8 px-3 disabled:opacity-50"
                  >
                    {aiLoading[capture.id] ? "Processing..." : "✨ Process with AI"}
                  </button>
                </div>
              </div>

              {/* AI Preview Section */}
              {aiResponses[capture.id] && (
                <div className="bg-primary/5 border-t border-primary/20 p-6 space-y-6">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-lg flex items-center gap-2">
                      <span className="text-xl">✨</span> AI Analysis Preview
                    </h4>
                    <span className="text-xs bg-amber-500/20 text-amber-600 dark:text-amber-400 px-2 py-1 rounded border border-amber-500/30 font-medium">
                      NOT SAVED YET
                    </span>
                  </div>

                  {/* Summary */}
                  <div className="space-y-2">
                    <h5 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Summary</h5>
                    <p className="text-sm">{aiResponses[capture.id].summary}</p>
                  </div>

                  {/* Concepts */}
                  {aiResponses[capture.id].concepts.length > 0 && (
                    <div className="space-y-3">
                      <h5 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Suggested Concepts</h5>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {aiResponses[capture.id].concepts.map((concept, i) => (
                          <div key={i} className="bg-background border rounded p-3 relative">
                            <div className="absolute top-2 right-2 text-[10px] bg-muted px-1.5 py-0.5 rounded">
                              {(concept.confidence * 100).toFixed(0)}%
                            </div>
                            <h6 className="font-semibold text-sm">{concept.name}</h6>
                            <p className="text-xs text-muted-foreground mt-1">{concept.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Relationships */}
                  {aiResponses[capture.id].relationships.length > 0 && (
                    <div className="space-y-3">
                      <h5 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Suggested Relationships</h5>
                      <div className="flex flex-col gap-2">
                        {aiResponses[capture.id].relationships.map((rel, i) => (
                          <div key={i} className="flex items-center gap-3 text-sm bg-background border rounded p-2">
                            <span className="font-medium text-foreground">{rel.from}</span>
                            <span className="text-[10px] uppercase bg-muted text-muted-foreground px-2 py-0.5 rounded border border-border">
                              {rel.type}
                            </span>
                            <span className="font-medium text-foreground">{rel.to}</span>
                            <span className="ml-auto text-[10px] text-muted-foreground">
                              {(rel.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Questions */}
                  {aiResponses[capture.id].questions.length > 0 && (
                    <div className="space-y-2">
                      <h5 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Review Questions</h5>
                      <ul className="list-disc list-inside text-sm space-y-1 pl-1">
                        {aiResponses[capture.id].questions.map((q, i) => (
                          <li key={i} className="text-muted-foreground">{q}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
