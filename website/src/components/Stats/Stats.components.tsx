import { Text, Box, Select, useColorModeValue } from "@chakra-ui/react";
import { ArcElement, Chart as ChartJS, Colors, Tooltip } from "chart.js";
import { TFunction, useTranslation } from "next-i18next";
import { useState } from "react";
import { Doughnut, Pie } from "react-chartjs-2";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { getLocaleDisplayName } from "src/lib/languages";
import { colors } from "src/styles/Theme/colors";
import { SimpleTable } from "../SimpleTable/SimpleTable";
import { Stat as StatType } from "src/types/Stat";

ChartJS.register(ArcElement, Tooltip, Colors);

const getDefaultChartOptions = (color: string) => ({
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color,
      },
    },
  },
});

type ChartProps = {
  stat: StatType;
  titleFn?: (name: string) => string;
  type?: typeof Pie | typeof Doughnut;
};

type KeyPairStatProps = {
  stat: StatType;
  titleFn?: (name: string) => string;
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

const findLangRow = (rows: any, lang: string) => {
  for (let i = 0; i < rows.length; i++) {
    const row_lang = rows[i][0];
    if (row_lang === lang) return i;
  }

  return -1;
};

function getTableData(
  stat: StatType & {
    stats: {
      lang: string;
      state: string;
      count: number;
    }[];
  },
  t: TFunction<"stats", undefined, "stats">
) {
  // The headers come from the message tree State.
  // These two states are not considered because they make
  // the table too wide and they are not so interesting:
  // - "ready_for_scoring",
  // - "scoring_failed"
  let headers = [
    "language", // This one doesn't come from the message tree state
    "prompt_lottery_waiting",
    "initial_prompt_review",
    "growing",
    "backlog_ranking",
    "ranking",
    "ready_for_export",
    "aborted_low_grade",
    "halted_by_moderator",
  ];

  const languages = [];
  for (let i = 0; i < stat.stats.length; i++) {
    if (!languages.includes(stat.stats[i].lang)) {
      languages.push(stat.stats[i].lang);
    }
  }

  const rows = [];

  for (let i = 0; i < stat.stats.length; i++) {
    const lang = stat.stats[i].lang;

    let langRow = findLangRow(rows, lang);

    if (langRow == -1) {
      // The language is not yet in the data. Add it
      rows.push(Array(headers.length).fill(0));
      langRow = rows.length - 1;
      rows[langRow][0] = lang;
    }

    const state = stat.stats[i].state;
    const stateCol = headers.indexOf(state);
    if (stateCol === -1) {
      continue;
    }

    const threadCount = stat.stats[i].count;
    rows[langRow][stateCol] = threadCount;
  }

  headers = headers.map((item) => t(getTypeSafei18nKey(item)));

  for (let i = 0; i < rows.length; i++) {
    const langCode = rows[i][0];
    rows[i][0] = getLocaleDisplayName(langCode) + " [" + langCode + "]";
  }
  return { headers, rows };
}

export const MessageTreeStateStats = ({ stat, titleFn }: MessageTreeStateStatsProps) => {
  const { t } = useTranslation("stats");
  const color = useColorModeValue(colors.light.text, colors.dark.text);
  const langs = stat.stats.map((item) => item.lang);
  const uniqueLangs = langs.filter((item, index) => langs.indexOf(item) === index);
  const [selectedLang, setSelectedLang] = useState("en");
  const stats = stat.stats.filter((item) => item.lang === selectedLang);

  return (
    <>
      <Select cursor="pointer" mb={3} value={selectedLang} onChange={(e) => setSelectedLang(e.target.value)}>
        {uniqueLangs.map((lang) => (
          <option key={lang} value={lang}>
            {titleFn(lang)}
          </option>
        ))}
      </Select>
      <Box minH={330}>
        <Doughnut
          width={100}
          height={50}
          options={getDefaultChartOptions(color)}
          data={{
            labels: stats.map((item) => t(getTypeSafei18nKey(item.state))),
            datasets: [
              {
                data: stats.map((item) => item.count),
              },
            ],
          }}
        />
      </Box>
    </>
  );
};

export const Chart = ({ stat, titleFn, type: Component }: ChartProps) => {
  const data = Object.keys(stat.stats);
  const { t } = useTranslation("stats");
  const color = useColorModeValue(colors.light.text, colors.dark.text);
  return (
    <Component
      width={100}
      height={50}
      options={getDefaultChartOptions(color)}
      data={{
        labels: data.map((lang) => (titleFn ? titleFn(lang) : t(getTypeSafei18nKey(lang)))),
        datasets: [
          {
            data: data.map((lang) => stat.stats[lang]),
          },
        ],
      }}
    />
  );
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

export const MessageTreeStateStatsTable = ({ stat }: MessageTreeStateStatsProps) => {
  const { t } = useTranslation("stats");
  const { headers, rows } = getTableData(stat, t);

  return <SimpleTable headers={headers} rows={rows}></SimpleTable>;
};

export const statComponents: Record<string, React.FC<{ stat: StatType }>> = {
  human_messages_by_role: ({ stat }: ChartProps) => <Chart stat={stat} type={Pie} />,
  message_trees_by_state: ({ stat }: ChartProps) => <Chart stat={stat} type={Doughnut} />,
  users_accepted_tos: () => null,
  message_trees_states_by_lang: ({ stat }: MessageTreeStateStatsProps) => (
    <MessageTreeStateStats stat={stat} titleFn={getLocaleDisplayName} />
  ),
  message_trees_states_by_lang_table: ({ stat }: MessageTreeStateStatsProps) => (
    <MessageTreeStateStatsTable stat={stat} />
  ),
  human_messages_by_lang: ({ stat }: ChartProps) => (
    <Chart stat={stat} titleFn={getLocaleDisplayName} type={Doughnut} />
  ),
};
