export type Tree<T> = T & { children: Tree<T>[] };

// https://medium.com/@lizhuohang.selina/building-a-hierarchical-tree-from-a-flat-list-an-easy-to-understand-solution-visualisation-19cb24bdfa33
export const buildTree = <T extends { id: string; parent_id: string | null }>(messages: T[]): Tree<T> | null => {
  const map: Record<string, Tree<T>> = {};
  const tree = [];

  // Build a hash table and map items to objects
  messages.forEach(function (item) {
    const id = item.id;
    if (!map[id]) {
      map[id] = { ...item, children: [] };
    }
  });

  // Loop over hash table
  let mappedElem: Tree<T>;
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
