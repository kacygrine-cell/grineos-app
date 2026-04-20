import React from 'react';

export function RecommendedAllocation({ allocQ }) {
  const allocation = allocQ?.allocation || {
    equities: 75,
    bonds: 15,
    commodities: 5,
    cash: 5
  };

  const assets = [
    { name: 'Equities', weight: allocation.equities, color: '#00c896' },
    { name: 'Bonds', weight: allocation.bonds, color: '#2196f3' },
    { name: 'Commodities', weight: allocation.commodities, color: '#ff9800' },
    { name: 'Cash', weight: allocation.cash, color: '#9c27b0' }
  ];

  const maxWeight = Math.max(...assets.map(a => a.weight));

  return (
    <div>
      <div style={{
        display: 'grid',
        gap: '1rem',
        marginBottom: '1.5rem'
      }}>
        {assets.map(asset => (
          <div key={asset.name} style={{
            display: 'grid',
            gridTemplateColumns: '1fr auto',
            alignItems: 'center',
            gap: '1rem',
            padding: '1rem',
            background: 'rgba(255, 255, 255, 0.03)',
            borderRadius: '8px',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div>
              <div style={{
                fontSize: '1rem',
                fontWeight: '500',
                color: 'white',
                marginBottom: '0.25rem'
              }}>
                {asset.name}
              </div>
              <div style={{
                fontSize: '0.875rem',
                color: '#b0bec5'
              }}>
                Strategic weight
              </div>
            </div>
            
            <div style={{
              fontSize: '1.5rem',
              fontWeight: '700',
              color: asset.color
            }}>
              {asset.weight}%
            </div>

            <div style={{
              position: 'absolute',
              bottom: '0',
              left: '0',
              height: '3px',
              width: `${(asset.weight / maxWeight) * 100}%`,
              background: `linear-gradient(90deg, ${asset.color}, ${asset.color}80)`,
              transition: 'width 0.3s ease'
            }} />
          </div>
        ))}
      </div>

      <div style={{
        padding: '1rem',
        background: 'rgba(255,255,255,0.03)',
        borderRadius: '8px',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <h4 style={{
          margin: '0 0 0.75rem 0',
          fontSize: '0.95rem',
          color: 'white',
          fontWeight: '600'
        }}>
          Allocation Summary
        </h4>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '1rem',
          fontSize: '0.875rem'
        }}>
          <div>
            <div style={{ color: '#b0bec5', marginBottom: '0.25rem' }}>Total Risk Assets</div>
            <div style={{ color: '#00c896', fontWeight: '600' }}>{allocation.equities + allocation.commodities}%</div>
          </div>
          <div>
            <div style={{ color: '#b0bec5', marginBottom: '0.25rem' }}>Defensive Assets</div>
            <div style={{ color: '#2196f3', fontWeight: '600' }}>{allocation.bonds + allocation.cash}%</div>
          </div>
        </div>
      </div>
    </div>
  );
}
