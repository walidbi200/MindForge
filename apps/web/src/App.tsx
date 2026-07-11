import { useEffect, useState } from "react";
import { GraphExplorer } from "./components/GraphExplorer";
import { SourcesView } from "./components/SourcesView";
import { CollectionsView } from "./components/CollectionsView";
import { ReviewsView } from "./components/ReviewsView";

interface HealthStatus {
  status: string;
  service: string;
  version: string;
}

export function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isError, setIsError] = useState(false);
  const [currentView, setCurrentView] = useState<"dashboard" | "graph" | "sources" | "collections" | "reviews">("dashboard");

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
        const response = await fetch(`${baseUrl}/api/v1/health`);
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setHealth(data);
        setIsError(false);
      } catch (error) {
        setIsError(true);
      }
    };

    fetchHealth();
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground dark">
      {/* Header */}
      <header className="flex h-14 items-center border-b px-4 lg:px-6">
        <div className="font-semibold text-lg">Ascend</div>
      </header>

      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className="w-64 border-r hidden md:block p-4">
          <nav className="space-y-2 text-sm">
            <button 
              onClick={() => setCurrentView("dashboard")}
              className={`w-full text-left rounded px-3 py-2 font-medium transition-colors ${currentView === 'dashboard' ? 'bg-muted' : 'text-muted-foreground hover:bg-muted/50'}`}
            >
              Dashboard
            </button>
            <div className="rounded px-3 py-2 text-muted-foreground/50 cursor-not-allowed">Capture</div>
            <div className="rounded px-3 py-2 text-muted-foreground/50 cursor-not-allowed">Concepts</div>
            <button 
              onClick={() => setCurrentView("collections")}
              className={`w-full text-left rounded px-3 py-2 font-medium transition-colors ${currentView === 'collections' ? 'bg-muted text-foreground' : 'text-muted-foreground hover:bg-muted/50'}`}
            >
              Collections
            </button>
            <button 
              onClick={() => setCurrentView("sources")}
              className={`w-full text-left rounded px-3 py-2 font-medium transition-colors ${currentView === 'sources' ? 'bg-muted text-foreground' : 'text-muted-foreground hover:bg-muted/50'}`}
            >
              Sources
            </button>
            <button 
              onClick={() => setCurrentView("graph")}
              className={`w-full text-left rounded px-3 py-2 font-medium transition-colors ${currentView === 'graph' ? 'bg-muted text-foreground' : 'text-muted-foreground hover:bg-muted/50'}`}
            >
              Graph Explorer
            </button>
            <button 
              onClick={() => setCurrentView("reviews")}
              className={`w-full text-left rounded px-3 py-2 font-medium transition-colors ${currentView === 'reviews' ? 'bg-muted text-foreground' : 'text-muted-foreground hover:bg-muted/50'}`}
            >
              Reviews
            </button>
          </nav>
        </aside>

        {/* Content */}
        <main className="flex-1 p-6">
          {currentView === "dashboard" && (
            <div className="max-w-4xl mx-auto space-y-6">
              <div>
                <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
                <p className="text-muted-foreground mt-2">
                  Personal Learning Operating System Foundation.
                </p>
              </div>

              {/* Health Status Card */}
              <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">System Status</h3>
                
                <div className="flex items-center gap-4 mb-4">
                  <div 
                    className={`px-3 py-1 text-sm font-medium rounded-full ${
                      health && !isError 
                        ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400" 
                        : "bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-400"
                    }`}
                  >
                    {health && !isError ? "API Online" : "API Offline"}
                  </div>
                </div>

                {health && !isError && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm mt-6">
                    <div>
                      <div className="text-muted-foreground">Service</div>
                      <div className="font-medium mt-1">{health.service}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Version</div>
                      <div className="font-medium mt-1">{health.version}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Status</div>
                      <div className="font-medium mt-1">{health.status}</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {currentView === "graph" && <GraphExplorer />}
          {currentView === "sources" && <SourcesView />}
          {currentView === "collections" && <CollectionsView />}
          {currentView === "reviews" && <ReviewsView />}
        </main>
      </div>
    </div>
  );
}
