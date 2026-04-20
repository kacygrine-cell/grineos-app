import React from 'react';

export function AllocationBand({
  label,
  weight,
  target,
  range,
  color,
  max = 1,
}) {
  const scale = (v) => (v / max) * 100;
  
  const pct = (value, decimals = 1) => `${value.toFixed(decimals)}%`;
  
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '90px 1fr 90px',
      gap: '1.5rem',
      alignItems: 'center',
      marginBottom: '1rem'
    }}>
      {/* Label */}
      <div style={{
        fontSize: '0.875rem',
        color: '#b0bec5',
        fontWeight: '500'
      }}>
        {label}
      </div>
      
      {/* Track with band and weight marker */}
      <div style={{
        position: 'relative',
        height: '2rem'
      }}>
        {/* Background scale line */}
        <div style={{
          position: 'absolute',
          left: '0',
          right: '0',
          top: '50%',
          transform: 'translateY(-50%)',
          height: '1px',
          background: 'rgba(255,255,255,0.2)'
        }} />
        
        {/* Constraint band */}
        <div style={{
          position: 'absolute',
          top: '50%',
          transform: 'translateY(-50%)',
          left: `${scale(range.lower)}%`,
          width: `${scale(range.upper - range.lower)}%`,
          height: '6px',
          borderRadius: '2px',
          backgroundColor: color,
          opacity: 0.18
        }} />
        
        {/* Band edges */}
        <div style={{
          position: 'absolute',
          top: '50%',
          transform: 'translateY(-50%)',
          left: `${scale(range.lower)}%`,
          width: '1px',
          height: '10px',
          backgroundColor: color,
          opacity: 0.5
        }} />
        <div style={{
          position: 'absolute',
          top: '50%',
          transform: 'translateY(-50%)',
          left: `${scale(range.upper)}%`,
          width: '1px',
          height: '10px',
          backgroundColor: color,
          opacity: 0.5
        }} />
        
        {/* Target marker (pre-turnover) — light dashed tick */}
        <div style={{
          position: 'absolute',
          top: '50%',
          transform: 'translateY(-50%)',
          left: `${scale(target)}%`,
          width: '1px',
          height: '18px',
          borderLeft: `1px dashed ${color}`,
          opacity: 0.4
        }} />
        
        {/* Weight tick — solid, dominant */}
        <div style={{
          position: 'absolute',
          top: '50%',
          transform: 'translateY(-50%)',
          left: `${scale(weight)}%`,
          width: '2px',
          height: '22px',
          backgroundColor: color
        }} />
        
        {/* Range labels */}
        <div style={{
          position: 'absolute',
          bottom: '-2px',
          left: `${scale(range.lower)}%`,
          transform: 'translateX(-50%)',
          fontFamily: 'monospace',
          fontSize: '10px',
          color: '#78909c'
        }}>
          {pct(range.lower, 0)}
        </div>
        <div style={{
          position: 'absolute',
          bottom: '-2px',
          left: `${scale(range.upper)}%`,
          transform: 'translateX(-50%)',
          fontFamily: 'monospace',
          fontSize: '10px',
          color: '#78909c'
        }}>
          {pct(range.upper, 0)}
        </div>
      </div>
      
      {/* Weight value */}
      <div style={{
        textAlign: 'right'
      }}>
        <div style={{
          fontSize: '1.5rem',
          fontWeight: '500',
          color: 'white',
          lineHeight: '1',
          fontFamily: 'monospace'
        }}>
          {pct(weight, 1)}
        </div>
      </div>
    </div>
  );
}

export function AllocationBandLegend() {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '1.25rem',
      fontSize: '0.75rem',
      color: '#78909c',
      marginTop: '1rem'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
      }}>
        <span style={{
          display: 'block',
          width: '12px',
          height: '6px',
          backgroundColor: 'white',
          borderRadius: '2px',
          opacity: 0.2
        }} />
        <span>Band</span>
      </div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
      }}>
        <span style={{
          display: 'block',
          width: '1px',
          height: '12px',
          borderLeft: '1px dashed #78909c'
        }} />
        <span>Target</span>
      </div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
      }}>
        <span style={{
          display: 'block',
          width: '2px',
          height: '12px',
          backgroundColor: 'white'
        }} />
        <span>Recommended</span>
      </div>
    </div>
  );
}
