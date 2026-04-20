import React from 'react';

export function Header() {
  return (
    <header style={{
      background: 'rgba(255, 255, 255, 0.05)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      padding: '1.5rem 2rem',
      marginBottom: '2rem',
      backdropFilter: 'blur(10px)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: '700',
            margin: '0',
            background: 'linear-gradient(45deg, #00c896, #0f4c75)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            GrineOS
          </h1>
          <p style={{
            fontSize: '1rem',
            color: '#b0bec5',
            margin: '0.25rem 0 0 0',
            fontWeight: '300'
          }}>
            The Operating System for Capital Allocation
          </p>
        </div>
        <div style={{
          display: 'flex',
          gap: '1rem',
          alignItems: 'center'
        }}>
          <div style={{
            padding: '0.5rem 1rem',
            background: 'rgba(0, 200, 150, 0.2)',
            borderRadius: '6px',
            fontSize: '0.875rem',
            color: '#00c896'
          }}>
            ● System Active
          </div>
          <div style={{
            fontSize: '0.875rem',
            color: '#b0bec5'
          }}>
            Last update: 2 min ago
          </div>
        </div>
      </div>
    </header>
  );
}
