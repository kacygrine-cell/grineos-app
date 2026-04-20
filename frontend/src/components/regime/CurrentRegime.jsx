import React from 'react';

export function CurrentRegime({ regimeQ }) {
  const regime = regimeQ?.regime || 'EXPANSION';
  
  const regimeConfig = {
    EXPANSION: { 
      color: '#00c896', 
      background: 'linear-gradient(45deg, #00c896, #4caf50)',
      description: 'Growth conditions with strong fundamentals'
    },
    BALANCED: { 
      color: '#2196f3', 
      background: 'linear-gradient(45deg, #2196f3, #03a9f4)',
      description: 'Stable conditions with moderate growth'
    },
    TRANSITION: { 
      color: '#ff9800', 
      background: 'linear-gradient(45deg, #ff9800, #ffc107)',
      description: 'Changing conditions requiring flexibility'
    },
    ENDURANCE: { 
      color: '#ff5722', 
      background: 'linear-gradient(45deg, #ff5722, #f44336)',
      description: 'Challenging conditions requiring resilience'
    },
    PROTECTION: { 
      color: '#9c27b0', 
      background: 'linear-gradient(45deg, #9c27b0, #673ab7)',
      description: 'Defensive conditions with capital preservation focus'
    }
  };

  const config = regimeConfig[regime] || regimeConfig.EXPANSION;

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{
        display: 'inline-block',
        padding: '1rem 2rem',
        borderRadius: '12px',
        background: config.background,
        marginBottom: '1rem',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
      }}>
        <div style={{
          fontSize: '2rem',
          fontWeight: '700',
          color: 'white',
          marginBottom: '0.25rem',
          textTransform: 'uppercase',
          letterSpacing: '1px'
        }}>
          {regime}
        </div>
        <div style={{
          fontSize: '0.875rem',
          color: 'rgba(255,255,255,0.9)',
          fontWeight: '500'
        }}>
          Current Market Regime
        </div>
      </div>
      
      <p style={{
        fontSize: '0.95rem',
        color: '#b0bec5',
        lineHeight: '1.5',
        margin: '0',
        maxWidth: '280px',
        marginLeft: 'auto',
        marginRight: 'auto'
      }}>
        {config.description}
      </p>
      
      <div style={{
        marginTop: '1.5rem',
        padding: '1rem',
        background: 'rgba(255,255,255,0.03)',
        borderRadius: '8px',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '1rem',
          fontSize: '0.875rem'
        }}>
          <div>
            <div style={{ color: '#b0bec5', marginBottom: '0.25rem' }}>Confidence</div>
            <div style={{ color: config.color, fontWeight: '600' }}>94%</div>
          </div>
          <div>
            <div style={{ color: '#b0bec5', marginBottom: '0.25rem' }}>Duration</div>
            <div style={{ color: 'white', fontWeight: '600' }}>8 weeks</div>
          </div>
        </div>
      </div>
    </div>
  );
}
