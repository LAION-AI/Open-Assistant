import { Grid, Slider, SliderFilledTrack, SliderThumb, SliderTrack } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/react";
import { ReactNode, useEffect, useId, useMemo, useState } from "react";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { colors } from "styles/Theme/colors";

export const LabelTask = ({
  title,
  desc,
  messages,
  inputs,
  controls,
}: {
  title: string;
  desc: string;
  messages: ReactNode;
  inputs: ReactNode;
  controls: ReactNode;
}) => {
  const { colorMode } = useColorMode();
  const mainBgClasses = colorMode === "light" ? "bg-slate-300 text-gray-800" : "bg-slate-900 text-white";

  const card = useMemo(
    () => (
      <>
        <h5 className="text-lg font-semibold">{title}</h5>
        <p className="text-lg py-1">{desc}</p>
        {messages}
      </>
    ),
    [title, desc, messages]
  );

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      <TwoColumnsWithCards>
        {card}
        {inputs}
      </TwoColumnsWithCards>
      {controls}
    </div>
  );
};

// TODO: consolidate with FlaggableElement
interface LabelSliderGroupProps {
  labelIDs: Array<string>;
  onChange: (sliderValues: number[]) => unknown;
}

export const LabelSliderGroup = ({ labelIDs, onChange }: LabelSliderGroupProps) => {
  const [sliderValues, setSliderValues] = useState<number[]>(Array.from({ length: labelIDs.length }).map(() => 0));

  useEffect(() => {
    onChange(sliderValues);
  }, [sliderValues, onChange]);

  return (
    <Grid templateColumns="auto 1fr" rowGap={1} columnGap={3}>
      {labelIDs.map((labelId, idx) => (
        <CheckboxSliderItem
          key={idx}
          labelId={labelId}
          sliderValue={sliderValues[idx]}
          sliderHandler={(sliderValue) => {
            const newState = sliderValues.slice();
            newState[idx] = sliderValue;
            setSliderValues(newState);
          }}
        />
      ))}
    </Grid>
  );
};

function CheckboxSliderItem(props: {
  labelId: string;
  sliderValue: number;
  sliderHandler: (newVal: number) => unknown;
}) {
  const id = useId();
  const { colorMode } = useColorMode();

  const labelTextClass = colorMode === "light" ? `text-${colors.light.text}` : `text-${colors.dark.text}`;

  return (
    <>
      <label className="text-sm" htmlFor={id}>
        {/* TODO: display real text instead of just the id */}
        <span className={labelTextClass}>{props.labelId}</span>
      </label>
      <Slider defaultValue={0} onChangeEnd={(val) => props.sliderHandler(val / 100)}>
        <SliderTrack>
          <SliderFilledTrack />
          <SliderThumb />
        </SliderTrack>
      </Slider>
    </>
  );
}
