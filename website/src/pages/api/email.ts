/*
This code updates the user's email field in the User table.
The code starts by importing the "withoutRole" function from the "src/lib/auth" module and the "isValidEmail" function from the "src/lib/email_validation" module and the prisma variable from the "src/lib/prismadb" module.
The code then defines a handler function.
The handler function dispatches the withoutRole function.
The code then creates a newmail variable and sets it to the email that the user inputs.
The code will then check to see if the newmail variable is a valid email.
If it is not, the code will return a 400 status code and a message that says "Invalid email".
The code will then create a emailExists variable and set it to the result of a database query that checks if the newmail variable exists.
If it does, the code will return a 400 status code and a message that says "Invalid email".
The code will then update the email field of the user in the database to the newmail variable.
The code will then return a 200 status code and a message that says "Email saved".
*/
import { withoutRole } from "src/lib/auth";
import { isValidEmail } from "src/lib/email_validation";
import prisma from "src/lib/prismadb";

/**
 * Updates the user's `name` field in the `User` table.
 */
const handler = withoutRole("banned", async (req, res, token) => {
  const newmail = req.body.email;
  if (!isValidEmail(newmail)) {
    return res.status(400).json({ message: "Invalid email" });
  }

  const emailExists = await prisma.user.findFirst({
    where: {
      email: newmail,
    },
  });
  if (emailExists) {
    console.log("this email exists.");
    return res.status(400).json({ message: "Invalid email" });
  }

  const { email } = await prisma.user.update({
    where: {
      id: token.sub,
    },
    data: {
      email: newmail,
    },
  });
  res.json({ newmail });
});

export default handler;
