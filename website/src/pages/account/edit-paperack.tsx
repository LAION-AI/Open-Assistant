import { Button, FormControl, FormLabel, Input, InputGroup } from "@chakra-ui/react";
import Head from "next/head";
import { useSession } from "next-auth/react";
import React from "react";
import { Control, useForm, useWatch } from "react-hook-form";
export { getStaticProps } from "src/lib/defaultServerSideProps";

export default function Account() {
  const { data: session } = useSession();

  const [paperackData, setPaperackData] = React.useState({
    paperackYes: false,
    paperackName: "",
  });

  const [successMsg, setSuccessMsg] = React.useState("");

  React.useEffect(() => {
    if (!session) {
      return;
    }
    async function fetchPaperack() {
      const response = await fetch("/api/paperack", {
        method: "GET",
        headers: { Accept: "application/json" },
      });
      const data = await response.json();
      return data;
    }
    fetchPaperack().then((data) => {
      setPaperackData(data);
    });
  }, [session]);

  if (!session) {
    return;
  }

  return (
    <>
      <Head>
        <title>Open Assistant</title>
        <meta
          name="description"
          content="Conversational AI for everyone. An open source project to create a chat enabled GPT LLM run by LAION and contributors around the world."
        />
      </Head>
      <main className="oa-basic-theme h-3/4 z-0 flex flex-col items-center justify-center">
        {successMsg ? (
          <div>
            <p className="text-green-500">{successMsg}</p>
          </div>
        ) : (
          <EditForm {...paperackData} setSuccessMsg={setSuccessMsg} />
        )}
      </main>
    </>
  );
}

const EditForm = ({ paperackYes, paperackName, setSuccessMsg }) => {
  const updatePaperack = async ({ paperackYes, paperackName }: { paperackYes: boolean; paperackName: string }) => {
    try {
      const body = { paperackYes, paperackName };
      await fetch("/api/paperack", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      setSuccessMsg("Successfully updated your preferences");
    } catch (error) {
      console.error(error);
    }
  };

  const {
    register,
    formState: { errors },
    handleSubmit,
    control,
    reset,
    getValues,
  } = useForm<{ paperackYes: boolean; paperackName: string }>({
    defaultValues: {
      paperackYes: false,
      paperackName: "",
    },
  });

  React.useEffect(() => {
    reset({ paperackYes, paperackName });
  }, [paperackYes, paperackName, reset, getValues]);

  return (
    <div className="m-4">
      <p className="mb-8">
        If you want to be considered for acknowledgements in the paper for your contributions, tick the box below AND
        enter your (real) name.
      </p>
      <form onSubmit={handleSubmit(updatePaperack)}>
        <InputGroup className="flex flex-col gap-6">
          <FormControl className="flex flex-row gap-2">
            <input id="paperackYes" type="checkbox" name="paperackYes" {...register("paperackYes")} className="mb-2" />
            <FormLabel htmlFor="paperackYes">I want to be mentioned in the acknowledgements</FormLabel>
          </FormControl>
          <FormControl isInvalid={errors.paperackName ? true : false}>
            <FormLabel>Write the name by which you want to be mentioned in the acknowledgements</FormLabel>
            <Input placeholder="Name" type="text" {...register("paperackName")}></Input>
          </FormControl>
          <SubmitButton control={control}></SubmitButton>
        </InputGroup>
      </form>
    </div>
  );
};

const SubmitButton = ({ control }: { control: Control<{ paperackYes: boolean; paperackName: string }> }) => {
  const paperackYes = useWatch({ control, name: "paperackYes" });
  const paperackName = useWatch({ control, name: "paperackName" });
  return (
    <Button isDisabled={paperackYes && !paperackName} type="submit" value="Change">
      Submit
    </Button>
  );
};
