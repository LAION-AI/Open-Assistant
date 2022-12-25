import { chakra, Box, HStack, useRadio, useRadioGroup } from "@chakra-ui/react";

const RatingRadioButton = (props) => {
  const { option, ...radioProps } = props;
  const { getInputProps, getCheckboxProps } = useRadio(radioProps);

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
        {option}
      </Box>
    </Box>
  );
};

const RatingRadioGroup = (props) => {
  const { min, max, onChange, ...rest } = props;
  const { value, getRadioProps, getRootProps } = useRadioGroup({
    defaultValue: min,
    onChange: onChange,
  });
  const options = Array.from(new Array(1 + max - min), (x, i) => i + min);

  return (
    <HStack {...getRootProps()}>
      {options.map((option) => (
        <RatingRadioButton key={option} option={option} {...getRadioProps({ value: option })} />
      ))}
    </HStack>
  );
};

export default RatingRadioGroup;
