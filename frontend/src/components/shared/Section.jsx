import React from 'react';

export function Section({ children, title, subtitle }) {
  return (
    <section style={{
      background: 'rgba(255, 255, 255, 0.05)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      padding: '1.5rem',
      backdropFilter: 'blur(10px)',
      height: 'fit-content'
    }}>
      {(title || subtitle) && (
        <header style={{ marginBottom: '1.5rem' }}>
          {title && (
            <h2 style={{
              fontSize: '1.3rem',
              margin: '0 0 0.25rem 0',
              color: 'white',
              fontWeight: '600'
            }}>
              {title}
            </h2>
          )}
          {subtitle && (
            <p style={{
              fontSize: '0.875rem',
              color: '#b0bec5',
              margin: '0',
              fontWeight: '400'
            }}>
              {subtitle}
            </p>
          )}
        </header>
      )}
      {children}
    </section>
  );
}
