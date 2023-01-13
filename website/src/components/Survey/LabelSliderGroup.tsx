import { Grid, Slider, SliderFilledTrack, SliderThumb, SliderTrack, useColorMode } from "@chakra-ui/react";
import { useId, useState } from "react";
import { colors } from "styles/Theme/colors";

// TODO: consolidate with FlaggableElement
interface LabelSliderGroupProps {
  labelIDs: Array<string>;
  onChange: (sliderValues: number[]) => unknown;
  isEditable?: boolean;
}

export const LabelSliderGroup = ({ labelIDs, onChange, isEditable }: LabelSliderGroupProps) => {
  const [sliderValues, setSliderValues] = useState<number[]>(Array.from({ length: labelIDs.length }).map(() => 0));

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
            onChange(newState);
            setSliderValues(newState);
          }}
          isEditable={isEditable}
        />
      ))}
    </Grid>
  );
};

function CheckboxSliderItem(props: {
  labelId: string;
  sliderValue: number;
  sliderHandler: (newVal: number) => unknown;
  isEditable: boolean;
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
      <Slider
        aria-roledescription="slider"
        defaultValue={0}
        isDisabled={!props.isEditable}
        onChangeEnd={(val) => props.sliderHandler(val / 100)}
      >
        <SliderTrack>
          <SliderFilledTrack />
          <SliderThumb />
        </SliderTrack>
      </Slider>
    </>
  );
}
