import Image from "next/image";
import { Container } from "src/components/Container";

const Vision = () => {
  return (
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
  );
};

export default Vision;
