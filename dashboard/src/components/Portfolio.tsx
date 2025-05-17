import React, { useEffect, useState } from 'react';
import { Box, Table, Thead, Tbody, Tr, Th, Td, Badge, Spinner } from '@chakra-ui/react';
import axios from 'axios';
import TooltipInfo from './TooltipInfo';

interface Balance {
  exchange: string;
  asset: string;
  total: number;
  available: number;
  timestamp: string;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function Portfolio() {
  const [balances, setBalances] = useState<Balance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_URL}/balances`).then((res) => {
      setBalances(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <Box>
      {loading && <Spinner />}
      <Table size="sm" variant="striped" mt={2}>
        <Thead>
          <Tr>
            <Th>Exchange <TooltipInfo label="The exchange where this balance is held." /></Th>
            <Th>Asset <TooltipInfo label="The cryptocurrency or fiat asset." /></Th>
            <Th>Total <TooltipInfo label="Total amount (including locked in orders)." /></Th>
            <Th>Available <TooltipInfo label="Amount available for immediate trading." /></Th>
            <Th>Timestamp <TooltipInfo label="The timestamp of the balance update." /></Th>
          </Tr>
        </Thead>
        <Tbody>
          {balances.map((b, i) => (
            <Tr key={i}>
              <Td><Badge>{b.exchange}</Badge></Td>
              <Td>{b.asset}</Td>
              <Td>{b.total}</Td>
              <Td>{b.available}</Td>
              <Td>{new Date(b.timestamp).toLocaleTimeString()}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
}
