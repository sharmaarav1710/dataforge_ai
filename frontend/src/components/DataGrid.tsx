import React, { useState } from 'react';

interface DataGridProps {
  rows: Record<string, any>[];
  columns: { name: string; dtype: string }[];
}

export const DataGrid: React.FC<DataGridProps> = ({ rows, columns }) => {
  const [searchTerm, setSearchTerm] = useState("");

  if (!rows || rows.length === 0) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-8 text-center text-slate-400">
        No row records available to display.
      </div>
    );
  }


  const filteredRows = rows.filter((row) =>
    Object.values(row).some((val) =>
      String(val ?? "").toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h3 className="text-lg font-semibold text-slate-100">Dataset Data Explorer</h3>
        <input
          type="text"
          placeholder="Search records..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-1.5 text-sm text-slate-200 placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60 shadow-xl">
        <div className="max-h-[400px] overflow-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="sticky top-0 bg-slate-900 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3 font-medium">#</th>
                {columns.map((col) => (
                  <th key={col.name} className="px-4 py-3 font-medium">
                    <div className="flex flex-col">
                      <span className="text-slate-200">{col.name}</span>
                      <span className="text-[10px] text-slate-500 font-normal">{col.dtype}</span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredRows.length > 0 ? (
                filteredRows.map((row, index) => (
                  <tr key={index} className="hover:bg-slate-800/40 transition">
                    <td className="px-4 py-3 text-xs text-slate-500 font-mono">{index + 1}</td>
                    {columns.map((col) => {
                      const val = row[col.name];
                      return (
                        <td key={col.name} className="px-4 py-3 font-mono text-xs whitespace-nowrap">
                          {val !== null && val !== undefined ? (
                            String(val)
                          ) : (
                            <span className="text-rose-400/70 italic">null</span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={columns.length + 1} className="px-4 py-8 text-center text-slate-500">
                    No matching records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="border-t border-slate-800 bg-slate-950/40 px-4 py-2.5 text-xs text-slate-400 flex justify-between items-center">
          <span>Showing {filteredRows.length} of {rows.length} rows</span>
          <span className="text-slate-500">Scroll horizontally & vertically to inspect data</span>
        </div>
      </div>
    </div>
  );
};