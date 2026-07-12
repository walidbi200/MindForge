import { useState, useEffect } from "react";
import { API_BASE_URL } from "@/lib/api";

interface Review {
  id: string;
  entity_id: string;
  entity_type: string;
  status: string;
  due_at: string;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  metadata_json: string;
}

export function ReviewsView() {
  const [dueReviews, setDueReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Selected Review details
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedReview, setSelectedReview] = useState<Review | null>(null);

  // Complete review form state
  const [notes, setNotes] = useState("");
  const [formError, setFormError] = useState("");
  const [formSuccess, setFormSuccess] = useState("");


  const fetchDueData = async () => {
    setLoading(true);
    setError("");
    try {
      const resDue = await fetch(`${API_BASE_URL}/api/v1/reviews/due`);
      if (!resDue.ok) throw new Error("Failed to fetch due reviews");

      const dueData = await resDue.json();
      setDueReviews(dueData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDueData();
  }, []);

  const handleSelectReview = async (id: string) => {
    setSelectedId(id);
    setFormError("");
    setFormSuccess("");
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/reviews/${id}`);
      if (!res.ok) throw new Error("Failed to load review details");
      const data = await res.json();
      setSelectedReview(data);
      // parse metadata_json for notes
      try {
        const meta = JSON.parse(data.metadata_json || "{}");
        setNotes(meta.notes || "");
      } catch (e) {
        setNotes("");
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleCompleteReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedId) return;
    setFormError("");
    setFormSuccess("");

    try {
      const metadata_json = JSON.stringify({ notes });
      const res = await fetch(`${API_BASE_URL}/api/v1/reviews/${selectedId}/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ metadata_json }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to complete review");
      }

      const updated = await res.json();
      setSelectedReview(updated);
      setFormSuccess("Review completed successfully!");
      fetchDueData();
    } catch (err: any) {
      setFormError(err.message);
    }
  };

  const handleSkipReview = async () => {
    if (!selectedId) return;
    if (!confirm("Are you sure you want to skip this review?")) return;
    setFormError("");
    setFormSuccess("");

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/reviews/${selectedId}/skip`, {
        method: "POST",
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to skip review");
      }

      const updated = await res.json();
      setSelectedReview(updated);
      setFormSuccess("Review skipped.");
      fetchDueData();
    } catch (err: any) {
      setFormError(err.message);
    }
  };

  const handleDeleteReview = async (id: string) => {
    if (!confirm("Are you sure you want to delete this review?")) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/reviews/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete review");
      if (selectedId === id) {
        setSelectedId(null);
        setSelectedReview(null);
      }
      fetchDueData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reviews</h1>
          <p className="text-muted-foreground mt-2">
            Schedule and perform reviews on your captures, concepts, and sources.
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded bg-destructive/10 text-destructive border border-destructive/20 text-sm">
          {error}
        </div>
      )}

      {/* Main Grid split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Lists */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Section 1: Due Reviews */}
          <div className="space-y-2">
            <h3 className="text-sm font-bold text-rose-500 uppercase tracking-wider flex justify-between items-center">
              <span>Due Reviews</span>
              <span className="text-xs px-2 py-0.5 rounded bg-rose-500/10 font-mono">{dueReviews.length}</span>
            </h3>
            {loading ? (
              <p className="text-xs text-muted-foreground">Loading...</p>
            ) : dueReviews.length === 0 ? (
              <p className="text-xs text-muted-foreground border border-dashed rounded p-3 text-center">
                All caught up! No due reviews.
              </p>
            ) : (
              <div className="space-y-2">
                {dueReviews.map((r) => (
                  <div
                    key={r.id}
                    onClick={() => handleSelectReview(r.id)}
                    className={`p-3 rounded border bg-card/60 cursor-pointer hover:bg-card/90 transition-all ${
                      selectedId === r.id ? "ring-1 ring-ring bg-card" : ""
                    }`}
                  >
                    <div className="flex justify-between items-center text-xs font-semibold mb-1">
                      <span className="uppercase text-[9px] bg-muted px-1 rounded text-muted-foreground">{r.entity_type}</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground font-mono truncate">Entity ID: {r.entity_id}</p>
                    <p className="text-[9px] text-muted-foreground/60 mt-1">Due: {new Date(r.due_at).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Detail & Action Pane */}
        <div className="lg:col-span-2">
          {selectedReview ? (
            <div className="border rounded-lg p-6 bg-card/30 space-y-6">
              <div className="flex justify-between items-start border-b pb-4">
                <div>
                  <h3 className="text-2xl font-bold flex items-center gap-2">
                    <span>Review Details</span>
                  </h3>
                  <p className="text-xs text-muted-foreground font-mono mt-1">Review ID: {selectedReview.id}</p>
                </div>
                <button
                  onClick={() => handleDeleteReview(selectedReview.id)}
                  className="text-xs text-destructive hover:underline"
                >
                  Delete
                </button>
              </div>

              {/* Entity metadata */}
              <div className="grid grid-cols-2 gap-4 bg-muted/30 p-4 rounded text-sm">
                <div>
                  <span className="text-xs text-muted-foreground block uppercase font-semibold">Entity Type</span>
                  <span className="font-medium text-base">{selectedReview.entity_type}</span>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground block uppercase font-semibold">Status</span>
                  <span className={`font-medium text-base ${selectedReview.status === 'COMPLETED' ? 'text-emerald-400' : selectedReview.status === 'SKIPPED' ? 'text-amber-400' : 'text-sky-400'}`}>{selectedReview.status}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-xs text-muted-foreground block uppercase font-semibold">Linked Entity ID</span>
                  <span className="font-mono text-xs block select-all mt-1">{selectedReview.entity_id}</span>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground block uppercase font-semibold">Due At</span>
                  <span className="font-medium text-base">{new Date(selectedReview.due_at).toLocaleString()}</span>
                </div>
                {selectedReview.completed_at && (
                  <div>
                    <span className="text-xs text-muted-foreground block uppercase font-semibold">Completed At</span>
                    <span className="font-medium text-base">{new Date(selectedReview.completed_at).toLocaleString()}</span>
                  </div>
                )}
              </div>

              {/* Complete Review Form */}
              {selectedReview.status === "PENDING" && (
                <div className="border rounded p-4 bg-card/60 space-y-4">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground border-b pb-2">
                    Execute Review
                  </h4>
                  
                  {formError && (
                    <div className="p-2 text-xs rounded bg-destructive/10 text-destructive border border-destructive/20">
                      {formError}
                    </div>
                  )}
                  {formSuccess && (
                    <div className="p-2 text-xs rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {formSuccess}
                    </div>
                  )}

                  <form onSubmit={handleCompleteReview} className="space-y-4">
                    <div className="space-y-2">
                      <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Notes / Observations (Optional)</label>
                      <textarea
                        rows={3}
                        placeholder="Add summary notes of your review..."
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        className="flex w-full rounded border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
                      />
                    </div>

                    <div className="flex gap-4">
                      <button
                        type="submit"
                        className="h-10 px-4 rounded bg-primary text-primary-foreground font-semibold text-sm hover:bg-primary/90"
                      >
                        Mark Completed
                      </button>
                      <button
                        type="button"
                        onClick={handleSkipReview}
                        className="h-10 px-4 rounded bg-secondary text-secondary-foreground font-semibold text-sm hover:bg-secondary/90"
                      >
                        Skip Review
                      </button>
                    </div>
                  </form>
                </div>
              )}
            </div>
          ) : (
            <div className="border border-dashed rounded-lg p-12 text-center text-muted-foreground bg-card/10">
              Select a review from the left list to see details or execute it.
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
