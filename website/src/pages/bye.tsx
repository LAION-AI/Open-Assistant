import Image from "next/image";
import Link from "next/link";
import { Container } from "src/components/Container";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const ByePage = () => {
  return (
    <div>
      <Container className="">
        <div className="grid gap-16 items-center py-20 md:py-40 lg:grid-cols-2">
          <div className="m-auto order-2 lg:order-1">
            <Image src="/images/logos/logo.png" width={450} height={450} alt="temp-image" />
          </div>
          <div className="space-y-8 order-1 lg:order-2">
            <div>
              <h1 className="text-4xl mb-6">OpenAssistant has finished!</h1>
              <p className="text-2xl">
                OpenAssistant collected data from over 13&apos;000 humans and released it to the public. Data, models,
                and code are publicly available.
              </p>
              <h2 className="text-2xl font-bold mt-4 mb-2">Links:</h2>
              <ul className="text-2xl list-none text-blue-500">
                <li>
                  <Link href="/contributors">List of contributors</Link>
                </li>
                <li>
                  <a href="https://ykilcher.com/oa-paper">Paper</a>
                </li>
                <li>
                  <a href="https://github.com/LAION-AI/Open-Assistant">GitHub</a>
                </li>
                <li>
                  <a href="https://huggingface.co/OpenAssistant">HuggingFace org</a>
                </li>
                <li>
                  <a href="https://youtu.be/gqtmUHhaplo">Yannic&apos;s conclusion video</a>
                </li>
              </ul>
              <p className="text-2xl mt-4 mb-2">
                If you&apos;re looking to support other open-data projects, check out these:
              </p>
              <ul className="text-2xl list-none text-blue-500">
                <li>
                  <a href="https://chat.lmsys.org/">LMSYS Chatbot Arena</a>
                </li>
                <li>
                  <a href="https://laion.ai/blog/open-empathic/">Open Empathic</a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </Container>
    </div>
  );
};

export default ByePage;
