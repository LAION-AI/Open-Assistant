import { Accordion, AccordionButton, AccordionItem, AccordionPanel, IconButton } from "@chakra-ui/react";
import { Sliders } from "lucide-react";
import { memo } from "react";
import { JsonCard } from "src/components/JsonCard";
import { InferenceMessage } from "src/types/Chat";

export const WorkParametersDisplay = memo(function WorkParametersDisplay({
  parameters,
}: {
  parameters: InferenceMessage["work_parameters"];
}) {
  return (
    <Accordion allowToggle>
      <AccordionItem border="none">
        <AccordionButton as={IconButton} icon={<Sliders />} bg="inherit" />
        <AccordionPanel>
          <JsonCard>{parameters}</JsonCard>
        </AccordionPanel>
      </AccordionItem>
    </Accordion>
  );
});
