import Image from "next/image";
import { Container } from "src/components/Container";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const BrbPage = () => {
  return (
    <div>
      <Container className="">
        <div className="grid gap-16 items-center py-20 md:py-40 lg:grid-cols-2">
          <div className="m-auto order-2 lg:order-1">
            <Image src="/images/logos/logo.png" width={450} height={450} alt="temp-image" />
          </div>
          <div className="space-y-8 order-1 lg:order-2">
            <div>
              <h1 className="text-4xl mb-6">Down for maintenance</h1>
            </div>
            <p className="text-2xl">{"We are improving the service, we'll be back in very few minutes."}</p>
          </div>
        </div>
      </Container>
    </div>
  );
};

export default BrbPage;
