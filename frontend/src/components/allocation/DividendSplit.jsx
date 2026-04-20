import React from 'react';

export function DividendSplit({ split }) {
  const pct = (value, decimals = 1) => `${value.toFixed(decimals)}%`;
  
  if (!split || split.equity_total <= 0) return null;
  
  const growthShare = 1 - split.dividend_share;

  return (
    <div style={{
      paddingTop: '2rem',
      borderTop: '1px solid rgba(255,255,255,0.1)',
      marginTop: '2rem'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'baseline',
        justifyContent: 'space-between',
        marginBottom: '0.75rem'
      }}>
        <div style={{
          fontSize: '0.875rem',
          color: '#b0bec5',
          fontWeight: '500'
        }}>
          Equity Composition
        </div>
        <div style={{
          fontSize: '0.75rem',
          color: '#78909c',
          fontFamily: 'monospace'
        }}>
          Regime band: {pct(split.range_lower, 0)} – {pct(split.range_upper, 0)}
        </div>
      </div>
      
      {/* Two-segment bar */}
      <div style={{
        display: 'flex',
        height: '8px',
        borderRadius: '2px',
        overflow: 'hidden',
        background: 'rgba(255,255,255,0.05)'
      }}>
        <div
          style={{
            backgroundColor: '#D4AF37', // Growth - gold light
            width: `${growthShare * 100}%`
          }}
        />
        <div
          style={{
            backgroundColor: '#B8860B', // Dividend - gold dark
            width: `${split.dividend_share * 100}%`
          }}
        />
      </div>
      
      <div style={{
        marginTop: '0.75rem',
        display: 'flex',
        alignItems: 'baseline',
        justifyContent: 'space-between',
        fontSize: '0.875rem'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'baseline',
          gap: '0.5rem'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: '#D4AF37',
            display: 'inline-block'
          }} />
          <span style={{ color: '#b0bec5' }}>Growth</span>
          <span style={{
            fontFamily: 'monospace',
            color: 'white',
            fontWeight: '600'
          }}>
            {pct(split.growth, 1)}
          </span>
          <span style={{
            color: '#78909c',
            fontFamily: 'monospace',
            fontSize: '0.75rem'
          }}>
            ({pct(growthShare, 0)} of equity)
          </span>
        </div>
        
        <div style={{
          display: 'flex',
          alignItems: 'baseline',
          gap: '0.5rem'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: '#B8860B',
            display: 'inline-block'
          }} />
          <span style={{ color: '#b0bec5' }}>Dividend</span>
          <span style={{
            fontFamily: 'monospace',
            color: 'white',
            fontWeight: '600'
          }}>
            {pct(split.dividend, 1)}
          </span>
          <span style={{
            color: '#78909c',
            fontFamily: 'monospace',
            fontSize: '0.75rem'
          }}>
            ({pct(split.dividend_share, 0)} of equity)
          </span>
        </div>
      </div>
    </div>
  );
}
