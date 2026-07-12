import { useState, useEffect } from "react";
import { ChevronRight, ExternalLink, Network, FileText, Database, BookOpen, AlertCircle, ArrowLeft } from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

interface KnowledgeNeighborhood {
  center: {
    entity_type: string;
    id: string;
    title?: string;
    content?: string;
    summary?: string;
    name?: string;
    description?: string;
    uri?: string;
    [key: string]: any;
  };
  concepts: any[];
  captures: any[];
  sources: any[];
  collections: any[];
  relationships: any[];
}

interface KnowledgeExplorerProps {
  initialEntityId?: string;
  onNavigateToWorkspace?: () => void;
}

export function KnowledgeExplorer({ initialEntityId, onNavigateToWorkspace }: KnowledgeExplorerProps) {
  const [entityId, setEntityId] = useState(initialEntityId || "");
  const [history, setHistory] = useState<string[]>(initialEntityId ? [initialEntityId] : []);
  const [data, setData] = useState<KnowledgeNeighborhood | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [duplicates, setDuplicates] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editSummary, setEditSummary] = useState("");

  useEffect(() => {
    if (initialEntityId && initialEntityId !== entityId) {
      handleNavigate(initialEntityId);
    }
  }, [initialEntityId]);

  useEffect(() => {
    if (entityId) {
      fetchNeighborhood(entityId);
    }
  }, [entityId]);

  const fetchNeighborhood = async (id: string) => {
    setLoading(true);
    setError("");
    setData(null);
    setDuplicates([]);
    setRecommendations([]);
    
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/graph/neighborhood/${id}`);
      if (!res.ok) throw new Error("Failed to fetch neighborhood");
      
      const json = await res.json();
      setData(json);

      if (json.center.entity_type === "Concept" && json.center.title) {
        const dupRes = await fetch(`${API_BASE_URL}/api/v1/graph/check-duplicates?title=${encodeURIComponent(json.center.title)}&exclude_id=${id}`);
        if (dupRes.ok) {
          const dups = await dupRes.json();
          if (dups.length > 0) setDuplicates(dups);
        }
      }

      const recRes = await fetch(`${API_BASE_URL}/api/v1/graph/recommendations/${id}`);
      if (recRes.ok) {
        const recs = await recRes.json();
        setRecommendations(recs);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateConcept = async () => {
    if (!data || data.center.entity_type !== 'Concept') return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/concepts/${entityId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: editTitle, summary: editSummary })
      });
      if (!res.ok) throw new Error("Failed to update concept");
      setIsEditing(false);
      fetchNeighborhood(entityId); // Refresh data
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleMerge = async (targetId: string) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/concepts/${entityId}/merge/${targetId}`, {
        method: "POST"
      });
      if (!res.ok) throw new Error("Failed to merge concepts");
      handleNavigate(targetId); // Navigate to the target concept
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleNavigate = (id: string) => {
    setHistory(prev => [...prev, id]);
    setEntityId(id);
  };

  const handleBack = () => {
    if (history.length > 1) {
      const newHistory = [...history];
      newHistory.pop(); // remove current
      const prevId = newHistory[newHistory.length - 1];
      setHistory(newHistory);
      setEntityId(prevId);
    } else if (onNavigateToWorkspace) {
      onNavigateToWorkspace();
    }
  };

  if (!entityId) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
        <Network className="w-16 h-16 mb-4 opacity-50" />
        <p>Select an entity to begin exploration</p>
      </div>
    );
  }

  const getEntityIcon = (type: string) => {
    switch(type) {
      case 'Concept': return <Database className="w-4 h-4" />;
      case 'Capture': return <FileText className="w-4 h-4" />;
      case 'Source': return <BookOpen className="w-4 h-4" />;
      default: return <Network className="w-4 h-4" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Breadcrumbs & Navigation */}
      <div className="flex items-center gap-2 p-4 border-b bg-card/50">
        <button onClick={handleBack} className="p-2 hover:bg-muted rounded-md transition-colors text-muted-foreground">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex items-center text-sm text-muted-foreground">
          <button onClick={onNavigateToWorkspace} className="hover:text-foreground transition-colors">Workspace</button>
          <ChevronRight className="w-4 h-4 mx-1" />
          <span className="text-foreground font-medium">{data ? (data.center.title || data.center.name || 'Capture') : 'Loading...'}</span>
        </div>
      </div>

      {loading && <div className="p-8 text-center text-muted-foreground animate-pulse">Mapping Knowledge Neighborhood...</div>}
      {error && <div className="p-8 text-rose-500 bg-rose-500/10 m-4 rounded-md border border-rose-500/20">{error}</div>}

      {data && (
        <div className="flex flex-1 overflow-hidden">
          {/* Main Content Area */}
          <div className="flex-1 overflow-y-auto p-6 md:p-10 border-r">
            
            {duplicates.length > 0 && (
              <div className="mb-6 p-4 rounded-md border border-amber-500/30 bg-amber-500/10 flex gap-3 items-start">
                <AlertCircle className="w-5 h-5 text-amber-500 mt-0.5 shrink-0" />
                <div>
                  <h4 className="text-sm font-medium text-amber-600 dark:text-amber-400">Potential Duplicate Found</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    "{duplicates[0].title}" is very similar ({Math.round(duplicates[0].similarity_score * 100)}% match). 
                    Consider merging if they represent the same concept.
                  </p>
                  <div className="flex gap-2 mt-3">
                    <button 
                      onClick={() => handleNavigate(duplicates[0].concept_id)}
                      className="text-xs font-medium bg-background border px-3 py-1.5 rounded shadow-sm hover:bg-muted"
                    >
                      View Duplicate
                    </button>
                    <button 
                      onClick={() => handleMerge(duplicates[0].concept_id)}
                      className="text-xs font-medium bg-amber-500 text-white border border-transparent px-3 py-1.5 rounded shadow-sm hover:bg-amber-600 transition-colors"
                    >
                      Merge into Duplicate
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="mb-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary uppercase tracking-wider">
              {getEntityIcon(data.center.entity_type)}
              {data.center.entity_type}
            </div>
            
            <div className="flex items-start justify-between gap-4 mt-2 mb-6">
              {isEditing ? (
                <div className="flex-1">
                  <input 
                    className="w-full text-3xl md:text-4xl font-bold tracking-tight bg-background border rounded px-3 py-1 mb-2"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                  />
                  <div className="flex gap-2">
                    <button onClick={handleUpdateConcept} className="text-xs font-medium bg-primary text-primary-foreground px-3 py-1 rounded">Save</button>
                    <button onClick={() => setIsEditing(false)} className="text-xs font-medium bg-muted text-muted-foreground px-3 py-1 rounded">Cancel</button>
                  </div>
                </div>
              ) : (
                <>
                  <h1 className="text-3xl md:text-4xl font-bold tracking-tight flex-1">
                    {data.center.title || data.center.name || 'Untitled Entity'}
                  </h1>
                  {data.center.entity_type === 'Concept' && (
                    <button 
                      onClick={() => {
                        setEditTitle(data.center.title || "");
                        setEditSummary(data.center.summary || "");
                        setIsEditing(true);
                      }}
                      className="text-sm font-medium text-muted-foreground hover:text-foreground shrink-0 mt-2"
                    >
                      Edit
                    </button>
                  )}
                </>
              )}
            </div>

            {/* Entity Content based on type */}
            <div className="prose prose-sm md:prose-base dark:prose-invert max-w-none">
              {data.center.entity_type === 'Concept' && (
                <div className="bg-card border rounded-lg p-6 shadow-sm">
                  <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-2">Summary</h3>
                  {isEditing ? (
                    <textarea 
                      className="w-full h-32 text-lg leading-relaxed bg-background border rounded p-3"
                      value={editSummary}
                      onChange={(e) => setEditSummary(e.target.value)}
                    />
                  ) : (
                    <p className="text-lg leading-relaxed">{data.center.summary}</p>
                  )}
                </div>
              )}
              {data.center.entity_type === 'Capture' && (
                <div className="bg-card border rounded-lg p-6 shadow-sm font-mono text-sm whitespace-pre-wrap">
                  {data.center.content}
                </div>
              )}
              {data.center.entity_type === 'Source' && (
                <div className="bg-card border rounded-lg p-6 shadow-sm flex flex-col gap-4">
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground w-20">URI:</span> 
                    <a href={data.center.uri} target="_blank" rel="noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                      {data.center.uri} <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                  {data.center.author && <div><span className="text-muted-foreground w-20 inline-block">Author:</span> {data.center.author}</div>}
                  {data.center.publisher && <div><span className="text-muted-foreground w-20 inline-block">Publisher:</span> {data.center.publisher}</div>}
                </div>
              )}
              {data.center.entity_type === 'Collection' && (
                <div className="bg-card border rounded-lg p-6 shadow-sm">
                  <p className="text-lg leading-relaxed">{data.center.description}</p>
                </div>
              )}
            </div>

            {/* Interactive Graph Area (Simplified list view for now, could be D3 later) */}
            <div className="mt-12">
              <h3 className="text-xl font-semibold mb-6 flex items-center gap-2 border-b pb-2">
                <Network className="w-5 h-5 text-muted-foreground" />
                Knowledge Neighborhood
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {data.concepts.map(c => (
                  <button key={c.id} onClick={() => handleNavigate(c.id)} className="text-left group bg-card border rounded-lg p-4 hover:border-primary/50 hover:shadow-md transition-all">
                    <div className="flex items-center gap-2 mb-2">
                      <Database className="w-4 h-4 text-indigo-500" />
                      <span className="text-xs font-medium text-indigo-500">Concept</span>
                    </div>
                    <div className="font-medium group-hover:text-primary transition-colors">{c.title}</div>
                  </button>
                ))}
                
                {data.sources.map(s => (
                  <button key={s.id} onClick={() => handleNavigate(s.id)} className="text-left group bg-card border rounded-lg p-4 hover:border-primary/50 hover:shadow-md transition-all">
                    <div className="flex items-center gap-2 mb-2">
                      <BookOpen className="w-4 h-4 text-amber-500" />
                      <span className="text-xs font-medium text-amber-500">Source</span>
                    </div>
                    <div className="font-medium group-hover:text-primary transition-colors line-clamp-2">{s.title}</div>
                  </button>
                ))}

                {data.captures.map(c => (
                  <button key={c.id} onClick={() => handleNavigate(c.id)} className="text-left group bg-card border rounded-lg p-4 hover:border-primary/50 hover:shadow-md transition-all">
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="w-4 h-4 text-emerald-500" />
                      <span className="text-xs font-medium text-emerald-500">Capture</span>
                    </div>
                    <div className="font-mono text-xs line-clamp-3 text-muted-foreground group-hover:text-foreground transition-colors">{c.content}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            {recommendations.length > 0 && (
              <div className="mt-12 mb-8">
                <h3 className="text-xl font-semibold mb-6 flex items-center gap-2 border-b pb-2">
                  <span className="text-muted-foreground">✨</span>
                  You may also want to revisit
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recommendations.map(r => (
                    <button key={r.id} onClick={() => handleNavigate(r.id)} className="text-left group bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/50 rounded-lg p-4 hover:border-indigo-500/50 hover:shadow-md transition-all">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getEntityIcon(r.type)}
                          <span className="text-xs font-medium text-muted-foreground">{r.type}</span>
                        </div>
                        <span className="text-[10px] uppercase font-semibold text-indigo-500 bg-indigo-100 dark:bg-indigo-900/50 px-2 py-0.5 rounded-full">{r.reason}</span>
                      </div>
                      <div className="font-medium text-indigo-950 dark:text-indigo-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-2">{r.title}</div>
                    </button>
                  ))}
                </div>
              </div>
            )}

          </div>

          {/* Right Sidebar - Backlinks & Meta */}
          <div className="w-80 bg-muted/20 border-l p-6 overflow-y-auto hidden lg:block">
            <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground mb-4">Backlinks (Referenced By)</h3>
            
            <div className="space-y-3">
              {data.relationships.filter(r => r.to_id === data.center.id).length === 0 && data.collections.length === 0 ? (
                <div className="text-sm text-muted-foreground italic">No incoming references.</div>
              ) : (
                <>
                  {data.relationships.filter(r => r.to_id === data.center.id).map(r => {
                    // Find the entity that points to us
                    const sourceEntity = 
                      data.concepts.find(c => c.id === r.from_id) || 
                      data.captures.find(c => c.id === r.from_id) || 
                      data.sources.find(c => c.id === r.from_id);
                    
                    return (
                      <button key={r.id} onClick={() => sourceEntity && handleNavigate(sourceEntity.id)} className="w-full text-left bg-background border rounded-md p-3 hover:border-primary/50 transition-colors">
                        <div className="text-[10px] uppercase font-bold text-muted-foreground mb-1">{r.relationship_type.replace('_', ' ')}</div>
                        <div className="text-sm font-medium truncate">{sourceEntity?.title || sourceEntity?.content?.substring(0,30) || 'Unknown Entity'}</div>
                      </button>
                    )
                  })}

                  {data.collections.map(col => (
                    <button key={col.id} onClick={() => handleNavigate(col.id)} className="w-full text-left bg-background border rounded-md p-3 hover:border-primary/50 transition-colors">
                      <div className="text-[10px] uppercase font-bold text-muted-foreground mb-1">In Collection</div>
                      <div className="text-sm font-medium truncate flex items-center gap-2">
                        <span>{col.icon || '📂'}</span>
                        {col.name}
                      </div>
                    </button>
                  ))}
                </>
              )}
            </div>

            <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground mt-8 mb-4">Outgoing Edges</h3>
            <div className="space-y-3">
              {data.relationships.filter(r => r.from_id === data.center.id).length === 0 ? (
                <div className="text-sm text-muted-foreground italic">No outgoing references.</div>
              ) : (
                data.relationships.filter(r => r.from_id === data.center.id).map(r => {
                  const targetEntity = 
                    data.concepts.find(c => c.id === r.to_id) || 
                    data.captures.find(c => c.id === r.to_id) || 
                    data.sources.find(c => c.id === r.to_id);
                  
                  return (
                    <button key={r.id} onClick={() => targetEntity && handleNavigate(targetEntity.id)} className="w-full text-left bg-background border rounded-md p-3 hover:border-primary/50 transition-colors">
                      <div className="text-[10px] uppercase font-bold text-primary mb-1">{r.relationship_type.replace('_', ' ')}</div>
                      <div className="text-sm font-medium truncate">{targetEntity?.title || targetEntity?.content?.substring(0,30) || 'Unknown Entity'}</div>
                    </button>
                  )
                })
              )}
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
