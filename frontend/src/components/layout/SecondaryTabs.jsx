import React from 'react';

export function SecondaryTabs() {
  const tabs = [
    { id: 'overview', label: 'Overview', active: true },
    { id: 'allocation', label: 'Allocation' },
    { id: 'alignment', label: 'Alignment' },
    { id: 'history', label: 'History' },
    { id: 'scenarios', label: 'Scenarios' }
  ];

  return (
    <div style={{
      display: 'flex',
      gap: '0.5rem',
      marginBottom: '2rem',
      padding: '0.5rem',
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '8px',
      border: '1px solid rgba(255, 255, 255, 0.1)'
    }}>
      {tabs.map(tab => (
        <button
          key={tab.id}
          style={{
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderRadius: '6px',
            background: tab.active ? '#0f4c75' : 'transparent',
            color: tab.active ? 'white' : '#b0bec5',
            cursor: 'pointer',
            fontSize: '0.875rem',
            fontWeight: '500',
            transition: 'all 0.2s ease',
            ':hover': {
              background: tab.active ? '#0f4c75' : 'rgba(255, 255, 255, 0.1)'
            }
          }}
          onMouseOver={(e) => {
            if (!tab.active) {
              e.target.style.background = 'rgba(255, 255, 255, 0.1)';
            }
          }}
          onMouseOut={(e) => {
            if (!tab.active) {
              e.target.style.background = 'transparent';
            }
          }}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
