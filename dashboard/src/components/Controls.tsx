import React, { useState } from 'react';
import { Box, Button, useToast, VStack, Heading, Switch, FormControl, FormLabel } from '@chakra-ui/react';
import axios from 'axios';
import TooltipInfo from './TooltipInfo';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function Controls() {
  const [killSwitch, setKillSwitch] = useState(false);
  const toast = useToast();

  const handleKillSwitch = async () => {
    try {
      // Call API to toggle kill switch
      await axios.post(`${API_URL}/override/kill`, {
        headers: { 'Content-Type': 'application/json' },
        data: JSON.stringify({ enabled: !killSwitch }),
      });
      setKillSwitch(!killSwitch);
      toast({
        title: `Kill Switch ${!killSwitch ? 'Activated' : 'Deactivated'}`,
        status: !killSwitch ? 'error' : 'success',
        duration: 2500,
        isClosable: true,
      });
    } catch (e) {
      toast({ title: 'Error updating kill switch', status: 'error' });
    }
  };

  return (
    <Box>
      <VStack spacing={4} align="start">
        <Heading size="md">Manual Controls</Heading>
        <FormControl display="flex" alignItems="center">
          <FormLabel htmlFor="kill-switch" mb="0">
            Kill Switch <TooltipInfo label="Instantly halts all trading. Use only in emergencies. When ON, no new trades will be placed or executed." />
          </FormLabel>
          <Switch
            id="kill-switch"
            isChecked={killSwitch}
            onChange={handleKillSwitch}
            colorScheme="red"
          />
        </FormControl>
        <Button mt={4} colorScheme="yellow" onClick={() => toast({ title: 'Manual override not implemented', status: 'info' })}>
          Manual Override <TooltipInfo label="Perform a manual system override (future feature). Use with caution!" />
        </Button>
      </VStack>
    </Box>
  );
}
