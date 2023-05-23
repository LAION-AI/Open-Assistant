import { Badge, Box, Card, CardBody, Divider, Flex, Table, TableContainer, Tbody, Td, Text, Th, Thead, Tr, useColorMode, useColorModeValue } from "@chakra-ui/react";
import { Change } from "diff";
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
import { Message, MessageWithChildren } from "src/types/Conversation";
import useSWRImmutable from "swr/immutable";

interface Edit {
  id: string;
  messageId: string;

  content: string;
  lang: string;

  additions: number;
  deletions: number;

  positiveReviews: number;
  negativeReviews: number;
}

interface EditedContentMesageTableEntryProps {
  edit: Edit;
}

const EditedContentMesageTableEntry: FC<EditedContentMesageTableEntryProps> = ({ edit }) => {
  return <BaseMessageEntry
    hideAvatar
    style={{
      width: '100%',
    }}
    content={edit.content}
  >
    <Flex
      justifyContent='end'
      mt="2"
      alignItems="center"
    >
      <MessageInlineEmojiRow>
        <Badge variant="subtle" colorScheme="gray" fontSize="xx-small">
          {edit.lang}
        </Badge>
        <MessageEmojiButton
          emoji={{ name: '+1', count: edit.positiveReviews }}
          checked={false}
          userReacted
          userIsAuthor={false}
          // eslint-disable-next-line @typescript-eslint/no-empty-function
          onClick={() => { }}
        />

        <MessageEmojiButton
          emoji={{ name: '-1', count: edit.negativeReviews }}
          checked={false}
          userReacted
          userIsAuthor={false}
          // eslint-disable-next-line @typescript-eslint/no-empty-function
          onClick={() => { }}
        />
      </MessageInlineEmojiRow>
    </Flex>

    <div className=''></div>
  </BaseMessageEntry>;
};

interface EditingTableProps {
  edits: Edit[];
}

const EditingTable: FC<EditingTableProps> = ({ edits }) => <TableContainer>
  <Table>
    <Thead>
      <Tr>
        <Th rowSpan={3}>Edited content</Th>
        <Th textAlign='center'>Deletions</Th>
        <Th textAlign='center'>Additions</Th>
      </Tr>
    </Thead>
    <Tbody>
      {edits.map(edit => (
        <Tr key={edit.id}>
          <Td rowSpan={3}>
            <EditedContentMesageTableEntry
              edit={edit}
            />
          </Td>
          <Td textAlign='center'>
            <Badge
              colorScheme='red'
              marginInline='auto'
              p={3}
              variant='outline'
              fontSize="x-large"
            > -{edit.deletions} </Badge>
          </Td>
          <Td textAlign='center'>
            <Badge
              colorScheme='green'
              p={3}
              variant='outline'
              marginInline='auto'
              fontSize="x-large"
            > +{edit.additions} </Badge>
          </Td>
        </Tr>
      ))}
    </Tbody>
  </Table>
</TableContainer>;

const MessageEditingDetails = ({ id }: InferGetServerSidePropsType<typeof getServerSideProps>) => {
  const { t } = useTranslation(["message", "common"]);
  const { data, isLoading, error } = useSWRImmutable<{ tree: MessageWithChildren | null; message?: Message }>(
    `/api/messages/${id}/tree`,
    get,
    {
      keepPreviousData: true,
    }
  );

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

            <div className='message-being-edited'>
              {isLoading && !data && <MessageLoading></MessageLoading>}
              {error && "Unable to load edits of message"}
              {data && data.message && <MessageTableEntry
                message={data.message}
              />}
            </div>

            <Divider marginBlock={5} />

            <EditingTable
              edits={[
                {
                  id: '',
                  messageId: data?.message?.id,

                  lang: data?.message?.lang,
                  content: "I don’t think so, can you tell me?\n\nI’m glad you asked me this question.",

                  additions: 2,
                  deletions: 1,

                  negativeReviews: 1,
                  positiveReviews: 2
                }
              ]}
            />
          </CardBody>
        </Card>
      </Box>
    </>
  );
};

MessageEditingDetails.getLayout = DashboardLayout;

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

export default MessageEditingDetails;
