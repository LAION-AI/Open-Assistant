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
  return !isValidEmail(Email) ? id : Email;
};

export const isValidEmail = async (Email: string) => {
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
