import React from 'react';

export function PortfolioAlignment() {
  const alignmentScore = 87;
  const maxScore = 100;
  
  const getScoreColor = (score) => {
    if (score >= 90) return '#00c896';
    if (score >= 70) return '#ff9800';
    return '#f44336';
  };
  
  const getScoreStatus = (score) => {
    if (score >= 90) return { text: '🟢 Fully Aligned', color: '#00c896' };
    if (score >= 70) return { text: '🟡 Well Aligned', color: '#ff9800' };
    return { text: '🔴 Needs Adjustment', color: '#f44336' };
  };

  const scoreColor = getScoreColor(alignmentScore);
  const status = getScoreStatus(alignmentScore);
  const circumference = 2 * Math.PI * 45;
  const strokeDasharray = `${(alignmentScore / 100) * circumference} ${circumference}`;

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{
        position: 'relative',
        display: 'inline-block',
        marginBottom: '1.5rem'
      }}>
        <svg width="120" height="120" style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx="60"
            cy="60"
            r="45"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="8"
            fill="none"
          />
          <circle
            cx="60"
            cy="60"
            r="45"
            stroke={scoreColor}
            strokeWidth="8"
            fill="none"
            strokeDasharray={strokeDasharray}
            strokeLinecap="round"
            style={{
              transition: 'stroke-dasharray 1s ease-in-out'
            }}
          />
        </svg>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '2rem',
            fontWeight: '700',
            color: scoreColor,
            lineHeight: '1'
          }}>
            {alignmentScore}
          </div>
          <div style={{
            fontSize: '0.875rem',
            color: '#b0bec5',
            lineHeight: '1'
          }}>
            / {maxScore}
          </div>
        </div>
      </div>

      <div style={{
        fontSize: '1.1rem',
        fontWeight: '500',
        color: status.color,
        marginBottom: '1.5rem'
      }}>
        {status.text}
      </div>

      <div style={{
        display: 'grid',
        gap: '1rem'
      }}>
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
            Alignment Breakdown
          </h4>
          <div style={{ fontSize: '0.875rem' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.5rem'
            }}>
              <span style={{ color: '#b0bec5' }}>Weight Deviation</span>
              <span style={{ color: '#00c896', fontWeight: '600' }}>-2.3%</span>
            </div>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.5rem'
            }}>
              <span style={{ color: '#b0bec5' }}>Regime Consistency</span>
              <span style={{ color: '#00c896', fontWeight: '600' }}>94%</span>
            </div>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <span style={{ color: '#b0bec5' }}>Risk Budget Usage</span>
              <span style={{ color: '#ff9800', fontWeight: '600' }}>78%</span>
            </div>
          </div>
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
            Recommended Actions
          </h4>
          <div style={{
            fontSize: '0.875rem',
            color: '#b0bec5',
            lineHeight: '1.5'
          }}>
            • Reduce equity allocation by 2.1%<br/>
            • Increase bond allocation by 1.8%<br/>
            • Rebalance within 5 business days
          </div>
        </div>
      </div>
    </div>
  );
}
