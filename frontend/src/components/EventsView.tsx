import React, { useState, useMemo } from 'react';
import type { SecurityEvent } from '../data/mockData';
import { Search, Download, FileText, ChevronLeft, ChevronRight, Filter } from 'lucide-react';

interface EventsViewProps {
  events: SecurityEvent[];
}

export const EventsView: React.FC<EventsViewProps> = ({ events }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('All');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  // Filtered Events
  const filteredEvents = useMemo(() => {
    return events.filter(e => {
      // Search matches source IP, dest IP, category, hostname, or rule ID
      const matchesSearch = 
        e.src_ip.toLowerCase().includes(searchTerm.toLowerCase()) ||
        e.dest_ip.toLowerCase().includes(searchTerm.toLowerCase()) ||
        e.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
        e.hostname.toLowerCase().includes(searchTerm.toLowerCase()) ||
        e.rule_id.toString().includes(searchTerm);
      
      const matchesSeverity = selectedSeverity === 'All' || e.severity === selectedSeverity;
      
      return matchesSearch && matchesSeverity;
    });
  }, [events, searchTerm, selectedSeverity]);

  // Reset pagination on filter change
  useMemo(() => {
    setCurrentPage(1);
  }, [searchTerm, selectedSeverity]);

  // Pagination bounds
  const totalPages = Math.ceil(filteredEvents.length / itemsPerPage) || 1;
  const paginatedEvents = useMemo(() => {
    const startIdx = (currentPage - 1) * itemsPerPage;
    return filteredEvents.slice(startIdx, startIdx + itemsPerPage);
  }, [filteredEvents, currentPage]);

  // Export CSV Action
  const handleExportCSV = () => {
    const headers = ['Timestamp', 'Host', 'Source IP', 'Destination IP', 'Port', 'Category', 'Rule ID', 'Severity', 'Action'];
    const rows = filteredEvents.map(e => [
      e.timestamp,
      e.hostname,
      e.src_ip,
      e.dest_ip,
      e.dest_port,
      `"${e.category}"`,
      e.rule_id,
      e.severity,
      e.action_taken
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(r => r.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `siem_security_events_${new Date().toISOString().substring(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Export PDF (Interactive Styled Print Window)
  const handleExportPDF = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      alert("Popup blocker prevented report generation. Please allow popups for this site.");
      return;
    }

    const rowsHtml = filteredEvents.map(e => `
      <tr>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 11px;">${e.timestamp}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 11px;">${e.hostname}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 11px;">${e.src_ip}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 11px;">${e.dest_ip}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 11px;">${e.dest_port}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 11px; font-weight: bold;">${e.category}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 11px;">${e.rule_id}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 11px; color: ${
          e.severity === 'Critical' ? '#ef4444' : e.severity === 'High' ? '#f59e0b' : '#06b6d4'
        }">${e.severity}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 11px;">${e.action_taken}</td>
      </tr>
    `).join('');

    printWindow.document.write(`
      <html>
        <head>
          <title>SIEM SOC Security Logs Export</title>
          <style>
            body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; padding: 20px; }
            .header { border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 20px; }
            .logo { font-size: 20px; font-weight: bold; color: #0f172a; }
            .meta { font-size: 12px; color: #666; margin-top: 5px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th { background-color: #f1f5f9; padding: 10px; border-bottom: 2px solid #cbd5e1; text-align: left; font-size: 11px; text-transform: uppercase; color: #475569; }
          </style>
        </head>
        <body>
          <div class="header">
            <div class="logo">SOC-AI CYBERSECURITY PLATFORM</div>
            <div class="meta">
              <strong>Exported by:</strong> rayane-virtual-machine <br/>
              <strong>Date:</strong> ${new Date().toLocaleString()} <br/>
              <strong>Total Records:</strong> ${filteredEvents.length} logs matching filters
            </div>
          </div>
          <h3>System Security Log Directory</h3>
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Host</th>
                <th>Source IP</th>
                <th>Destination IP</th>
                <th>Port</th>
                <th>Category</th>
                <th>Rule ID</th>
                <th>Severity</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${rowsHtml}
            </tbody>
          </table>
          <script>
            window.onload = function() {
              window.print();
            };
          </script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Table Toolbar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
        
        {/* Search */}
        <div style={{ position: 'relative', minWidth: '280px', flexGrow: 1 }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search by IP, Category, Host, Rule ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="glow-border-cyan"
            style={{
              width: '100%',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-primary)',
              borderRadius: '8px',
              padding: '10px 16px 10px 38px',
              color: '#ffffff',
              fontSize: '0.875rem'
            }}
          />
        </div>

        {/* Severity Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={14} style={{ color: 'var(--text-secondary)' }} />
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginRight: '4px' }}>Sévérité:</span>
          {['All', 'Critical', 'High', 'Medium', 'Low'].map(sev => (
            <button
              key={sev}
              onClick={() => setSelectedSeverity(sev)}
              style={{
                fontSize: '0.75rem',
                padding: '6px 12px',
                borderRadius: '6px',
                border: '1px solid',
                cursor: 'pointer',
                transition: 'all 0.2s',
                backgroundColor: selectedSeverity === sev ? 'rgba(6, 182, 212, 0.15)' : 'rgba(15, 23, 42, 0.4)',
                color: selectedSeverity === sev ? 'var(--cyan)' : 'var(--text-secondary)',
                borderColor: selectedSeverity === sev ? 'var(--cyan)' : 'var(--border-primary)'
              }}
            >
              {sev === 'All' ? 'Tous' : sev}
            </button>
          ))}
        </div>

        {/* Exports */}
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handleExportCSV} className="btn-secondary" style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Download size={14} /> CSV
          </button>
          <button onClick={handleExportPDF} className="btn-secondary" style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <FileText size={14} /> PDF
          </button>
        </div>

      </div>

      {/* Main Table */}
      <div style={{ overflowX: 'auto', border: '1px solid var(--border-primary)', borderRadius: '8px' }}>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Horodatage</th>
              <th>Hôte</th>
              <th>Source IP</th>
              <th>Destination IP</th>
              <th>Port</th>
              <th>Catégorie</th>
              <th>Règle ID</th>
              <th>Sévérité</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {paginatedEvents.length > 0 ? (
              paginatedEvents.map(e => (
                <tr key={e.id}>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{e.timestamp}</td>
                  <td style={{ fontWeight: 500 }}>{e.hostname}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{e.src_ip}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{e.dest_ip}</td>
                  <td style={{ color: 'var(--text-secondary)' }}>{e.dest_port}</td>
                  <td style={{ fontWeight: 600 }}>{e.category}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{e.rule_id}</td>
                  <td>
                    <span style={{
                      fontSize: '0.7rem',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: '4px',
                      backgroundColor: e.severity === 'Critical' ? 'rgba(239, 68, 68, 0.15)' : e.severity === 'High' ? 'rgba(245, 158, 11, 0.15)' : e.severity === 'Medium' ? 'rgba(6, 182, 212, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                      color: e.severity === 'Critical' ? 'var(--red)' : e.severity === 'High' ? 'var(--amber)' : e.severity === 'Medium' ? 'var(--cyan)' : 'var(--emerald)'
                    }}>
                      {e.severity}
                    </span>
                  </td>
                  <td style={{ 
                    color: e.action_taken === 'Dropped' || e.action_taken === 'Blocked' || e.action_taken === 'Killed' ? 'var(--red)' : e.action_taken === 'Allowed' ? 'var(--emerald)' : 'var(--amber)',
                    fontWeight: 500,
                    fontSize: '0.8rem'
                  }}>
                    {e.action_taken}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                  Aucun log de sécurité ne correspond aux filtres.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, filteredEvents.length)} of {filteredEvents.length} events
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              className="btn-secondary"
              style={{ padding: '6px 10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            >
              <ChevronLeft size={16} />
            </button>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-primary)', fontWeight: 600 }}>
              {currentPage} / {totalPages}
            </span>
            <button
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              className="btn-secondary"
              style={{ padding: '6px 10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

    </div>
  );
};
