import { Grid, Heading } from "@chakra-ui/react";
import { TeamMember } from "src/components/TeamMember";

import data from "../../data/team.json";

const SponsorGroup = ({ heading, members }) => {
  const { people } = data;
  return (
    <>
      <Heading size="sm" mt={3} mb={1}>
        {heading}
      </Heading>
      <Grid gap="6" gridTemplateColumns="repeat(auto-fit, minmax(300px, 1fr))">
        {members.map((id) => {
          const info = people[id] ?? {};
          return <TeamMember {...info} key={id} />;
        })}
      </Grid>
    </>
  );
};

export const InferencePoweredBy = () => {
  return (
    <>
      <SponsorGroup heading="Inference powered by" members={["hf", "stability"]} />
      <SponsorGroup heading="Model training supported by" members={["redmond", "wandb"]} />
    </>
  );
};
