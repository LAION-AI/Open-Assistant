import { Container } from "@/components/Container";
import { CallToAction } from "@/components/CallToAction";
import Image from "next/image";

const AboutPage = () => {
  return (
    <div>
      <Container className="">
        <div className="grid gap-16 items-center py-20 md:py-40 lg:grid-cols-2">
          <div className="m-auto order-2 lg:order-1">
            <Image src="/images/logos/logo.png" width={450} height={450} alt="temp-image" />
          </div>
          <div className="space-y-8 order-1 lg:order-2">
            <div>
              <h1 className="text-4xl mb-6">What is OpenAssistant?</h1>
              <p className="text-2xl">
                OpenAssistant is a chat-based assistant that understands tasks, can interact with third-party systems,
                and retrieve information dynamically to do so.
              </p>
            </div>
            <p className="text-2xl">
              It can be extended and personalized easily and is developed as free, open-source software.
            </p>
          </div>
        </div>
      </Container>

      <div className="bg-white py-32 border-t-[1px] border-gray-150">
        <Container className="">
          <div className="grid grid-cols-1 lg:grid-cols-10 lg:grid-rows-2">
            <div className="grid col-span-3 row-span-2">
              <div className="min-h-[17.5rem] px-12 sm:px-16 row-span-1 flex flex-col justify-center bg-[#307bf3] rounded-tl-[45px] lg:rounded-tl-none lg:rounded-bl-[45px] rounded-br-[45px] lg:rounded-br-none lg:rounded-tr-[45px]">
                <h4 className="font-bold text-white text-xl mb-4">Your Conversational Assistant</h4>
                <span className="w-8 h-[2px] bg-white mb-4 block lg:hidden" />
                <p className="text-white">State-of-the-Art chat assistant that can be personalized to your needs</p>
              </div>
              <div className="min-h-[17.5rem] px-12 sm:px-16 row-span-1 flex flex-col justify-center bg-[#275ddf] rounded-tl-[45px] rounded-br-[45px]">
                <h4 className="font-bold text-white text-xl mb-4">Interface w/ external systems</h4>
                <span className="w-8 h-[2px] bg-white mb-4 block lg:hidden" />
                <p className="text-white">
                  Usage of APIs and third-party applications, described via language & demonstrations.
                </p>
              </div>
            </div>
            <div className="grid grid-rows-2 col-span-3 row-span-2">
              <div className="min-h-[17.5rem] px-12 sm:px-16 row-span-1 flex flex-col justify-center bg-[#307bf3] lg:bg-[#275ddf] rounded-tl-[45px] rounded-br-[45px]">
                <h4 className="font-bold text-white text-xl mb-4">Retrieval via Search Engines</h4>
                <span className="w-8 h-[2px] bg-white mb-4 block lg:hidden" />
                <p className="text-white">External, upgradeable knowledge: No need for billions of parameters.</p>
              </div>
              <div className="min-h-[17.5rem] px-12 sm:px-16 row-span-1 flex flex-col justify-center bg-[#275ddf] lg:bg-[#307bf3] rounded-tl-[45px] lg:rounded-tl-none lg:rounded-bl-[45px] rounded-br-[45px] lg:rounded-br-none lg:rounded-tr-[45px]">
                <h4 className="font-bold text-white text-xl mb-4">A building block for developers</h4>
                <span className="w-8 h-[2px] bg-white mb-4 block lg:hidden" />
                <p className="text-white">Integrate OpenAssistant into your application.</p>
              </div>
            </div>
            <div className="px-12 sm:px-16 py-20 lg:p-20 col-span-4 row-span-2 bg-[#1a44a1] lg:flex lg:flex-col lg:justify-center rounded-tl-[45px] rounded-br-[45px] lg:rounded-tr-[80px] lg:rounded-tl-none lg:rounded-br-none">
              <h4 className="font-bold text-white text-xl mb-4">
                OpenAssistant unifies all knowledge work in one place
              </h4>
              <span className="w-8 h-[2px] bg-white mb-4 block lg:hidden" />
              <ul className="ml-4 sm:ml-12 mt-8 space-y-4 list-disc text-white">
                <li>Uses modern deep learning</li>
                <li>Runs on consumer hardware</li>
                <li>Trains on human feedback</li>
                <li>Free and open</li>
              </ul>
            </div>
          </div>
        </Container>
      </div>

      <div className="bg-gray-900 py-20">
        <Container className="">
          <div className="grid gap-16 items-center py-20 md:py-32 lg:grid-cols-2">
            <div>
              <h2 className="text-4xl text-white mb-6">Our Vision</h2>
              <p className="text-2xl text-gray-400">
                We want OpenAssistant to be the single, unifying platform that all other systems use to interface with
                humans.
              </p>
            </div>
            <div className="m-auto rounded-tl-[45px] rounded-br-[45px] overflow-hidden">
              <Image src="/images/temp-avatars/av2.jpg" width={450} height={450} alt="temp-image" />
            </div>
          </div>
        </Container>
      </div>

      <Container className="">
        <div className="py-32">
          <h2 className="text-4xl mb-16">Our Roadmap</h2>
          <div className="flex flex-col items-center space-y-8 md:space-y-0 md:items-start md:flex-row md:justify-between">
            <div className="flex flex-col items-center space-y-4">
              <div className="h-[5rem] w-[5rem] border-4 border-[#a72a1e] rounded-full flex items-center justify-center">
                <p className="font-bold text-[#a72a1e] text-center">ASAP</p>
              </div>
              <h4 className="font-bold text-xl text-[#a72a1e] text-center max-w-[10rem]">Minimum Viable Prototype</h4>
              <ul className="ml-6 md:ml-8 lg:ml-6 space-y-4 text-[#a72a1e] list-disc">
                <li>Data Collection Pipeline</li>
                <li>RL on Human Feedback</li>
                <li>Assistant v1 usable</li>
                <li>Out January 2023!</li>
              </ul>
            </div>
            <div>
              <span className="w-[4vw] h-[4px] mt-8 bg-[#a72a1e] rounded-full hidden md:block" />
            </div>
            <span className="w-[4px] h-16 bg-[#a72a1e] rounded-full block md:hidden" />
            <div className="flex flex-col items-center space-y-4">
              <div className="h-[5rem] w-[5rem] border-4 border-[#858585] rounded-full flex items-center justify-center">
                <p className="font-bold text-[#858585] text-center">
                  Q1
                  <br />
                  2023
                </p>
              </div>
              <h4 className="font-bold text-xl text-[#858585] text-center max-w-[10rem]">Growing Up</h4>
              <ul className="ml-6 md:ml-8 lg:ml-6 space-y-4 text-[#858585] list-disc">
                <li>Retrieval Augmentation</li>
                <li>Rapid Personalization</li>
                <li>Using External Tools</li>
              </ul>
            </div>
            <div>
              <span className="w-[4vw] h-[4px] mt-8 bg-[#858585] rounded-full hidden md:block" />
            </div>
            <span className="w-[4px] h-16 bg-[#858585] rounded-full block md:hidden" />
            <div className="flex flex-col items-center space-y-4">
              <div className="h-[5rem] w-[5rem] border-4 border-[#858585] rounded-full flex items-center justify-center">
                <p className="font-bold text-[#858585] text-center">
                  Q2
                  <br />
                  2023
                </p>
              </div>
              <h4 className="font-bold text-xl text-[#858585] text-center max-w-[10rem]">Growing Up</h4>
              <ul className="ml-6 md:ml-8 lg:ml-6 space-y-4 text-[#858585] list-disc">
                <li>Third-Party Extentions</li>
                <li>Device Control</li>
                <li>Multi-Modality</li>
              </ul>
            </div>
            <div>
              <span className="w-[4vw] h-[4px] mt-8 bg-[#858585] rounded-full hidden md:block" />
            </div>
            <span className="w-[4px] h-16 bg-[#858585] rounded-full block md:hidden" />
            <div className="flex flex-col items-center space-y-4">
              <div className="h-[5rem] w-[5rem] border-4 border-[#858585] rounded-full flex items-center justify-center">
                <p className="font-bold text-[#858585] text-center">...</p>
              </div>
              <h4 className="font-bold text-xl text-[#858585] text-center max-w-[10rem]">Growing Up</h4>
              <ul className="ml-6 md:ml-8 lg:ml-6 space-y-4 text-[#858585] list-disc">
                <li>What do you need?</li>
              </ul>
            </div>
          </div>
        </div>
      </Container>

      <CallToAction />
    </div>
  );
};

export default AboutPage;
