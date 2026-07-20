// frontend/src/components/VersionTimeline.tsx
import React from 'react';
import { VersionManifest } from '../types/dataset';

interface VersionTimelineProps {
  manifest: VersionManifest | null;
  currentVersionId: string | number;
  onSelectVersion?: (versionId: string) => void;
}

export const VersionTimeline: React.FC<VersionTimelineProps> = ({
  manifest,
  currentVersionId,
  onSelectVersion
}) => {
  if (!manifest) return <div className="p-4 text-gray-400 text-sm">Loading version history...</div>;


  const versionsArray = Object.entries(manifest.versions || {}).map(([vKey, data]: [string, any]) => {
    // Extract numeric string ID if needed, or stick to the key format ("v0", "v1")
    const numericId = vKey.replace('v', '');
    
    return {
      version_id: vKey,
      display_id: numericId,
      created_at: data.created_at || new Date().toISOString(),

      applied_step: data.parent ? {
        issue_type: "Transformation",
        action_taken: data.changes,
        affected_rows_count: data.affected_rows ?? "Unknown"
      } : null
    };
  });

  return (
    <div className="w-80 border-l border-gray-800 bg-gray-900/50 h-full p-4 flex flex-col overflow-y-auto">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-6">
        Dataset Pipeline Tree
      </h3>
      
      <div className="relative border-l-2 border-indigo-500/20 ml-3 pl-6 space-y-6 flex-1">
        {versionsArray.map((version) => {
          const isCurrent = String(version.version_id) === String(currentVersionId) || String(version.display_id) === String(currentVersionId);
          const step = version.applied_step;

          return (
            <div 
              key={version.version_id} 
              className="relative cursor-pointer group transition-all"
              onClick={() => onSelectVersion?.(version.version_id)}
            >
              {/* Timeline Bullet Node */}
              <div className={`absolute -left-[31px] top-1.5 w-3.5 h-3.5 rounded-full border-2 transition-all
                ${isCurrent 
                  ? 'bg-indigo-500 border-indigo-400 shadow-[0_0_10px_rgba(99,102,241,0.6)]' 
                  : 'bg-gray-900 border-gray-700 group-hover:border-indigo-400'
                }`} 
              />
              
              <div className={`p-3 rounded-lg border transition-all ${
                isCurrent 
                  ? 'bg-indigo-950/30 border-indigo-500/40' 
                  : 'bg-gray-800/30 border-transparent hover:bg-gray-800/50 hover:border-gray-700'
              }`}>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-gray-800 text-indigo-300 font-semibold">
                    v{version.display_id}
                  </span>
                  <span className="text-[10px] text-gray-500">
                    {new Date(version.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                
                {step ? (
                  <div>
                    <p className="text-xs font-medium text-gray-200 capitalize">
                      {step.issue_type.replace('_', ' ')} Applied
                    </p>
                    <p className="text-[11px] text-gray-400 mt-1 line-clamp-2 leading-relaxed">
                      {step.action_taken}
                    </p>
                    <div className="mt-2 text-[10px] text-emerald-400 font-medium font-mono">
                      ± {step.affected_rows_count} rows updated
                    </div>
                  </div>
                ) : (
                  <div>
                    <p className="text-xs font-medium text-gray-200">Raw Source Ingested</p>
                    <p className="text-[11px] text-gray-500 mt-0.5">Original immutable state node.</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};