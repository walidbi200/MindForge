import { useState, useEffect, useRef } from "react";

// Interfaces
interface WorkspaceSummary {
  due_reviews: any[];
  recent_captures: any[];
  pinned_spaces: any[];
  recent_sources: any[];
  activity: any[];
  graph_preview: any[];
  recent_concepts: any[];
  recent_collections: any[];
  pending_proposals: PendingProposal[];
  continue_learning: ContinueLearning | null;
  reading_queue: ReadingQueueItem[];
  daily_stats: DailyStats;
}

interface PendingProposal {
  capture_id: string;
  content: string;
  proposal: AIAnalysis;
}

interface ContinueLearning {
  last_concept: { id: string; title: string; type: string } | null;
  last_collection: { id: string; title: string; type: string } | null;
  last_review: { id: string; title: string; type: string; entity_id: string } | null;
  time_since_last_interaction: string | null;
}

interface ReadingQueueItem {
  id: string;
  type: string;
  title: string;
  reason: string;
  priority: number;
}

interface DailyStats {
  captures_today: number;
  reviews_completed_today: number;
  concepts_today: number;
  pending_proposals: number;
  goal_progress: number;
}

interface SearchResult {
  id: string;
  type: string;
  title: string;
  snippet: string;
}

interface AIConceptSuggestion {
  name: string;
  description: string;
  confidence: number;
}

interface AIRelationshipSuggestion {
  from_entity: string;
  to_entity: string;
  relationship_type: string;
  confidence: number;
}

interface AIAnalysis {
  summary: string;
  concepts: AIConceptSuggestion[];
  relationships: AIRelationshipSuggestion[];
  collections: string[];
  review_suggestion: string | null;
}

export function DailyWorkspace({ onNavigateToEntity }: { onNavigateToEntity?: (id: string) => void }) {
  const [summary, setSummary] = useState<WorkspaceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const [captureContent, setCaptureContent] = useState("");
  const [captureLoading, setCaptureLoading] = useState(false);
  const captureInputRef = useRef<HTMLTextAreaElement>(null);

  const [selectedCaptureId, setSelectedCaptureId] = useState<string | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiApplying, setAiApplying] = useState(false);
  
  const [successMessage, setSuccessMessage] = useState("");

  const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  const fetchWorkspace = async () => {
    try {
      const res = await fetch(`${baseUrl}/api/v1/workspace`);
      if (!res.ok) throw new Error("Failed to fetch workspace");
      const data = await res.json();
      setSummary(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkspace();
    if (captureInputRef.current) {
      captureInputRef.current.focus();
    }
  }, []);

  // Global Keybindings
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen(true);
      }
      if (e.key === 'Escape' && isSearchOpen) {
        setIsSearchOpen(false);
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, [isSearchOpen]);

  useEffect(() => {
    if (isSearchOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isSearchOpen]);

  const showToast = (msg: string) => {
    setSuccessMessage(msg);
    setTimeout(() => setSuccessMessage(""), 6000);
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }
    setSearchLoading(true);
    try {
      const res = await fetch(`${baseUrl}/api/v1/workspace/search?q=${encodeURIComponent(searchQuery)}`);
      if (!res.ok) throw new Error("Search failed");
      const data = await res.json();
      setSearchResults(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleProcessCapture = async (e?: React.FormEvent | React.KeyboardEvent) => {
    if (e) e.preventDefault();
    if (!captureContent.trim()) return;
    
    setCaptureLoading(true);
    setAiLoading(true);
    setError("");
    
    try {
      const res = await fetch(`${baseUrl}/api/v1/workspace/process-capture`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: captureContent }),
      });
      if (!res.ok) throw new Error("Failed to process capture");
      const data = await res.json();
      setCaptureContent(""); // Clear input
      setSelectedCaptureId(data.capture_id);
      setAiAnalysis(data.proposal);
    } catch (err: any) {
      alert(err.message);
      setAiLoading(false);
    } finally {
      setCaptureLoading(false);
      setAiLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleProcessCapture(e);
    }
  };

  const handleCompleteReview = async (reviewId: string) => {
    try {
      await fetch(`${baseUrl}/api/v1/reviews/${reviewId}/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ metadata_json: "{}" }),
      });
      showToast("✓ Review completed");
      fetchWorkspace();
    } catch (err) {
      console.error(err);
    }
  };

  const handleApplyAI = async () => {
    if (!selectedCaptureId || !aiAnalysis) return;
    setAiApplying(true);
    try {
      const res = await fetch(`${baseUrl}/api/v1/workspace/apply-proposal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          capture_id: selectedCaptureId,
          proposal: aiAnalysis
        }),
      });
      if (!res.ok) throw new Error("Failed to apply AI analysis");
      
      const conceptsCount = aiAnalysis.concepts.length;
      
      showToast(`✓ Capture organized\n${conceptsCount} Concepts created & mapped`);
      
      setAiAnalysis(null);
      setSelectedCaptureId(null);
      fetchWorkspace();
    } catch (err: any) {
      console.error(err);
      alert(err.message);
    } finally {
      setAiApplying(false);
    }
  };

  const openProposal = (proposalCard: PendingProposal) => {
    setSelectedCaptureId(proposalCard.capture_id);
    setAiAnalysis(proposalCard.proposal);
  };

  // Inline Edit Handlers
  const handleUpdateConcept = (idx: number, field: keyof AIConceptSuggestion, val: string) => {
    if (!aiAnalysis) return;
    const newConcepts = [...aiAnalysis.concepts];
    newConcepts[idx] = { ...newConcepts[idx], [field]: val };
    setAiAnalysis({ ...aiAnalysis, concepts: newConcepts });
  };
  const handleRemoveConcept = (idx: number) => {
    if (!aiAnalysis) return;
    const newConcepts = aiAnalysis.concepts.filter((_, i) => i !== idx);
    setAiAnalysis({ ...aiAnalysis, concepts: newConcepts });
  };
  const handleRemoveCollection = (idx: number) => {
    if (!aiAnalysis) return;
    const newCollections = aiAnalysis.collections.filter((_, i) => i !== idx);
    setAiAnalysis({ ...aiAnalysis, collections: newCollections });
  };
  const handleRemoveRelationship = (idx: number) => {
    if (!aiAnalysis) return;
    const newRels = aiAnalysis.relationships.filter((_, i) => i !== idx);
    setAiAnalysis({ ...aiAnalysis, relationships: newRels });
  };
  const handleUpdateReviewSuggestion = (val: string) => {
    if (!aiAnalysis) return;
    setAiAnalysis({ ...aiAnalysis, review_suggestion: val });
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-8 space-y-8 animate-pulse">
        <div className="h-12 bg-muted rounded w-1/3"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="h-24 bg-muted rounded"></div>
          <div className="h-24 bg-muted rounded"></div>
          <div className="h-24 bg-muted rounded"></div>
          <div className="h-24 bg-muted rounded"></div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-96 bg-muted rounded"></div>
          <div className="h-96 bg-muted rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center text-rose-500 max-w-lg mx-auto mt-20">
        <div className="text-4xl mb-4">⚠️</div>
        <h2 className="text-xl font-bold mb-2">Workspace Error</h2>
        <p className="mb-4 text-muted-foreground">{error}</p>
        <button onClick={fetchWorkspace} className="bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium">Retry</button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 pb-12 relative">
      
      {/* Toast Notification */}
      {successMessage && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 bg-green-600 text-white px-6 py-4 rounded-full shadow-2xl z-50 animate-in slide-in-from-top-8 fade-in whitespace-pre-wrap text-center font-medium border border-green-500">
          {successMessage}
        </div>
      )}

      {/* Global Search Overlay */}
      {isSearchOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex justify-center p-4 pt-[10vh]">
          <div className="bg-card border shadow-2xl rounded-xl w-full max-w-2xl flex flex-col h-[60vh] overflow-hidden animate-in fade-in zoom-in-95">
            <div className="p-4 border-b flex items-center gap-3">
              <span className="text-muted-foreground">🔍</span>
              <form onSubmit={handleSearch} className="flex-1">
                <input 
                  ref={searchInputRef}
                  type="text" 
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  placeholder="Search your knowledge base... (Esc to close)"
                  className="w-full bg-transparent border-none focus:outline-none text-lg"
                />
              </form>
            </div>
            <div className="flex-1 overflow-y-auto p-2">
              {searchLoading ? (
                <div className="p-8 text-center text-muted-foreground">Searching...</div>
              ) : searchResults ? (
                searchResults.length === 0 ? (
                  <div className="p-8 text-center text-muted-foreground">No results found for "{searchQuery}"</div>
                ) : (
                  <div className="space-y-1">
                    {searchResults.map(res => (
                      <button key={res.id} onClick={() => onNavigateToEntity && onNavigateToEntity(res.id)} className="w-full text-left p-3 hover:bg-muted rounded-lg flex items-start gap-3 transition-colors">
                        <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-1 bg-primary/10 text-primary rounded mt-0.5">
                          {res.type}
                        </span>
                        <div>
                          <div className="font-medium">{res.title}</div>
                          <div className="text-xs text-muted-foreground mt-1 line-clamp-1">{res.snippet}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                )
              ) : (
                <div className="p-8 flex flex-col items-center justify-center h-full text-muted-foreground space-y-4">
                  <div className="text-4xl">💡</div>
                  <p>Type to search across captures, concepts, sources, and collections.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Header & Welcome */}
      <div className="py-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight mb-2">Good Morning, Walid.</h1>
          <p className="text-lg text-muted-foreground">
            You have <strong className="text-foreground">{summary?.due_reviews.length}</strong> reviews due and <strong className="text-foreground">{summary?.daily_stats.pending_proposals}</strong> AI suggestions waiting.
          </p>
        </div>
        
        {/* Progress Widget */}
        <div className="bg-card border rounded-xl p-4 min-w-[250px] shadow-sm">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Today's Progress</h3>
            <span className="text-sm font-bold text-primary">{summary?.daily_stats.goal_progress}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2.5 overflow-hidden">
            <div 
              className="bg-primary h-2.5 rounded-full transition-all duration-1000 ease-out" 
              style={{ width: `${summary?.daily_stats.goal_progress}%` }}
            ></div>
          </div>
          <p className="text-xs text-muted-foreground mt-3 flex justify-between">
            <span>{summary?.daily_stats.reviews_completed_today} reviews done</span>
            <span>{summary?.daily_stats.captures_today} captured</span>
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative">
        
        {/* LEFT COLUMN: Main Dashboard */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Today's Focus Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 rounded-xl p-4 text-left hover:shadow-md transition-shadow">
              <div className="text-2xl mb-2">📅</div>
              <div className="font-semibold text-amber-900 dark:text-amber-200">Reviews</div>
              <div className="text-sm text-amber-700 dark:text-amber-400">{summary?.due_reviews.length} due today</div>
            </button>
            <button className="bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-900/50 rounded-xl p-4 text-left hover:shadow-md transition-shadow">
              <div className="text-2xl mb-2">✨</div>
              <div className="font-semibold text-indigo-900 dark:text-indigo-200">AI Proposals</div>
              <div className="text-sm text-indigo-700 dark:text-indigo-400">{summary?.daily_stats.pending_proposals} pending</div>
            </button>
            <div className="md:col-span-2 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/50 rounded-xl p-4 text-left">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <div className="text-2xl">📚</div>
                  <div className="font-semibold text-emerald-900 dark:text-emerald-200">Continue Learning</div>
                </div>
                {summary?.continue_learning?.time_since_last_interaction && (
                  <span className="text-xs font-medium text-emerald-700/70 dark:text-emerald-400/70 bg-emerald-100 dark:bg-emerald-900/50 px-2 py-0.5 rounded-full">
                    {summary.continue_learning.time_since_last_interaction}
                  </span>
                )}
              </div>
              <div className="flex gap-2 flex-wrap mt-2">
                {summary?.continue_learning?.last_concept ? (
                  <button onClick={() => onNavigateToEntity && onNavigateToEntity(summary.continue_learning!.last_concept!.id)} className="text-xs bg-emerald-100 hover:bg-emerald-200 dark:bg-emerald-900/60 dark:hover:bg-emerald-800 text-emerald-800 dark:text-emerald-300 px-3 py-1.5 rounded-md transition-colors truncate max-w-[150px]">
                    🧠 {summary.continue_learning.last_concept.title}
                  </button>
                ) : null}
                {summary?.continue_learning?.last_collection ? (
                  <button onClick={() => onNavigateToEntity && onNavigateToEntity(summary.continue_learning!.last_collection!.id)} className="text-xs bg-emerald-100 hover:bg-emerald-200 dark:bg-emerald-900/60 dark:hover:bg-emerald-800 text-emerald-800 dark:text-emerald-300 px-3 py-1.5 rounded-md transition-colors truncate max-w-[150px]">
                    📂 {summary.continue_learning.last_collection.title}
                  </button>
                ) : null}
                {!summary?.continue_learning?.last_concept && !summary?.continue_learning?.last_collection && (
                  <div className="text-sm text-emerald-700/70 dark:text-emerald-400/70">No recent activity</div>
                )}
              </div>
            </div>
          </div>

          {/* Quick Capture */}
          <div className="bg-card border shadow-sm rounded-xl overflow-hidden focus-within:ring-2 focus-within:ring-primary/50 transition-shadow">
            <div className="p-4 border-b bg-muted/30">
              <h2 className="font-semibold flex items-center gap-2">
                <span>⚡</span> Quick Capture
              </h2>
            </div>
            <form onSubmit={handleProcessCapture}>
              <textarea 
                ref={captureInputRef}
                value={captureContent}
                onChange={e => setCaptureContent(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="What's on your mind?&#10;&#10;Drop a thought, paste an article, or capture an idea..."
                className="w-full min-h-[140px] bg-transparent border-none p-5 text-base focus:outline-none resize-none"
                required
              />
              <div className="px-5 py-3 border-t bg-muted/10 flex items-center justify-between">
                <span className="text-xs text-muted-foreground font-medium">
                  {captureContent.length} chars <span className="mx-2 opacity-50">•</span> Ctrl+Enter to process
                </span>
                <button 
                  disabled={captureLoading || !captureContent.trim()} 
                  className="bg-primary text-primary-foreground px-6 py-2 rounded-full text-sm font-bold hover:bg-primary/90 transition-transform active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
                >
                  {captureLoading ? "Processing..." : "Capture & Analyze"}
                </button>
              </div>
            </form>
          </div>

          {/* Pending AI Suggestions Feed */}
          {summary?.pending_proposals && summary.pending_proposals.length > 0 && (
            <div>
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span className="text-indigo-500">✨</span> Pending AI Suggestions
              </h2>
              <div className="space-y-4">
                {summary.pending_proposals.map(p => (
                  <div key={p.capture_id} className="bg-card border border-indigo-100 dark:border-indigo-900/50 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                    <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
                    <div className="flex justify-between items-start gap-4">
                      <div>
                        <h3 className="font-semibold text-lg line-clamp-1 mb-1">{p.proposal.summary}</h3>
                        <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{p.content}</p>
                        <div className="flex gap-2 text-xs">
                          <span className="bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 px-2 py-1 rounded font-medium">
                            {p.proposal.concepts.length} Concepts
                          </span>
                          <span className="bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 px-2 py-1 rounded font-medium">
                            {p.proposal.relationships.length} Relationships
                          </span>
                        </div>
                      </div>
                      <button 
                        onClick={() => openProposal(p)}
                        className="bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-900/30 dark:hover:bg-indigo-900/50 text-indigo-600 dark:text-indigo-300 px-4 py-2 rounded-lg text-sm font-semibold whitespace-nowrap transition-colors"
                      >
                        Review
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Knowledge Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span>🧠</span> Recent Concepts
              </h2>
              <div className="bg-card border rounded-xl shadow-sm overflow-hidden">
                {summary?.recent_concepts && summary.recent_concepts.length > 0 ? (
                  <div className="divide-y">
                    {summary.recent_concepts.map(c => (
                      <div key={c.id} onClick={() => onNavigateToEntity && onNavigateToEntity(c.id)} className="p-4 hover:bg-muted/50 transition-colors cursor-pointer">
                        <div className="font-medium text-sm">{c.title}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center text-muted-foreground text-sm">No concepts yet.</div>
                )}
              </div>
            </div>

            <div>
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span>📚</span> Recent Sources
              </h2>
              <div className="bg-card border rounded-xl shadow-sm overflow-hidden">
                {summary?.recent_sources && summary.recent_sources.length > 0 ? (
                  <div className="divide-y">
                    {summary.recent_sources.map(s => (
                      <div key={s.id} onClick={() => onNavigateToEntity && onNavigateToEntity(s.id)} className="p-4 hover:bg-muted/50 transition-colors cursor-pointer">
                        <div className="font-medium text-sm line-clamp-1">{s.title}</div>
                        <div className="text-[10px] uppercase text-muted-foreground mt-1">{s.source_type}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center text-muted-foreground text-sm">No sources added.</div>
                )}
              </div>
            </div>
          </div>

        </div>

        {/* RIGHT COLUMN: Sidebar (Interactive UI & Reviews) */}
        <div className="space-y-8">
          
          {/* AI Interactive Review Panel */}
          {(aiLoading || selectedCaptureId) && (
            <div className="bg-card border-2 border-indigo-500 rounded-xl shadow-2xl overflow-hidden flex flex-col h-[650px] sticky top-6 animate-in slide-in-from-right-8">
              <div className="p-4 bg-indigo-500 text-white flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xl animate-pulse">✨</span>
                  <h2 className="font-bold">Review Suggestions</h2>
                </div>
                <button onClick={() => {setAiAnalysis(null); setSelectedCaptureId(null);}} className="text-white/80 hover:text-white bg-white/10 hover:bg-white/20 rounded p-1 transition-colors">✕</button>
              </div>
              
              <div className="flex-1 p-5 overflow-y-auto bg-slate-50 dark:bg-slate-900/50">
                {aiLoading ? (
                  <div className="h-full flex flex-col items-center justify-center text-indigo-500 space-y-4">
                    <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-500 rounded-full animate-spin"></div>
                    <p className="font-medium animate-pulse">Synthesizing knowledge...</p>
                  </div>
                ) : aiAnalysis && (
                  <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
                    
                    <div>
                      <h3 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2">Summary</h3>
                      <textarea 
                        className="text-sm bg-background border shadow-sm p-3 rounded-lg w-full min-h-[80px] focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                        value={aiAnalysis.summary}
                        onChange={(e) => setAiAnalysis({...aiAnalysis, summary: e.target.value})}
                      />
                    </div>

                    <div>
                      <h3 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2 flex justify-between">
                        Concepts <span className="bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300 px-1.5 py-0.5 rounded-full">{aiAnalysis.concepts.length}</span>
                      </h3>
                      {aiAnalysis.concepts.length === 0 ? (
                        <p className="text-sm text-muted-foreground bg-background p-3 rounded-lg border border-dashed">No concepts suggested.</p>
                      ) : (
                        <div className="space-y-3">
                          {aiAnalysis.concepts.map((c, i) => (
                            <div key={i} className="text-sm border border-indigo-100 dark:border-indigo-900/50 p-3 rounded-lg bg-background shadow-sm flex flex-col gap-2 relative group focus-within:ring-1 focus-within:ring-indigo-500">
                              <button onClick={() => handleRemoveConcept(i)} className="absolute top-2 right-2 text-muted-foreground opacity-0 group-hover:opacity-100 hover:text-rose-500 transition-opacity bg-background rounded-full p-0.5" title="Remove Concept">✕</button>
                              <input 
                                className="font-bold bg-transparent focus:outline-none w-[90%] text-foreground" 
                                value={c.name} 
                                onChange={(e) => handleUpdateConcept(i, 'name', e.target.value)} 
                                placeholder="Concept Name"
                              />
                              <textarea 
                                className="text-xs text-muted-foreground bg-transparent focus:outline-none w-full resize-none min-h-[40px]" 
                                value={c.description}
                                onChange={(e) => handleUpdateConcept(i, 'description', e.target.value)} 
                                placeholder="Description"
                              />
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div>
                      <h3 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2 flex justify-between">
                        Collections <span className="bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300 px-1.5 py-0.5 rounded-full">{aiAnalysis.collections.length}</span>
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {aiAnalysis.collections.length === 0 ? (
                          <p className="text-xs text-muted-foreground">None</p>
                        ) : (
                          aiAnalysis.collections.map((c, i) => (
                            <div key={i} className="flex items-center gap-1 text-xs font-semibold bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 px-2.5 py-1.5 rounded-full border border-indigo-500/20">
                              <span>#{c}</span>
                              <button onClick={() => handleRemoveCollection(i)} className="ml-1 hover:text-rose-500 bg-indigo-500/10 rounded-full w-4 h-4 flex items-center justify-center">×</button>
                            </div>
                          ))
                        )}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2 flex justify-between">
                        Relationships <span className="bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300 px-1.5 py-0.5 rounded-full">{aiAnalysis.relationships.length}</span>
                      </h3>
                      <div className="space-y-2">
                        {aiAnalysis.relationships.length === 0 ? (
                          <p className="text-sm text-muted-foreground bg-background p-3 rounded-lg border border-dashed">No relationships suggested.</p>
                        ) : (
                          aiAnalysis.relationships.map((r, i) => (
                            <div key={i} className="text-xs flex items-center justify-between bg-background p-2.5 rounded-lg border shadow-sm group">
                              <div className="flex items-center gap-2 overflow-hidden flex-1">
                                <span className="truncate font-semibold">{r.from_entity}</span>
                                <span className="text-[9px] uppercase font-bold text-indigo-500 bg-indigo-50 dark:bg-indigo-900/30 px-1.5 py-0.5 rounded">{r.relationship_type}</span>
                                <span className="truncate font-semibold">{r.to_entity}</span>
                              </div>
                              <button onClick={() => handleRemoveRelationship(i)} className="text-muted-foreground hover:text-rose-500 flex-shrink-0 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">✕</button>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2">Review Schedule</h3>
                      <select 
                        className="w-full text-sm font-medium bg-background border shadow-sm p-2.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                        value={aiAnalysis.review_suggestion || "NEVER"}
                        onChange={(e) => handleUpdateReviewSuggestion(e.target.value)}
                      >
                        <option value="NEVER">Do not schedule review</option>
                        <option value="1_DAY">Review in 1 Day</option>
                        <option value="1_WEEK">Review in 1 Week</option>
                        <option value="1_MONTH">Review in 1 Month</option>
                      </select>
                    </div>

                  </div>
                )}
              </div>

              <div className="p-4 border-t bg-background flex gap-3">
                <button 
                  onClick={handleApplyAI}
                  disabled={aiApplying || aiLoading}
                  className="flex-1 bg-indigo-600 text-white font-bold py-3 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50 transition-all active:scale-[0.98] shadow-md"
                >
                  {aiApplying ? "Applying..." : "Apply to Graph"}
                </button>
                <button 
                  onClick={() => {setAiAnalysis(null); setSelectedCaptureId(null);}}
                  disabled={aiApplying}
                  className="bg-muted text-muted-foreground font-semibold px-5 py-3 rounded-lg text-sm hover:bg-muted/80 disabled:opacity-50 transition-colors"
                >
                  Discard
                </button>
              </div>
            </div>
          )}

          {/* Today's Reading Queue */}
          {(!aiLoading && !selectedCaptureId) && (
            <div className="bg-card border rounded-xl shadow-sm overflow-hidden border-t-4 border-t-amber-500">
              <div className="p-5 border-b bg-muted/20">
                <h2 className="text-lg font-bold flex items-center justify-between">
                  <span className="flex items-center gap-2">📥 Today's Reading Queue</span>
                  <span className="bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400 text-xs px-2.5 py-1 rounded-full font-bold">
                    {summary?.reading_queue.length} items
                  </span>
                </h2>
              </div>
              {summary?.reading_queue && summary.reading_queue.length > 0 ? (
                <div className="divide-y">
                  {summary.reading_queue.map((item, idx) => (
                    <div key={`${item.id}-${idx}`} className="p-4 bg-background hover:bg-muted/30 transition-colors">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground bg-muted px-2 py-0.5 rounded">{item.type}</span>
                        <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${item.type === 'Review' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400' : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'}`}>
                          {item.reason}
                        </span>
                      </div>
                      <div className="font-semibold text-sm mb-3 line-clamp-2">{item.title}</div>
                      {item.type === 'Review' ? (
                        <button 
                          onClick={() => handleCompleteReview(item.id)}
                          className="w-full text-xs font-bold bg-secondary text-secondary-foreground py-2 rounded-lg hover:bg-secondary/80 transition-colors"
                        >
                          Mark Complete
                        </button>
                      ) : (
                        <button 
                          onClick={() => onNavigateToEntity && onNavigateToEntity(item.id)}
                          className="w-full text-xs font-bold bg-primary/10 text-primary py-2 rounded-lg hover:bg-primary/20 transition-colors"
                        >
                          Open in Explorer
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center">
                  <div className="text-4xl mb-3">🎉</div>
                  <h3 className="font-semibold mb-1">Queue is clear!</h3>
                  <p className="text-sm text-muted-foreground">You have reviewed all items for today.</p>
                </div>
              )}
            </div>
          )}

          {/* Activity Timeline */}
          {(!aiLoading && !selectedCaptureId) && summary?.activity && summary.activity.length > 0 && (
            <div className="bg-card border rounded-xl shadow-sm overflow-hidden">
              <div className="p-5 border-b bg-muted/20">
                <h2 className="text-lg font-bold flex items-center gap-2">
                  <span>⚡</span> Activity Feed
                </h2>
              </div>
              <div className="p-2">
                {summary.activity.slice(0, 8).map((event, i) => (
                  <button 
                    key={event.id} 
                    onClick={() => onNavigateToEntity && onNavigateToEntity(event.aggregate_id)}
                    className="w-full text-left p-3 text-sm flex gap-4 hover:bg-muted/50 rounded-lg transition-colors group"
                  >
                    <div className="text-muted-foreground font-medium text-xs pt-0.5 w-12 text-right">
                      {new Date(event.occurred_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                    <div>
                      <span className="font-semibold text-foreground group-hover:text-primary transition-colors">{event.event_type.replace(/([A-Z])/g, ' $1').trim()}</span>
                      <div className="text-xs text-muted-foreground mt-0.5">{event.aggregate_type}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
          
        </div>
      </div>
    </div>
  );
}
