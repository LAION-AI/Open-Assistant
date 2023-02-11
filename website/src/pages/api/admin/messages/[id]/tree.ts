import { withAnyRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import { Message, MessageWithChildren } from "src/types/Conversation";

export default withAnyRole(["admin", "moderator"], async (req, res, token) => {
  const client = await createApiClient(token);
  const messageId = req.query.id as string;
  const response = await client.fetch_message_tree(messageId);

  if (!response) {
    return res.json({ tree: null });
  }

  const tree = buildTree(response.messages);

  return res.json({ tree, message: response.messages.find((m) => m.id === messageId) });
});

// https://medium.com/@lizhuohang.selina/building-a-hierarchical-tree-from-a-flat-list-an-easy-to-understand-solution-visualisation-19cb24bdfa33
const buildTree = (messages: Message[]): MessageWithChildren | null => {
  const map: Record<string, MessageWithChildren> = {};
  const tree = [];

  // Build a hash table and map items to objects
  messages.forEach(function (item) {
    const id = item.id;
    if (!map[id]) {
      map[id] = { ...item, children: [] };
    }
  });

  // Loop over hash table
  let mappedElem: MessageWithChildren;
  for (const id in map) {
    if (map[id]) {
      mappedElem = map[id];

      // If the element is not at the root level, add it to its parent array of children. Note this will continue till we have only root level elements left
      if (mappedElem.parent_id) {
        const parentId = mappedElem.parent_id;
        map[parentId].children.push(mappedElem);
      }

      // If the element is at the root level, directly push to the tree
      else {
        tree.push(mappedElem);
      }
    }
  }

  return tree.shift() || null;
};
