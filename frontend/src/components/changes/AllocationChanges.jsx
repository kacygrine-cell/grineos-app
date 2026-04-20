import React from 'react';

export function AllocationChanges({ historyQ }) {
  const changes = [
    {
      id: 1,
      date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
      fromRegime: 'BALANCED',
      toRegime: 'EXPANSION',
      changes: [
        { asset: 'Equities', from: 60, to: 75, change: '+15%' },
        { asset: 'Bonds', from: 30, to: 15, change: '-15%' },
        { asset: 'Commodities', from: 5, to: 5, change: '0%' },
        { asset: 'Cash', from: 5, to: 5, change: '0%' }
      ]
    },
    {
      id: 2,
      date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      fromRegime: 'TRANSITION',
      toRegime: 'BALANCED',
      changes: [
        { asset: 'Equities', from: 45, to: 60, change: '+15%' },
        { asset: 'Bonds', from: 35, to: 30, change: '-5%' },
        { asset: 'Commodities', from: 15, to: 5, change: '-10%' },
        { asset: 'Cash', from: 5, to: 5, change: '0%' }
      ]
    }
  ];

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getChangeColor = (change) => {
    if (change.startsWith('+')) return '#00c896';
    if (change.startsWith('-')) return '#f44336';
    return '#b0bec5';
  };

  return (
    <div>
      <div style={{
        display: 'grid',
        gap: '1.5rem'
      }}>
        {changes.map((change) => (
          <div key={change.id} style={{
            padding: '1.5rem',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1rem'
            }}>
              <div>
                <div style={{
                  fontSize: '1rem',
                  fontWeight: '600',
                  color: 'white',
                  marginBottom: '0.25rem'
                }}>
                  Regime Transition
                </div>
                <div style={{
                  fontSize: '0.875rem',
                  color: '#b0bec5'
                }}>
                  {formatDate(change.date)}
                </div>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                fontSize: '0.875rem'
              }}>
                <span style={{
                  padding: '0.25rem 0.75rem',
                  background: 'rgba(255,155,0,0.2)',
                  color: '#ff9b00',
                  borderRadius: '4px',
                  fontWeight: '600'
                }}>
                  {change.fromRegime}
                </span>
                <span style={{ color: '#b0bec5' }}>→</span>
                <span style={{
                  padding: '0.25rem 0.75rem',
                  background: 'rgba(0,200,150,0.2)',
                  color: '#00c896',
                  borderRadius: '4px',
                  fontWeight: '600'
                }}>
                  {change.toRegime}
                </span>
              </div>
            </div>

            <div style={{
              display: 'grid',
              gap: '0.75rem'
            }}>
              {change.changes.map((assetChange) => (
                <div key={assetChange.asset} style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr auto auto auto',
                  alignItems: 'center',
                  gap: '1rem',
                  padding: '0.75rem',
                  background: 'rgba(255,255,255,0.02)',
                  borderRadius: '6px'
                }}>
                  <div style={{
                    fontSize: '0.875rem',
                    color: 'white',
                    fontWeight: '500'
                  }}>
                    {assetChange.asset}
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    color: '#b0bec5',
                    textAlign: 'right'
                  }}>
                    {assetChange.from}%
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    color: '#b0bec5',
                    textAlign: 'center'
                  }}>
                    →
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    color: getChangeColor(assetChange.change),
                    fontWeight: '600',
                    textAlign: 'right',
                    minWidth: '50px'
                  }}>
                    {assetChange.to}% ({assetChange.change})
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div style={{
        marginTop: '1.5rem',
        padding: '1rem',
        background: 'rgba(255,255,255,0.03)',
        borderRadius: '8px',
        border: '1px solid rgba(255,255,255,0.1)',
        textAlign: 'center'
      }}>
        <div style={{
          fontSize: '0.875rem',
          color: '#b0bec5',
          lineHeight: '1.5'
        }}>
          Allocation changes are triggered by regime transitions.<br/>
          Historical changes help validate allocation strategy effectiveness.
        </div>
      </div>
    </div>
  );
}
