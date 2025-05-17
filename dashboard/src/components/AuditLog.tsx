import React, { useEffect, useState } from 'react';
import { Box, Table, Thead, Tbody, Tr, Th, Td, Spinner } from '@chakra-ui/react';
import axios from 'axios';

interface AuditEntry {
  timestamp: string;
  event: string;
  details: string;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function AuditLog() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_URL}/audit`).then((res) => {
      setEntries(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <Box>
      {loading && <Spinner />}
      <Table size="sm" variant="striped" mt={2}>
        <Thead>
          <Tr>
            <Th>Time</Th>
            <Th>Event</Th>
            <Th>Details</Th>
          </Tr>
        </Thead>
        <Tbody>
          {entries.map((e, i) => (
            <Tr key={i}>
              <Td>{new Date(e.timestamp).toLocaleString()}</Td>
              <Td>{e.event}</Td>
              <Td>{e.details}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
}
