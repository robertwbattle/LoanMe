'use client';
import { useEffect } from 'react';

declare global {
  namespace JSX {
    interface IntrinsicElements {
      'gecko-coin-price-chart-widget': any;
    }
  }
}

const CoinGeckoWidget = () => {
  useEffect(() => {
    // Load the CoinGecko widget script
    const script = document.createElement('script');
    script.src = 'https://widgets.coingecko.com/gecko-coin-price-chart-widget.js';
    script.async = true;
    document.body.appendChild(script);

    return () => {
      // Cleanup
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div className="w-full h-full">
      <gecko-coin-price-chart-widget 
        locale="en" 
        transparent-background="true" 
        coin-id="solana" 
        initial-currency="usd" 
      />
    </div>
  );
};

export default CoinGeckoWidget;