import { ChatConfigDesktop } from "./ChatConfigDesktop";
import { ChatConfigForm } from "./ChatConfigForm";
import { ChatConfigMobile } from "./ChatConfigMobile";

const form = <ChatConfigForm />;

export const ChatConfig = () => {
  return (
    <>
      <ChatConfigDesktop>{form}</ChatConfigDesktop>
      <ChatConfigMobile>{form}</ChatConfigMobile>
    </>
  );
};
