/*
This code checks if a given email is valid. The given email is "example@gmail.com".
The code starts by importing the "prisma" package.
The code then defines a constant named "validEmailRegex" that uses a regex to check if the email is valid.
The code then defines an export function named "getValidEmail" that takes in an email and an id.
This function will return a valid email.
The code then defines an export function named "isValidEmail" that takes in an email.
This function will return a boolean value.
The code then checks if the email is valid.
The code then returns a boolean value.
*/
import prisma from "./prismadb";

export const validEmailRegex = /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/g;
/**
 * Given a user's email and its ID, returns a valid display email,
 * checking if the original display email is invalid.
 *
 * @param Email
 * @param {string} id The user's ID.
 * @returns {string} A valid email.
 */
export const getValidEmail = (Email: string, id: string): string => {
  /*
    Given a user's email and its ID, returns a valid display email,
    checking if the original display email is invalid.

    Parameters
    ----------
    Email: string
        The user's email.
    id: string
        The user's id.

    Returns
    -------
    string
        A valid email.

    */
  return !isValidEmail(Email) ? id : Email;
};

export const isValidEmail = async (Email: string) => {
  /*
    Checks if the email is valid.

    Parameters
    ----------
    Email: string
        The user's email.

    Returns
    -------
    boolean
        Whether or not the email is valid.

    */
  if (!(Email && Email.match(validEmailRegex))) {
    return false;
  }
  // const email = await prisma.user.findFirst({
  //   where: {
  //     email: Email,
  //   }
  // });
  // return !email;
  return true;
};
