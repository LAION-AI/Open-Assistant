import { Box, Select, useColorModeValue } from "@chakra-ui/react";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Colors,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { Doughnut, Pie } from "react-chartjs-2";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { getLocaleDisplayName } from "src/lib/languages";
import { colors } from "src/styles/Theme/colors";
import { Stat as StatType } from "src/types/Stat";

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Colors);

const getDefaultChartOptions = (color) => ({
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
          plugins={[]}
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

export const statComponents: Record<string, React.FC<{ stat: StatType }>> = {
  human_messages_by_role: ({ stat }: ChartProps) => <Chart stat={stat} type={Pie} />,
  message_trees_by_state: ({ stat }: ChartProps) => <Chart stat={stat} type={Doughnut} />,
  users_accepted_tos: () => null,
  message_trees_states_by_lang: ({ stat }: MessageTreeStateStatsProps) => (
    <MessageTreeStateStats stat={stat} titleFn={getLocaleDisplayName} />
  ),
  human_messages_by_lang: ({ stat }: ChartProps) => (
    <Chart stat={stat} titleFn={getLocaleDisplayName} type={Doughnut} />
  ),
};
