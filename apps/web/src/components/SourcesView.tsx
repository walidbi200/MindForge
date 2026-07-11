import { useState, useEffect } from "react";

interface Source {
  id: string;
  title: string;
  source_type: string;
  uri: string | null;
  author: string | null;
  publisher: string | null;
  language: string | null;
  created_at: string;
  updated_at: string;
  metadata_json: string;
}

const SOURCE_TYPES = [
  "WEB_ARTICLE",
  "YOUTUBE",
  "PDF",
  "BOOK",
  "MARKDOWN",
  "IMAGE",
  "AUDIO",
  "VIDEO",
  "TWEET",
  "LOCAL_FILE",
  "MANUAL",
];

export function SourcesView() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filterType, setFilterType] = useState("");

  // Form State
  const [isEditing, setIsEditing] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [sourceType, setSourceType] = useState("WEB_ARTICLE");
  const [uri, setUri] = useState("");
  const [author, setAuthor] = useState("");
  const [publisher, setPublisher] = useState("");
  const [language, setLanguage] = useState("");
  const [metadataJson, setMetadataJson] = useState("{}");

  const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  const fetchSources = async () => {
    setLoading(true);
    setError("");
    try {
      let url = `${baseUrl}/api/v1/sources?limit=100`;
      if (filterType) {
        url += `&source_type=${filterType}`;
      }
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to fetch sources");
      const data = await res.json();
      setSources(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSources();
  }, [filterType]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const payload = {
      title,
      source_type: sourceType,
      uri: uri || null,
      author: author || null,
      publisher: publisher || null,
      language: language || null,
      metadata_json: metadataJson,
    };

    try {
      let res;
      if (editingId) {
        res = await fetch(`${baseUrl}/api/v1/sources/${editingId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } else {
        res = await fetch(`${baseUrl}/api/v1/sources`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Operation failed");
      }

      // Reset form
      resetForm();
      fetchSources();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const resetForm = () => {
    setIsEditing(false);
    setEditingId(null);
    setTitle("");
    setSourceType("WEB_ARTICLE");
    setUri("");
    setAuthor("");
    setPublisher("");
    setLanguage("");
    setMetadataJson("{}");
  };

  const handleEdit = (source: Source) => {
    setIsEditing(true);
    setEditingId(source.id);
    setTitle(source.title);
    setSourceType(source.source_type);
    setUri(source.uri || "");
    setAuthor(source.author || "");
    setPublisher(source.publisher || "");
    setLanguage(source.language || "");
    setMetadataJson(source.metadata_json);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this source?")) return;
    setError("");
    try {
      const res = await fetch(`${baseUrl}/api/v1/sources/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to delete source");
      }
      fetchSources();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Sources</h1>
          <p className="text-muted-foreground mt-2">
            Manage provenance and origins of knowledge in MindForge.
          </p>
        </div>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          >
            Add Source
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
            {editingId ? "Edit Source" : "Create New Source"}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Title *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Source Type *</label>
                <select
                  value={sourceType}
                  onChange={(e) => setSourceType(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  {SOURCE_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">URI (Optional)</label>
                <input
                  type="text"
                  value={uri}
                  onChange={(e) => setUri(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Author (Optional)</label>
                <input
                  type="text"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Publisher (Optional)</label>
                <input
                  type="text"
                  value={publisher}
                  onChange={(e) => setPublisher(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Language (Optional)</label>
                <input
                  type="text"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Metadata JSON (Optional)</label>
                <input
                  type="text"
                  value={metadataJson}
                  onChange={(e) => setMetadataJson(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
            </div>

            <div className="flex gap-4 pt-4 justify-end">
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
                {editingId ? "Save Changes" : "Create Source"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filter and List Section */}
      <div className="flex justify-between items-center border-b pb-4">
        <div className="flex items-center gap-4">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Filter by Type:</span>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="flex h-9 rounded-md border border-input bg-background px-3 text-sm focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value="">All Types</option>
            {SOURCE_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading sources...</div>
      ) : sources.length === 0 ? (
        <div className="text-center py-12 border border-dashed rounded-lg bg-card/20">
          <p className="text-muted-foreground">No sources found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sources.map((source) => (
            <div
              key={source.id}
              className="rounded-lg border bg-card p-6 shadow-sm hover:shadow-md transition-shadow relative space-y-4"
            >
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-muted text-muted-foreground border">
                    {source.source_type}
                  </span>
                  <h4 className="text-lg font-semibold mt-2">{source.title}</h4>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(source)}
                    className="text-xs hover:text-primary underline"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(source.id)}
                    className="text-xs text-destructive hover:underline"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                {source.uri && (
                  <div className="col-span-2">
                    <span className="font-semibold text-foreground/75">URI: </span>
                    <a
                      href={source.uri}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:underline text-primary"
                    >
                      {source.uri}
                    </a>
                  </div>
                )}
                {source.author && (
                  <div>
                    <span className="font-semibold text-foreground/75">Author: </span>
                    {source.author}
                  </div>
                )}
                {source.publisher && (
                  <div>
                    <span className="font-semibold text-foreground/75">Publisher: </span>
                    {source.publisher}
                  </div>
                )}
                {source.language && (
                  <div>
                    <span className="font-semibold text-foreground/75">Lang: </span>
                    {source.language}
                  </div>
                )}
                <div className="col-span-2 text-[10px] font-mono truncate">
                  ID: {source.id}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
