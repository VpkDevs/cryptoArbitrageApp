import React, { useEffect, useState } from 'react';
import { Box, Table, Thead, Tbody, Tr, Th, Td, Badge, Spinner } from '@chakra-ui/react';
import axios from 'axios';
import TooltipInfo from './TooltipInfo';

interface HealthStatus {
  status: string;
  [key: string]: any;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function Health() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_URL}/health`).then((res) => {
      setHealth(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <Box>
      {loading && <Spinner />}
      {health && (
        <Table size="sm" variant="striped" mt={2}>
          <Thead>
            <Tr>
              <Th>API Status <TooltipInfo label="Current health: green = healthy, red = action needed." /></Th>
            </Tr>
          </Thead>
          <Tbody>
            <Tr>
              <Td>
                <Badge colorScheme={health.status === 'ok' ? 'green' : 'red'}>{health.status}</Badge>
              </Td>
            </Tr>
          </Tbody>
        </Table>
      )}
    </Box>
  );
}
