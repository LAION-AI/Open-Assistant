import { Button, FormControl, FormLabel, Input, InputGroup, useToast } from "@chakra-ui/react";
import Head from "next/head";
import React, { useEffect, useMemo } from "react";
import { useForm } from "react-hook-form";
export { getStaticProps } from "src/lib/defaultServerSideProps";
import { get, post } from "src/lib/api";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

interface AckData {
  paperackYes: boolean;
  paperackName: string;
}

export default function PaperAck() {
  const toast = useToast();

  const { data: defaultValues } = useSWRImmutable<AckData>("/api/paperack", get);
  const { trigger } = useSWRMutation<AckData, any, any, AckData>("/api/paperack", post, {
    onSuccess() {
      toast({
        title: "Successfully updated your preferences",
        status: "success",
      });
    },
    onError(err) {
      console.error(err);
      toast({
        title: "An error occurred!",
        status: "error",
      });
    },
  });

  const {
    register,
    formState: { errors },
    handleSubmit,
    reset,
    watch,
  } = useForm<AckData>({ defaultValues });

  useEffect(() => {
    reset(defaultValues);
  }, [defaultValues, reset]);

  const updatePaperAck = useMemo(() => handleSubmit((data: AckData) => trigger(data)), [handleSubmit, trigger]);

  const { paperackYes, paperackName } = watch();

  return (
    <>
      <Head>
        <title>Open Assistant</title>
      </Head>
      <main className="oa-basic-theme h-3/4 z-0 flex flex-col items-center justify-center">
        <div className="max-w-3xl">
          <div className="m-4">
            <p className="mb-8">
              If you want to be considered for acknowledgements in the paper for your contributions, tick the box below
              AND enter your (real) name.
            </p>
            <form onSubmit={updatePaperAck}>
              <InputGroup className="flex flex-col gap-6">
                <FormControl className="flex flex-row gap-2">
                  <input
                    id="paperackYes"
                    type="checkbox"
                    name="paperackYes"
                    {...register("paperackYes")}
                    className="mb-2"
                  />
                  <FormLabel htmlFor="paperackYes">I want to be mentioned in the acknowledgements</FormLabel>
                </FormControl>
                <FormControl isInvalid={errors.paperackName ? true : false}>
                  <FormLabel>Write the name by which you want to be mentioned in the acknowledgements</FormLabel>
                  <Input placeholder="Name" type="text" {...register("paperackName")}></Input>
                </FormControl>
                <Button isDisabled={paperackYes && !paperackName} type="submit">
                  Submit
                </Button>
              </InputGroup>
            </form>
          </div>
        </div>
      </main>
    </>
  );
}
