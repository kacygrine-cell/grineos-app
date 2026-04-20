import { useState, useEffect } from 'react';

export function useRegime() {
  const [regimeData, setRegimeData] = useState({
    regime: 'EXPANSION',
    confidence: 0.94,
    duration: 8,
    timestamp: Date.now() - 120000, // 2 minutes ago
    isLoading: false,
    error: null
  });

  // Simulate data fetching
  useEffect(() => {
    const fetchRegimeData = () => {
      // In a real app, this would be an API call
      // For now, we'll simulate regime data
      const regimes = ['EXPANSION', 'BALANCED', 'TRANSITION', 'ENDURANCE', 'PROTECTION'];
      const currentRegime = regimes[Math.floor(Math.random() * regimes.length)];
      
      setRegimeData({
        regime: 'EXPANSION', // Keep consistent for demo
        confidence: 0.94,
        duration: 8,
        timestamp: Date.now() - 120000,
        isLoading: false,
        error: null
      });
    };

    fetchRegimeData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchRegimeData, 30000);
    return () => clearInterval(interval);
  }, []);

  return regimeData;
}

export function useAllocation() {
  const [allocationData, setAllocationData] = useState({
    allocation: {
      equities: 75,
      bonds: 15,
      commodities: 5,
      cash: 5
    },
    regime: 'EXPANSION',
    timestamp: Date.now() - 120000,
    isLoading: false,
    error: null
  });

  useEffect(() => {
    const fetchAllocationData = () => {
      // In a real app, this would be an API call
      setAllocationData({
        allocation: {
          equities: 75,
          bonds: 15,
          commodities: 5,
          cash: 5
        },
        regime: 'EXPANSION',
        timestamp: Date.now() - 120000,
        isLoading: false,
        error: null
      });
    };

    fetchAllocationData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchAllocationData, 30000);
    return () => clearInterval(interval);
  }, []);

  return allocationData;
}

export function useAllocationHistory() {
  const [historyData, setHistoryData] = useState({
    history: [
      {
        id: 1,
        date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
        fromRegime: 'BALANCED',
        toRegime: 'EXPANSION',
        allocation: { equities: 75, bonds: 15, commodities: 5, cash: 5 }
      },
      {
        id: 2,
        date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
        fromRegime: 'TRANSITION',
        toRegime: 'BALANCED',
        allocation: { equities: 60, bonds: 30, commodities: 5, cash: 5 }
      }
    ],
    isLoading: false,
    error: null
  });

  useEffect(() => {
    // In a real app, this would fetch allocation history from an API
    // For now, we'll use mock data
  }, []);

  return historyData;
}

export function useAlignment() {
  const [alignmentData, setAlignmentData] = useState({
    score: 87,
    breakdown: {
      weightDeviation: -2.3,
      regimeConsistency: 94,
      riskBudgetUsage: 78
    },
    recommendations: [
      'Reduce equity allocation by 2.1%',
      'Increase bond allocation by 1.8%',
      'Rebalance within 5 business days'
    ],
    timestamp: Date.now() - 120000,
    isLoading: false,
    error: null
  });

  useEffect(() => {
    const fetchAlignmentData = () => {
      // In a real app, this would be an API call
      setAlignmentData(prev => ({
        ...prev,
        timestamp: Date.now() - 120000
      }));
    };

    fetchAlignmentData();
    
    // Refresh every 60 seconds
    const interval = setInterval(fetchAlignmentData, 60000);
    return () => clearInterval(interval);
  }, []);

  return alignmentData;
}
