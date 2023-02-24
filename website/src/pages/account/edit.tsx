import { Button, FormControl, FormErrorMessage, Input, InputGroup } from "@chakra-ui/react";
import Head from "next/head";
import Router from "next/router";
import { useSession } from "next-auth/react";
import React from "react";
import { Control, useForm, useWatch } from "react-hook-form";
import { validDisplayNameRegex } from "src/lib/display_name_validation";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

export default function Account() {
  const { data: session } = useSession();

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
      <div className="oa-basic-theme">
        <main className="h-3/4 z-0 flex flex-col items-center justify-center">
          <p>{session.user.name || "No username"}</p>
          <EditForm></EditForm>
        </main>
      </div>
    </>
  );
}

const EditForm = () => {
  const { data: session } = useSession();

  const updateUser = async ({ username }: { username: string }) => {
    try {
      const body = { username };
      await fetch("/api/username", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      session.user.name = username;
      await Router.push("/account");
    } catch (error) {
      console.error(error);
    }
  };

  const {
    register,
    formState: { errors },
    handleSubmit,
    control,
  } = useForm<{ username: string }>({
    defaultValues: {
      username: session?.user.name,
    },
  });

  return (
    <form onSubmit={handleSubmit(updateUser)}>
      <InputGroup>
        <FormControl isInvalid={errors.username ? true : false}>
          <Input
            placeholder="Edit Username"
            type="text"
            {...register("username", { required: true, pattern: validDisplayNameRegex })}
          ></Input>
          <FormErrorMessage>
            {errors.username?.type === "required" && "Username is required"}
            {errors.username?.type === "pattern" && "Username is invalid"}
          </FormErrorMessage>
        </FormControl>
        <SubmitButton control={control}></SubmitButton>
      </InputGroup>
    </form>
  );
};

const SubmitButton = ({ control }: { control: Control<{ username: string }> }) => {
  const username = useWatch({ control, name: "username" });
  return (
    <Button isDisabled={!username} type="submit" value="Change">
      Submit
    </Button>
  );
};
