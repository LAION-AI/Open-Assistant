/*
This code creates a website that allows a user to change their email address.
The code starts by importing several React components.
The code then defines an EditEmailForm component.
The EditEmailForm component creates a form that allows the user to change their email address.
The code then creates a session variable and sets it to the result of the useSession function.
The code then creates a captcha variable and sets it to the result of the useRef function.
The code then defines a updateUser function.
The updateUser function updates the user's email and redirects the user to the account page.
The code then creates a form using the useForm function.
The form has a field that is used to enter the user's new email address.
The form is submitted when the user clicks the submit button.
The code then creates a SubmitButton component.
The SubmitButton component creates a submit button that will be displayed at the end of the form.
*/

import { Button, FormControl, FormErrorMessage, Input, InputGroup } from "@chakra-ui/react";
import Head from "next/head";
import Router from "next/router";
import { useSession, signIn } from "next-auth/react";
import React from "react";
import { useRef } from "react";
import { Control, useForm, useWatch } from "react-hook-form";
import { validEmailRegex } from "src/lib/email_validation";
export { getStaticProps } from "src/lib/defaultServerSideProps";
import { TurnstileInstance } from "@marsidev/react-turnstile";

export default function emailAccount() {
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
      <main className="oa-basic-theme h-3/4 z-0 flex flex-col items-center justify-center">
        <p>{session.user.email || "No email"}</p>
        <EditEmailForm />
      </main>
    </>
  );
}

const EditEmailForm = () => {
  const { data: session } = useSession();
  const captcha = useRef<TurnstileInstance>(null);

  const updateUser = async ({ email }: { email: string }) => {
    try {
      const body = { email };
      await fetch("/api/email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then((response) => {
        if (response.status >= 400 && response.status < 600) {
          errors.email = { type: "pattern" };
        } else {
          session.user.email = email;
          Router.push("/account");
          // signIn('email', {
          //   callbackUrl: "/api/update_email?previousEmail="+session.user.email,
          //   email: email,
          //   captcha: captcha.current?.getResponse(),
          // });
        }
      });
    } catch (error) {
      console.error(error);
    }
  };

  const {
    register,
    formState: { errors },
    handleSubmit,
    control,
  } = useForm<{ email: string }>({
    defaultValues: {
      email: session?.user.email,
    },
  });

  return (
    <form onSubmit={handleSubmit(updateUser)}>
      <InputGroup>
        <FormControl isInvalid={errors.email ? true : false}>
          <Input
            placeholder="Edit Email"
            type="text"
            {...register("email", { required: true, pattern: validEmailRegex })}
          ></Input>
          <FormErrorMessage>
            {errors.email?.type === "required" && "email is required"}
            {errors.email?.type === "pattern" && "email is invalid"}
          </FormErrorMessage>
        </FormControl>
        <SubmitButton control={control}></SubmitButton>
      </InputGroup>
    </form>
  );
};

const SubmitButton = ({ control }: { control: Control<{ email: string }> }) => {
  const email = useWatch({ control, name: "email" });
  return (
    <Button isDisabled={!email} type="submit" value="Change">
      Submit
    </Button>
  );
};
