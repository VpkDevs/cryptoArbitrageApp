import React, { useEffect, useState } from 'react';
import { Box, Table, Thead, Tbody, Tr, Th, Td, Badge, Spinner } from '@chakra-ui/react';
import TooltipInfo from './TooltipInfo';

interface Opportunity {
  type: string;
  symbol: string;
  est_profit_pct: number;
  est_profit_abs: number;
  risk_score: number;
  detected_at: string;
  legs: Array<{
    exchange: string;
    symbol: string;
    side: string;
    price: number;
    size: number;
    strategy: string;
  }>;
}

const WS_URL = process.env.REACT_APP_API_URL?.replace(/^http/, 'ws') + '/ws/opportunities';

export default function Opportunities() {
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ws: WebSocket | null = null;
    if (WS_URL) {
      ws = new WebSocket(WS_URL);
      ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        setOpps((prev) => [data, ...prev].slice(0, 100));
        setLoading(false);
      };
      ws.onerror = () => setLoading(false);
    }
    return () => ws && ws.close();
  }, []);

  return (
    <Box>
      {loading && <Spinner />}
      <Table size="sm" variant="striped" mt={2}>
        <Thead>
          <Tr>
            <Th>Type <TooltipInfo label="Type of arbitrage: spatial (cross-exchange), triangular (within-exchange loop), or statistical (spread/mean-reversion)." /></Th>
            <Th>Symbol <TooltipInfo label="Asset or asset-pair involved in the opportunity." /></Th>
            <Th>Profit (%) <TooltipInfo label="Estimated profit percentage after fees and costs." /></Th>
            <Th>Profit ($) <TooltipInfo label="Estimated absolute profit in USD after fees and costs." /></Th>
            <Th>Risk <TooltipInfo label="Risk score: higher means more risk due to volatility, liquidity, or system health." /></Th>
            <Th>Detected <TooltipInfo label="Timestamp when this opportunity was detected." /></Th>
            <Th>Legs <TooltipInfo label="Sequence of trades needed to capture this arbitrage. Hover for details." /></Th>
          </Tr>
        </Thead>
        <Tbody>
          {opps.map((o, i) => (
            <Tr key={i}>
              <Td><Badge colorScheme="teal">{o.type}</Badge></Td>
              <Td>{o.symbol}</Td>
              <Td>{o.est_profit_pct.toFixed(3)}</Td>
              <Td>{o.est_profit_abs.toFixed(2)}</Td>
              <Td>{o.risk_score.toFixed(2)}</Td>
              <Td>{new Date(o.detected_at).toLocaleTimeString()}</Td>
              <Td>{o.legs.map((l, j) => (
                <Box as="span" key={j} mr={2}>
                  <TooltipInfo label={`Leg ${j+1}: ${l.side.toUpperCase()} ${l.size} ${l.symbol} on ${l.exchange} at $${l.price} (strategy: ${l.strategy})`} />
                  <Badge colorScheme={l.side === 'buy' ? 'green' : 'red'}>{l.side.toUpperCase()}</Badge> {l.exchange} {l.symbol} @{l.price}
                </Box>
              ))}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
}
