import {
  Badge,
  Box,
  Card,
  CardBody,
  Divider,
  Flex,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { GetServerSideProps, InferGetServerSidePropsType } from "next";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { FC } from "react";
import { DashboardLayout } from "src/components/Layout";
import { MessageLoading } from "src/components/Loading/MessageLoading";
import { BaseMessageEntry } from "src/components/Messages/BaseMessageEntry";
import { MessageEmojiButton } from "src/components/Messages/MessageEmojiButton";
import { MessageInlineEmojiRow } from "src/components/Messages/MessageInlineEmojiRow";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import { get } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import { Message } from "src/types/Conversation";
import { MessageRevisionProposal } from "src/types/MessageRevisionProposal";
import useSWRImmutable from "swr/immutable";

interface RevisionProposalsTableEntryProps {
  revision: MessageRevisionProposal;
  lang: string;
}

const RevisionProposalsTableEntry: FC<RevisionProposalsTableEntryProps> = ({ revision, lang }) => {
  return (
    <BaseMessageEntry
      hideAvatar={true}
      style={{
        width: "100%",
      }}
      content={revision.text.replaceAll("\\n", "\n").toString()}
    >
      <Flex justifyContent="end" mt="2" alignItems="center">
        <MessageInlineEmojiRow>
          <Badge variant="subtle" colorScheme="gray" fontSize="xx-small">
            {lang}
          </Badge>
          <MessageEmojiButton
            emoji={{ name: "+1", count: revision.upvotes }}
            checked={false}
            userReacted
            userIsAuthor={false}
            // eslint-disable-next-line @typescript-eslint/no-empty-function
            onClick={() => { }}
          />

          <MessageEmojiButton
            emoji={{ name: "-1", count: revision.downvotes }}
            checked={false}
            userReacted
            userIsAuthor={false}
            // eslint-disable-next-line @typescript-eslint/no-empty-function
            onClick={() => { }}
          />
        </MessageInlineEmojiRow>
      </Flex>
    </BaseMessageEntry>
  );
};

interface RevisionProposalsTableProps {
  revisions: MessageRevisionProposal[];
  lang: string;
}

const RevisionProposalsTable: FC<RevisionProposalsTableProps> = ({ revisions, lang }) => (
  <TableContainer>
    <Table>
      <Thead>
        <Tr>
          <Th colSpan={3}>Edited content</Th>
          <Th textAlign="center">Deletions</Th>
          <Th textAlign="center">Additions</Th>
        </Tr>
      </Thead>
      <Tbody>
        {revisions.map((revision) => (
          <Tr key={revision.id}>
            <Td colSpan={3}>
              <RevisionProposalsTableEntry revision={revision} lang={lang} />
            </Td>
            <Td textAlign="center">
              <Badge colorScheme="red" marginInline="auto" p={3} variant="outline" fontSize="x-large">
                {" "}
                -{revision.deletions}{" "}
              </Badge>
            </Td>
            <Td textAlign="center">
              <Badge colorScheme="green" p={3} variant="outline" marginInline="auto" fontSize="x-large">
                {" "}
                +{revision.additions}{" "}
              </Badge>
            </Td>
          </Tr>
        ))}
      </Tbody>
    </Table>
  </TableContainer>
);

const MessageRevisionProposals = ({ id }: InferGetServerSidePropsType<typeof getServerSideProps>) => {
  const { t } = useTranslation(["message", "common"]);
  const { data, isLoading, error } = useSWRImmutable<{
    revision_proposals: MessageRevisionProposal[];
    message: Message;
  }>(API_ROUTES.REVISION_PROPOSALS_TO_MESSAGE(id), get, {
    keepPreviousData: true,
  });

  return (
    <>
      <Head>
        <title>{t("common:title")}</title>
        <meta
          name="description"
          content="Conversational AI for everyone. An open source project to create a chat enabled GPT LLM run by LAION and contributors around the world."
        />
      </Head>
      <Box width="full">
        <Card>
          <CardBody p={[3, 4, 6]}>
            {/*<Stack spacing="1">
              <HStack>
                <Text fontSize="xl" fontWeight="bold" color={titleColor}>
                  All edits of a message
                </Text>
              </HStack>
            </Stack>*/}

            {isLoading && !data && <MessageLoading />}
            {error && "Unable to load the message's revision proposals!"}
            {data && data.message && (
              <div className="message-being-edited">
                <MessageTableEntry message={data.message} />
              </div>
            )}

            <Divider marginBlock={5} />

            {data && data.message && data.revision_proposals && (
              <RevisionProposalsTable 
                revisions={data.revision_proposals} 
                lang={data.message.lang} 
              />
            )}
          </CardBody>
        </Card>
      </Box>
    </>
  );
};

MessageRevisionProposals.getLayout = DashboardLayout;

export const getServerSideProps: GetServerSideProps<{ id: string }, { id: string }> = async ({
  locale = "en",
  params,
}) => ({
  props: {
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    id: params!.id,
    ...(await serverSideTranslations(locale, ["common", "message", "labelling"])),
  },
});

export default MessageRevisionProposals;
