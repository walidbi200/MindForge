import { useState } from "react";

interface NodeResponse {
  id: string;
  type: string;
  title: string;
}

interface RelationshipResponse {
  id: string;
  from_id: string;
  to_id: string;
  relationship_type: string;
  confidence: number;
}

interface GraphResponse {
  nodes: NodeResponse[];
  relationships: RelationshipResponse[];
}

export function GraphExplorer() {
  const [entityId, setEntityId] = useState("");
  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFetchGraph = async () => {
    if (!entityId.trim()) return;
    
    setLoading(true);
    setError("");
    setGraphData(null);
    
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      // We will fetch the neighborhood (depth 1) by default
      const res = await fetch(`${baseUrl}/api/v1/graph/neighborhood/${entityId}`);
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error("Entity not found");
        }
        throw new Error("Failed to fetch graph data");
      }
      
      const data = await res.json();
      setGraphData(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Graph Explorer</h1>
        <p className="text-muted-foreground mt-2">
          Navigate relationships and visualize connected entities in MindForge.
        </p>
      </div>

      {/* Search Bar */}
      <div className="flex gap-4">
        <input 
          type="text" 
          value={entityId}
          onChange={(e) => setEntityId(e.target.value)}
          placeholder="Enter Entity UUID (Capture or Concept)" 
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 flex-1 max-w-md"
        />
        <button 
          onClick={handleFetchGraph}
          disabled={loading || !entityId.trim()}
          className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
        >
          {loading ? "Searching..." : "Explore Neighborhood"}
        </button>
      </div>

      {/* State rendering */}
      {error && (
        <div className="p-4 rounded-md bg-destructive/10 text-destructive border border-destructive/20">
          {error}
        </div>
      )}

      {graphData && (
        <div className="mt-8 border rounded-lg p-6 bg-card/50 min-h-[400px]">
          <h3 className="text-lg font-semibold mb-6 border-b pb-2">Neighborhood View</h3>
          
          {graphData.nodes.length === 0 ? (
            <p className="text-muted-foreground">No connections found for this entity.</p>
          ) : (
            <div className="flex flex-col md:flex-row gap-8 items-start">
              
              {/* Root Node rendering (simplified approach: we assume requested entity is root) */}
              <div className="flex flex-col items-center gap-2">
                <div className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-2">Target Node</div>
                {graphData.nodes.filter(n => n.id === entityId).map(node => (
                  <GraphNode key={node.id} node={node} isRoot={true} />
                ))}
              </div>

              {/* Connections */}
              <div className="flex-1 border-l pl-8 space-y-6">
                <div className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">Connections</div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {graphData.nodes.filter(n => n.id !== entityId).map(node => {
                    // Find relationship linking this node to the root
                    const rel = graphData.relationships.find(r => 
                      (r.from_id === entityId && r.to_id === node.id) || 
                      (r.to_id === entityId && r.from_id === node.id)
                    );
                    
                    const isOutgoing = rel?.from_id === entityId;

                    return (
                      <div key={node.id} className="flex flex-col gap-2 relative">
                        {rel && (
                          <div className="text-xs font-mono px-2 py-1 bg-muted rounded w-fit mb-1 border">
                            {isOutgoing ? '──( ' + rel.relationship_type + ' )─▶' : '◀─( ' + rel.relationship_type + ' )──'}
                          </div>
                        )}
                        <GraphNode node={node} isRoot={false} />
                      </div>
                    );
                  })}
                </div>
              </div>

            </div>
          )}
        </div>
      )}
    </div>
  );
}

function GraphNode({ node, isRoot }: { node: NodeResponse, isRoot: boolean }) {
  return (
    <div className={`p-4 rounded-lg border shadow-sm w-64 break-words ${isRoot ? 'bg-primary/5 border-primary/30 shadow-primary/10' : 'bg-card'}`}>
      <div className="flex items-center justify-between mb-2">
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${node.type === 'Concept' ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400' : 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'}`}>
          {node.type}
        </span>
      </div>
      <p className="text-sm font-medium line-clamp-3">{node.title}</p>
      <p className="text-[10px] text-muted-foreground mt-4 font-mono truncate" title={node.id}>ID: {node.id.substring(0,8)}...</p>
    </div>
  );
}
