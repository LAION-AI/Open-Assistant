import { Change } from "diff";
import { withoutRole } from "src/lib/auth";
import { OasstApiClient } from "src/lib/oasst_api_client";
import { createApiClient } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";
import { z } from "zod";

const Body = z.object({
  new_content: z.string(),
  changes: z.array(
    z.object({
      count: z.optional(z.number()),
      value: z.string(),
      added: z.optional(z.boolean()),
      removed: z.optional(z.boolean())
    })
  ),
});

export default withoutRole("banned", async (req, res, token) => {
  const client: OasstApiClient = await createApiClient(token);
  const user = await getBackendUserCore(token.sub);

  const { id: messageId } = req.query;
  const bodyParse = Body.safeParse(req.body.arg);

  if (bodyParse.success) {
    const body = bodyParse.data;
    try {
      await client.propose_revision_to_message(
        messageId as string,
        user,
        body.new_content,
        body.changes as Change[]
      );

      res.status(200).json({ message: 'Successfully created revision proposal to message!' });
    } catch (exception) {
      res.status(500).json({ message: 'Failed to create revision proposal to mesage!' });
    }
  } else {
    res.status(400).json({ 
      message: `Body was not as it should be to create a new revision!` 
    })
  }

});
