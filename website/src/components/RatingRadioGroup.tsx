import { Box, HStack, useRadio, useRadioGroup } from "@chakra-ui/react";

const RatingRadioButton = (props) => {
  const { getInputProps, getCheckboxProps } = useRadio(props);

  const input = getInputProps();
  const checkbox = getCheckboxProps();

  return (
    <Box as="label">
      <input {...input} />
      <Box
        {...checkbox}
        cursor="pointer"
        borderWidth="1px"
        borderRadius="md"
        boxShadow="md"
        _checked={{
          bg: "blue.200",
          color: "white",
          borderColor: "blue.200",
        }}
        _focus={{
          boxShadow: "outline",
        }}
        px={5}
        py={3}
      >
        {props.children}
      </Box>
    </Box>
  );
};

const RatingRadioGroup = (props) => {
  const { min, max, onChange } = props;
  const { getRadioProps, getRootProps } = useRadioGroup({
    name: "rating",
    defaultValue: `${min}`,
    onChange: onChange,
  });
  const group = getRootProps();

  const options = Array.from(new Array(1 + max - min), (x, i) => `${i + min}`);

  return (
    <HStack {...group}>
      {options.map((option) => {
        const radio = getRadioProps({ value: option });
        return (
          <RatingRadioButton key={option} {...radio}>
            {option}
          </RatingRadioButton>
        );
      })}
    </HStack>
  );
};

export default RatingRadioGroup;
