export interface MessageRevisionProposal {
  id: string;
  messageId: string;

  text: string;

  additions: number;
  deletions: number;

  upvotes: number;
  downvotes: number;
}
