import { useState, useEffect } from "react";
import { API_BASE_URL } from "@/lib/api";

interface Collection {
  id: string;
  name: string;
  description: string;
  color: string;
  icon: string;
  created_at: string;
  updated_at: string;
  metadata_json: string;
  item_count: number;
}

interface MemberNode {
  id: string;
  type: string;
  title: string;
}

export function CollectionsView() {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Filters and search
  const [q, setQ] = useState("");
  const [colorFilter, setColorFilter] = useState("");
  const [iconFilter, setIconFilter] = useState("");

  // Selection
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [members, setMembers] = useState<MemberNode[]>([]);
  const [loadingMembers, setLoadingMembers] = useState(false);

  // Form State
  const [isEditing, setIsEditing] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [color, setColor] = useState("#3B82F6");
  const [icon, setIcon] = useState("book");

  // Add Member form state
  const [newMemberId, setNewMemberId] = useState("");
  const [newMemberType, setNewMemberType] = useState("Capture");
  const [memberError, setMemberError] = useState("");


  const fetchCollections = async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (q.trim()) params.append("q", q.trim());
      if (colorFilter.trim()) params.append("color", colorFilter.trim());
      if (iconFilter.trim()) params.append("icon", iconFilter.trim());

      const res = await fetch(`${API_BASE_URL}/api/v1/collections?${params.toString()}`);
      if (!res.ok) throw new Error("Failed to fetch collections");
      const data: Collection[] = await res.json();
      setCollections(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollections();
  }, [q, colorFilter, iconFilter]);

  const fetchMembers = async (colId: string) => {
    setLoadingMembers(true);
    setMemberError("");
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/collections/${colId}/entities`);
      if (!res.ok) throw new Error("Failed to load members");
      const data = await res.json();
      setMembers(data);
    } catch (err: any) {
      setMemberError(err.message);
    } finally {
      setLoadingMembers(false);
    }
  };

  const handleSelectCollection = (id: string) => {
    setSelectedId(id);
    fetchMembers(id);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const payload = {
      name,
      description,
      color,
      icon,
    };

    try {
      let res;
      if (editingId) {
        res = await fetch(`${API_BASE_URL}/api/v1/collections/${editingId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } else {
        res = await fetch(`${API_BASE_URL}/api/v1/collections`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Operation failed");
      }

      resetForm();
      fetchCollections();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this collection?")) return;
    setError("");
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/collections/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to delete collection");
      }
      if (selectedId === id) {
        setSelectedId(null);
      }
      fetchCollections();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedId || !newMemberId.trim()) return;
    setMemberError("");

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/collections/${selectedId}/entities`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          entity_id: newMemberId.trim(),
          entity_type: newMemberType,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to add member");
      }

      setNewMemberId("");
      fetchMembers(selectedId);
      fetchCollections(); // Update list counts
    } catch (err: any) {
      setMemberError(err.message);
    }
  };

  const handleRemoveMember = async (entityId: string) => {
    if (!selectedId) return;
    if (!confirm("Remove this member from collection?")) return;
    setMemberError("");

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/collections/${selectedId}/entities/${entityId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to remove member");
      }

      fetchMembers(selectedId);
      fetchCollections(); // Update list counts
    } catch (err: any) {
      setMemberError(err.message);
    }
  };

  const handleEditCollection = (c: Collection) => {
    setIsEditing(true);
    setEditingId(c.id);
    setName(c.name);
    setDescription(c.description);
    setColor(c.color);
    setIcon(c.icon);
  };

  const resetForm = () => {
    setIsEditing(false);
    setEditingId(null);
    setName("");
    setDescription("");
    setColor("#3B82F6");
    setIcon("book");
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Spaces (Collections)</h1>
          <p className="text-muted-foreground mt-2">
            Organize knowledge, captures, and concepts into structural collections.
          </p>
        </div>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          >
            New Collection
          </button>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-md bg-destructive/10 text-destructive border border-destructive/20 text-sm">
          {error}
        </div>
      )}

      {isEditing && (
        <div className="rounded-lg border bg-card text-card-foreground p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">
            {editingId ? "Edit Collection" : "Create New Collection"}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Name *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Description</label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Color Hex</label>
                <input
                  type="text"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Icon Identifier</label>
                <input
                  type="text"
                  value={icon}
                  onChange={(e) => setIcon(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
                />
              </div>
            </div>

            <div className="flex gap-4 justify-end">
              <button
                type="button"
                onClick={resetForm}
                className="inline-flex items-center justify-center rounded-md text-sm font-medium border border-input bg-background hover:bg-accent h-10 px-4 py-2"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
              >
                Save
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Search and Filters Controls */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 border p-4 rounded-lg bg-card/20">
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 block">Search</label>
          <input
            type="text"
            placeholder="Search by name or desc..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
          />
        </div>
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 block">Color Filter</label>
          <input
            type="text"
            placeholder="e.g. #3B82F6"
            value={colorFilter}
            onChange={(e) => setColorFilter(e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
          />
        </div>
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1 block">Icon Filter</label>
          <input
            type="text"
            placeholder="e.g. book"
            value={iconFilter}
            onChange={(e) => setIconFilter(e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
          />
        </div>
      </div>

      {/* Main Layout Split Screen */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Col: Collection list */}
        <div className="lg:col-span-1 space-y-4">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Spaces</h3>
          {loading ? (
            <div className="text-muted-foreground text-sm py-4">Loading Spaces...</div>
          ) : collections.length === 0 ? (
            <div className="text-muted-foreground text-sm border border-dashed rounded p-6 text-center">
              No spaces found matching your search. Clear filters or add a new space.
            </div>
          ) : (
            <div className="space-y-2">
              {collections.map((c) => (
                <div
                  key={c.id}
                  onClick={() => handleSelectCollection(c.id)}
                  style={{ borderLeftColor: c.color }}
                  className={`p-4 rounded border bg-card/50 cursor-pointer border-l-4 transition-all hover:bg-card ${
                    selectedId === c.id ? "bg-card shadow-sm ring-1 ring-ring" : ""
                  }`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-semibold text-base flex items-center gap-1.5">
                      <span>[{c.icon}]</span>
                      <span>{c.name}</span>
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded bg-muted font-mono font-bold">
                      {c.item_count} items
                    </span>
                  </div>
                  {c.description && <p className="text-xs text-muted-foreground line-clamp-2">{c.description}</p>}
                  
                  <div className="flex gap-2 justify-end mt-4 text-[10px]">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditCollection(c);
                      }}
                      className="hover:text-primary underline"
                    >
                      Edit
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(c.id);
                      }}
                      className="text-destructive hover:underline"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Col: Collection Members */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Space Detail</h3>
          
          {selectedId ? (
            <div className="border rounded-lg p-6 bg-card/40 space-y-6">
              {collections.filter(c => c.id === selectedId).map(col => (
                <div key={col.id} className="border-b pb-4">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">[{col.icon}]</span>
                    <h2 className="text-2xl font-bold">{col.name}</h2>
                  </div>
                  {col.description && <p className="text-sm text-muted-foreground mt-1">{col.description}</p>}
                </div>
              ))}

              {/* Add Member form */}
              <div className="border rounded p-4 bg-card/60">
                <h4 className="text-xs font-semibold uppercase tracking-wider mb-2">Add Member Entity</h4>
                {memberError && (
                  <div className="text-xs text-destructive bg-destructive/10 p-2 rounded mb-2 border border-destructive/20">
                    {memberError}
                  </div>
                )}
                <form onSubmit={handleAddMember} className="flex flex-col sm:flex-row gap-3">
                  <select
                    value={newMemberType}
                    onChange={(e) => setNewMemberType(e.target.value)}
                    className="flex h-10 w-full sm:w-32 rounded border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="Capture">Capture</option>
                    <option value="Concept">Concept</option>
                    <option value="Source">Source</option>
                  </select>
                  <input
                    type="text"
                    required
                    placeholder="Enter Entity UUID"
                    value={newMemberId}
                    onChange={(e) => setNewMemberId(e.target.value)}
                    className="flex-1 h-10 rounded border border-input bg-background px-3 py-2 text-sm"
                  />
                  <button
                    type="submit"
                    className="h-10 px-4 rounded bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90"
                  >
                    Add Member
                  </button>
                </form>
              </div>

              {/* Members List */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Members</h4>
                
                {loadingMembers ? (
                  <p className="text-xs text-muted-foreground">Loading members...</p>
                ) : members.length === 0 ? (
                  <p className="text-xs text-muted-foreground border border-dashed rounded p-4 text-center">
                    This space is empty. Add captures or concepts above.
                  </p>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {members.map((node) => (
                      <div key={node.id} className="p-4 rounded border bg-card flex flex-col justify-between gap-4">
                        <div>
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-[10px] px-1.5 py-0.5 rounded font-semibold bg-muted uppercase text-muted-foreground border">
                              {node.type}
                            </span>
                            <button
                              onClick={() => handleRemoveMember(node.id)}
                              className="text-xs text-destructive hover:underline"
                            >
                              Remove
                            </button>
                          </div>
                          <p className="text-sm font-medium line-clamp-3">{node.title}</p>
                        </div>
                        <span className="text-[10px] text-muted-foreground font-mono truncate">ID: {node.id}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="border border-dashed rounded-lg p-12 text-center text-muted-foreground">
              Select a Space from the left sidebar to view details and members.
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
