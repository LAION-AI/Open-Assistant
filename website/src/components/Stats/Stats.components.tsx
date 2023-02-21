import { Box, Select, useColorModeValue } from "@chakra-ui/react";
import { ArcElement, BarElement, CategoryScale, Chart as ChartJS, Colors, LinearScale, Tooltip } from "chart.js";
import { createColumnHelper } from "@tanstack/react-table";
import { useTranslation } from "next-i18next";
import { useState, useMemo } from "react";
import { Doughnut, Pie, Bar } from "react-chartjs-2";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { getLocaleDisplayName } from "src/lib/languages";
import { colors } from "src/styles/Theme/colors";
import { DataTable } from "../DataTable/DataTable";
import { Stat as StatType } from "src/types/Stat";

ChartJS.register(ArcElement, Tooltip, Colors, CategoryScale, BarElement, LinearScale);

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

// The headers come from the message tree State. These two states are not
// considered because they make the table too wide and they are not so
// interesting:
// - "ready_for_scoring",
// - "scoring_failed"
const interestingStates = [
  "prompt_lottery_waiting",
  "initial_prompt_review",
  "growing",
  "backlog_ranking",
  "ranking",
  "ready_for_export",
  "aborted_low_grade",
  "halted_by_moderator",
];

type LangRow = {
  language: string;
  initial_prompt_review: number;
  prompt_lottery_waiting: number;
  growing: number;
  backlog_ranking: number;
  ranking: number;
  ready_for_export: number;
  aborted_low_grade: number;
  halted_by_moderator: number;
};

function getTableData(
  stat: StatType & {
    stats: {
      lang: string;
      state: string;
      count: number;
    }[];
  },
  t
) {
  // Group the stats in a dictionary where the key is the language
  const dataPerLang = {};
  stat.stats.forEach((item) => {
    const { lang, state, count } = item;
    const langWithCode = `${getLocaleDisplayName(lang)} [${lang}]`;
    if (!dataPerLang[langWithCode]) {
      dataPerLang[langWithCode] = {};
    }

    dataPerLang[langWithCode][state] = count;
  });

  // If some state was not found for a language, set the count to 0
  Object.keys(dataPerLang).forEach((lang) => {
    interestingStates.forEach((state) => {
      if (!dataPerLang[lang][state]) {
        dataPerLang[lang][state] = 0;
      }
    });
  });

  // Put the data in the format required by DataTable
  const data: LangRow[] = [];
  for (const lang in dataPerLang) {
    const row = { language: lang, ...dataPerLang[lang] };
    data.push(row);
  }

  const columnHelper = createColumnHelper<LangRow>();

  const columns = [
    columnHelper.accessor("language", {
      cell: (info) => info.getValue(),
      header: "Language",
    }),
    columnHelper.accessor("initial_prompt_review", {
      cell: (info) => info.getValue(),
      header: t("initial_prompt_review"),
      meta: {
        isNumeric: true,
      },
    }),
    columnHelper.accessor("prompt_lottery_waiting", {
      cell: (info) => info.getValue(),
      header: t("prompt_lottery_waiting"),
      meta: {
        isNumeric: true,
      },
    }),
    columnHelper.accessor("growing", {
      cell: (info) => info.getValue(),
      header: t("growing"),
      meta: {
        isNumeric: true,
      },
    }),
    columnHelper.accessor("backlog_ranking", {
      cell: (info) => info.getValue(),
      header: t("backlog_ranking"),
      meta: {
        isNumeric: true,
      },
    }),
    columnHelper.accessor("ranking", {
      cell: (info) => info.getValue(),
      header: t("ranking"),
      meta: {
        isNumeric: true,
      },
    }),
    columnHelper.accessor("ready_for_export", {
      cell: (info) => info.getValue(),
      header: t("ready_for_export"),
      meta: {
        isNumeric: true,
      },
    }),
    columnHelper.accessor("aborted_low_grade", {
      cell: (info) => info.getValue(),
      header: t("aborted_low_grade"),
      meta: {
        isNumeric: true,
      },
    }),
    columnHelper.accessor("halted_by_moderator", {
      cell: (info) => info.getValue(),
      header: t("halted_by_moderator"),
      meta: {
        isNumeric: true,
      },
    }),
  ];

  return { data, columns };
}

export const MessageTreeStateStats = ({ stat, titleFn }: MessageTreeStateStatsProps) => {
  const { t } = useTranslation("stats");
  const color = useColorModeValue(colors.light.text, colors.dark.text);
  const uniqueLangs = Array.from(new Set(stat.stats.map((s) => s.lang)));
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

const barOptions = {
  responsive: true,
  scales: {
    x: {
      stacked: true,
    },
    y: {
      stacked: true,
    },
  },
};

export const MessageTreeStateStatsStacked = ({ stat, titleFn }: MessageTreeStateStatsProps) => {
  const { t } = useTranslation("stats");
  const uniqueLangs = useMemo(() => Array.from(new Set(stat.stats.map((s) => s.lang))), stat.stats);
  const uniqueStates = useMemo(() => Array.from(new Set(stat.stats.map((s) => s.state))), stat.stats);

  const barDatasets = [];
  uniqueStates.forEach((state) => {
    const dataState = stat.stats.filter((item) => item.state === state);

    const langCount = {};
    dataState.forEach((item) => {
      langCount[item.lang] = item.count;
    });

    barDatasets.push({
      label: t(getTypeSafei18nKey(state)),
      data: uniqueLangs.map((item) => langCount[item]),
    });
  });

  const barData = {
    labels: uniqueLangs,
    datasets: barDatasets,
  };

  return (
    <>
      <Box minH={330}>
        <Bar options={barOptions} data={barData} />
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

export const MessageTreeStateStatsTable = ({ stat, titleFn }: MessageTreeStateStatsProps) => {
  const { t } = useTranslation("stats");
  const { data, columns } = getTableData(stat, t);

  return <DataTable data={data} columns={columns} disablePagination={true}></DataTable>;
};

export const statComponents: Record<string, React.FC<{ stat: StatType }>> = {
  human_messages_by_role: ({ stat }: ChartProps) => <Chart stat={stat} type={Pie} />,
  message_trees_by_state: ({ stat }: ChartProps) => <Chart stat={stat} type={Doughnut} />,
  users_accepted_tos: () => null,
  message_trees_states_by_lang: ({ stat }: MessageTreeStateStatsProps) => (
    <MessageTreeStateStats stat={stat} titleFn={getLocaleDisplayName} />
  ),
  message_trees_states_by_lang_table: ({ stat }: MessageTreeStateStatsProps) => (
    <MessageTreeStateStatsTable stat={stat} titleFn={getLocaleDisplayName} />
  ),
  message_trees_states_by_lang_stacked: ({ stat }: MessageTreeStateStatsProps) => (
    <MessageTreeStateStatsStacked stat={stat} titleFn={getLocaleDisplayName} />
  ),
  human_messages_by_lang: ({ stat }: ChartProps) => (
    <Chart stat={stat} titleFn={getLocaleDisplayName} type={Doughnut} />
  ),
};
