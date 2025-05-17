import React from 'react';
import { Box, Container, Heading, Tab, TabList, TabPanel, TabPanels, Tabs } from '@chakra-ui/react';
import Opportunities from './components/Opportunities';
import Portfolio from './components/Portfolio';
import Health from './components/Health';
import Controls from './components/Controls';
import AuditLog from './components/AuditLog';

function App() {
  return (
    <Container maxW="container.xl" py={4}>
      <Heading mb={6}>Crypto Arbitrage Dashboard</Heading>
      <Tabs variant="enclosed" colorScheme="teal">
        <TabList>
          <Tab>Opportunities</Tab>
          <Tab>Portfolio</Tab>
          <Tab>Health</Tab>
          <Tab>Controls</Tab>
          <Tab>Audit Log</Tab>
        </TabList>
        <TabPanels>
          <TabPanel><Opportunities /></TabPanel>
          <TabPanel><Portfolio /></TabPanel>
          <TabPanel><Health /></TabPanel>
          <TabPanel><Controls /></TabPanel>
          <TabPanel><AuditLog /></TabPanel>
        </TabPanels>
      </Tabs>
    </Container>
  );
}

export default App;
