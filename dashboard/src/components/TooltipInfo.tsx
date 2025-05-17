import React from 'react';
import { Tooltip, IconButton } from '@chakra-ui/react';
import { InfoOutlineIcon } from '@chakra-ui/icons';

interface TooltipInfoProps {
  label: string;
}

export default function TooltipInfo({ label }: TooltipInfoProps) {
  return (
    <Tooltip label={label} placement="top" hasArrow>
      <span>
        <IconButton
          aria-label="info"
          icon={<InfoOutlineIcon />}
          size="xs"
          variant="ghost"
          colorScheme="teal"
          tabIndex={-1}
        />
      </span>
    </Tooltip>
  );
}
