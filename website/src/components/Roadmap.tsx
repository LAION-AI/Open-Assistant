import { Container } from "./Container";

const Roadmap = () => {
  return (
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
              <li>Third-Party Extensions</li>
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
  );
};

export default Roadmap;
