import { Text } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { getLocaleDisplayName } from "src/lib/languages";
import { Stat as StatType, StatNames } from "src/types/Stat";

type KeyPairStatProps = {
  stat: StatType;
  titleFn?: (name: string) => string;
};

export const KeyPairStat = ({ stat, titleFn }: KeyPairStatProps) => {
  const { t } = useTranslation("stats");
  return (
    <>
      {Object.keys(stat.stats).map((item) => {
        return (
          <Text key={item}>
            <Text className="capitalize" as="span" fontWeight="semibold">
              {titleFn ? titleFn(item) : t(getTypeSafei18nKey(item))}
            </Text>
            : {t(getTypeSafei18nKey(stat.stats[item]))}
          </Text>
        );
      })}
    </>
  );
};

type MessageTreeStateStatsProps = {
  titleFn: (name: string) => string;
  stat: StatType & {
    stats: {
      lang: string;
      state: string;
      count: number;
    }[];
  };
};

export const MessageTreeStateStats = ({ stat, titleFn }: MessageTreeStateStatsProps) => {
  const { t } = useTranslation("stats");
  return (
    <>
      {stat.stats.map((item) => {
        return (
          <Text key={item.state}>
            <Text as="span" fontWeight="semibold">
              {titleFn ? titleFn(item.lang) : item.lang}
            </Text>
            : {item.count} ({t(getTypeSafei18nKey(item.state))})
          </Text>
        );
      })}
    </>
  );
};

export const statComponents: Record<StatNames, React.FC<{ stat: StatType }>> = {
  human_messages_by_lang: ({ stat }: KeyPairStatProps) => <KeyPairStat stat={stat} titleFn={getLocaleDisplayName} />,
  human_messages_by_role: ({ stat }: KeyPairStatProps) => <KeyPairStat stat={stat} />,
  message_trees_by_state: ({ stat }: KeyPairStatProps) => <KeyPairStat stat={stat} />,
  message_trees_states_by_lang: ({ stat }: MessageTreeStateStatsProps) => (
    <MessageTreeStateStats stat={stat} titleFn={getLocaleDisplayName} />
  ),
  users_accepted_tos: ({ stat }: KeyPairStatProps) => <KeyPairStat stat={stat} />,
};
