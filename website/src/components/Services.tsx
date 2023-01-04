import { Container } from "./Container";

const Services = () => {
  return (
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
            <h4 className="font-bold text-white text-xl mb-4">OpenAssistant unifies all knowledge work in one place</h4>
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
  );
};

export default Services;
