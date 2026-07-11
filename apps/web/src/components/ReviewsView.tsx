import { useState, useEffect } from "react";

interface Review {
  id: string;
  entity_id: string;
  entity_type: string;
  review_type: string;
  status: string;
  difficulty: string;
  score: number;
  notes: string;
  created_at: string;
  updated_at: string;
  last_reviewed_at: string | null;
  next_review_at: string | null;
}

export function ReviewsView() {
  const [allReviews, setAllReviews] = useState<Review[]>([]);
  const [dueReviews, setDueReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Selected Review details
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedReview, setSelectedReview] = useState<Review | null>(null);

  // Complete review form state
  const [score, setScore] = useState(3);
  const [difficulty, setDifficulty] = useState("MEDIUM");
  const [notes, setNotes] = useState("");
  const [formError, setFormError] = useState("");
  const [formSuccess, setFormSuccess] = useState("");

  // Create review form state
  const [newEntityId, setNewEntityId] = useState("");
  const [newEntityType, setNewEntityType] = useState("Capture");
  const [newReviewType, setNewReviewType] = useState("READ");
  const [createError, setCreateError] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  const fetchAllData = async () => {
    setLoading(true);
    setError("");
    try {
      const [resAll, resDue] = await Promise.all([
        fetch(`${baseUrl}/api/v1/reviews`),
        fetch(`${baseUrl}/api/v1/reviews/due`)
      ]);

      if (!resAll.ok || !resDue.ok) throw new Error("Failed to fetch reviews");

      const allData = await resAll.json();
      const dueData = await resDue.json();

      setAllReviews(allData);
      setDueReviews(dueData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const handleSelectReview = async (id: string) => {
    setSelectedId(id);
    setFormError("");
    setFormSuccess("");
    try {
      const res = await fetch(`${baseUrl}/api/v1/reviews/${id}`);
      if (!res.ok) throw new Error("Failed to load review details");
      const data = await res.json();
      setSelectedReview(data);
      // pre-fill completion notes if any
      setNotes(data.notes || "");
      setDifficulty(data.difficulty || "MEDIUM");
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleCreateReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateError("");
    if (!newEntityId.trim()) return;

    try {
      const res = await fetch(`${baseUrl}/api/v1/reviews`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          entity_id: newEntityId.trim(),
          entity_type: newEntityType,
          review_type: newReviewType,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to create review");
      }

      setNewEntityId("");
      setIsCreating(false);
      fetchAllData();
    } catch (err: any) {
      setCreateError(err.message);
    }
  };

  const handleCompleteReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedId) return;
    setFormError("");
    setFormSuccess("");

    try {
      const res = await fetch(`${baseUrl}/api/v1/reviews/${selectedId}/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          difficulty,
          score,
          notes,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to complete review");
      }

      const updated = await res.json();
      setSelectedReview(updated);
      setFormSuccess("Review completed successfully!");
      fetchAllData();
    } catch (err: any) {
      setFormError(err.message);
    }
  };

  const handleDeleteReview = async (id: string) => {
    if (!confirm("Are you sure you want to delete this review target?")) return;
    try {
      const res = await fetch(`${baseUrl}/api/v1/reviews/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete review");
      if (selectedId === id) {
        setSelectedId(null);
        setSelectedReview(null);
      }
      fetchAllData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Grouping client-side for sections
  const nowStr = new Date().toISOString();
  const completedReviews = allReviews.filter((r) => r.last_reviewed_at !== null);
  const upcomingReviews = allReviews.filter(
    (r) => r.next_review_at && r.next_review_at > nowStr && r.status !== "MASTERED"
  );

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Active Recall (Reviews)</h1>
          <p className="text-muted-foreground mt-2">
            Schedule and perform recall/spaced repetition tasks on captures, concepts, and sources.
          </p>
        </div>
        {!isCreating && (
          <button
            onClick={() => setIsCreating(true)}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          >
            Create Review Target
          </button>
        )}
      </div>

      {error && (
        <div className="p-4 rounded bg-destructive/10 text-destructive border border-destructive/20 text-sm">
          {error}
        </div>
      )}

      {isCreating && (
        <div className="rounded-lg border bg-card p-6 shadow-sm space-y-4">
          <h3 className="text-lg font-semibold">Create Review Target</h3>
          {createError && (
            <div className="p-3 text-xs rounded bg-destructive/10 text-destructive border border-destructive/20">
              {createError}
            </div>
          )}
          <form onSubmit={handleCreateReview} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Entity Type</label>
                <select
                  value={newEntityType}
                  onChange={(e) => setNewEntityType(e.target.value)}
                  className="flex h-10 w-full rounded border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="Capture">Capture</option>
                  <option value="Concept">Concept</option>
                  <option value="Source">Source</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Review Type</label>
                <select
                  value={newReviewType}
                  onChange={(e) => setNewReviewType(e.target.value)}
                  className="flex h-10 w-full rounded border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="READ">READ</option>
                  <option value="RECALL">RECALL</option>
                  <option value="FLASHCARD">FLASHCARD</option>
                  <option value="QUIZ">QUIZ</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Entity UUID *</label>
                <input
                  type="text"
                  required
                  placeholder="Enter Entity UUID"
                  value={newEntityId}
                  onChange={(e) => setNewEntityId(e.target.value)}
                  className="flex h-10 w-full rounded border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setIsCreating(false)}
                className="h-10 px-4 rounded border font-medium text-sm hover:bg-accent"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="h-10 px-4 rounded bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90"
              >
                Save Target
              </button>
            </div>
          </form>
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
                      <span className="text-rose-400">[{r.review_type}]</span>
                      <span className="uppercase text-[9px] bg-muted px-1 rounded text-muted-foreground">{r.entity_type}</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground font-mono truncate">Entity ID: {r.entity_id}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Section 2: Upcoming Reviews */}
          <div className="space-y-2">
            <h3 className="text-sm font-bold text-sky-500 uppercase tracking-wider flex justify-between items-center">
              <span>Upcoming Reviews</span>
              <span className="text-xs px-2 py-0.5 rounded bg-sky-500/10 font-mono">{upcomingReviews.length}</span>
            </h3>
            {loading ? null : upcomingReviews.length === 0 ? (
              <p className="text-xs text-muted-foreground border border-dashed rounded p-3 text-center">
                No upcoming reviews scheduled.
              </p>
            ) : (
              <div className="space-y-2">
                {upcomingReviews.map((r) => (
                  <div
                    key={r.id}
                    onClick={() => handleSelectReview(r.id)}
                    className={`p-3 rounded border bg-card/40 cursor-pointer hover:bg-card/80 transition-all ${
                      selectedId === r.id ? "ring-1 ring-ring bg-card" : ""
                    }`}
                  >
                    <div className="flex justify-between items-center text-xs font-semibold mb-1">
                      <span className="text-sky-400">[{r.review_type}]</span>
                      <span className="uppercase text-[9px] bg-muted px-1 rounded text-muted-foreground">{r.entity_type}</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground font-mono truncate">Entity ID: {r.entity_id}</p>
                    <p className="text-[9px] text-muted-foreground/60 mt-1">Due: {new Date(r.next_review_at!).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Section 3: Completed Reviews */}
          <div className="space-y-2">
            <h3 className="text-sm font-bold text-emerald-500 uppercase tracking-wider flex justify-between items-center">
              <span>Completed Reviews</span>
              <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 font-mono">{completedReviews.length}</span>
            </h3>
            {loading ? null : completedReviews.length === 0 ? (
              <p className="text-xs text-muted-foreground border border-dashed rounded p-3 text-center">
                No completed reviews yet.
              </p>
            ) : (
              <div className="space-y-2">
                {completedReviews.map((r) => (
                  <div
                    key={r.id}
                    onClick={() => handleSelectReview(r.id)}
                    className={`p-3 rounded border bg-card/20 cursor-pointer hover:bg-card/60 transition-all ${
                      selectedId === r.id ? "ring-1 ring-ring bg-card" : ""
                    }`}
                  >
                    <div className="flex justify-between items-center text-xs font-semibold mb-1">
                      <span className="text-emerald-400">[{r.review_type}]</span>
                      <span className="uppercase text-[9px] bg-muted px-1 rounded text-muted-foreground">{r.entity_type}</span>
                    </div>
                    <div className="flex justify-between items-center text-[10px] text-muted-foreground mt-1">
                      <span>Score: {r.score}/5</span>
                      <span>Difficulty: {r.difficulty}</span>
                    </div>
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
                    <span className="text-sky-400">[{selectedReview.review_type}]</span>
                    <span>Review Target</span>
                  </h3>
                  <p className="text-xs text-muted-foreground font-mono mt-1">Review ID: {selectedReview.id}</p>
                </div>
                <button
                  onClick={() => handleDeleteReview(selectedReview.id)}
                  className="text-xs text-destructive hover:underline"
                >
                  Delete Target
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
                  <span className="font-medium text-base text-sky-400">{selectedReview.status}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-xs text-muted-foreground block uppercase font-semibold">Linked Entity ID</span>
                  <span className="font-mono text-xs block select-all mt-1">{selectedReview.entity_id}</span>
                </div>
              </div>

              {/* Complete Review Form */}
              <div className="border rounded p-4 bg-card/60 space-y-4">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground border-b pb-2">
                  Log Review Execution
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
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Difficulty</label>
                      <select
                        value={difficulty}
                        onChange={(e) => setDifficulty(e.target.value)}
                        className="flex h-10 w-full rounded border border-input bg-background px-3 py-2 text-sm"
                      >
                        <option value="VERY_EASY">VERY EASY</option>
                        <option value="EASY">EASY</option>
                        <option value="MEDIUM">MEDIUM</option>
                        <option value="HARD">HARD</option>
                        <option value="VERY_HARD">VERY HARD</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Recall Score (0-5)</label>
                      <input
                        type="number"
                        min="0"
                        max="5"
                        value={score}
                        onChange={(e) => setScore(parseInt(e.target.value) || 0)}
                        className="flex h-10 w-full rounded border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Notes / Observations</label>
                    <textarea
                      rows={3}
                      placeholder="Add summary notes of your recall practice..."
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="flex w-full rounded border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
                    />
                  </div>

                  <button
                    type="submit"
                    className="h-10 px-4 rounded bg-primary text-primary-foreground font-semibold text-sm hover:bg-primary/90"
                  >
                    Submit Execution
                  </button>
                </form>
              </div>

              {/* Execution History Stats */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center border-t pt-4 text-sm">
                <div>
                  <span className="text-xs text-muted-foreground block uppercase">Last Executed</span>
                  <span className="font-semibold block mt-1">
                    {selectedReview.last_reviewed_at 
                      ? new Date(selectedReview.last_reviewed_at).toLocaleDateString()
                      : "Never"}
                  </span>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground block uppercase">Next Scheduled</span>
                  <span className="font-semibold block mt-1 text-sky-400">
                    {selectedReview.next_review_at 
                      ? new Date(selectedReview.next_review_at).toLocaleDateString()
                      : "Due Now"}
                  </span>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground block uppercase">Difficulty Rating</span>
                  <span className="font-semibold block mt-1">{selectedReview.difficulty}</span>
                </div>
              </div>

            </div>
          ) : (
            <div className="border border-dashed rounded-lg p-12 text-center text-muted-foreground bg-card/10">
              Select a review target from the left list to run recall practices and log performance scores.
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
