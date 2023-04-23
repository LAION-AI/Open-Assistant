import { Grid, Heading } from "@chakra-ui/react";
import { TeamMember } from "src/components/TeamMember";

import data from "../../data/warning.json";

const Warning = ({ heading, members }) => {
  const { panels } = data;
  return (
    <>
      <Heading size="sm" mt={3} mb={1} textAlign="center">
        {heading}
      </Heading>
      <Grid gap="6" gridTemplateColumns="repeat(auto-fit, minmax(300px, 1fr))" alignItems="center">
        {members.map((id) => {
          const info = panels[id] ?? {};
          return <TeamMember {...info} key={id} />;
        })}
      </Grid>
    </>
  );
};

export const ChatWarning = () => {
  return (
    <>
      <Warning heading="Usage warning" members={["warning"]} />
    </>
  );
};
