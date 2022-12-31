import { Container } from "./Container";

const faqs = [
  [
    {
      question: "How far along is this project?",
      answer:
        "We are in the early stages of development, working from established research in applying RLHF to large language models.",
    },
  ],
  [
    {
      question: "Who is behind Open Assistant?",
      answer:
        "Open Assistant is a project organized by LAION and individuals around the world interested in bringing this technology to everyone.",
    },
  ],
  [
    // {
    //   question: 'Where can I learn more?',
    //   answer:
    //     'Please feel free to reach out to us on Discord. We are happy to answer any questions you may have.',
    // },
  ],
];

export function Faq() {
  return (
    <section id="faq" aria-labelledby="faqs-title" className="border-t border-gray-200 py-20 sm:py-32">
      <Container className="">
        <div className="mx-auto max-w-2xl lg:mx-0">
          <h2 id="faqs-title" className="text-3xl font-medium tracking-tight text-gray-900">
            Frequently Asked Questions
          </h2>
          {/* <p className="mt-2 text-lg text-gray-600">
            If you have anything else you want to ask,{' '}
            <Link
              href="mailto:info@open-assistant.tech"
              className="text-gray-900 underline"
            >
              reach out to us
            </Link>
            .
          </p> */}
        </div>
        <ul
          role="list"
          className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-8 sm:mt-20 lg:max-w-none lg:grid-cols-3"
        >
          {faqs.map((column, columnIndex) => (
            <li key={columnIndex}>
              <ul role="list" className="space-y-10">
                {column.map((faq, faqIndex) => (
                  <li key={faqIndex}>
                    <h3 className="text-lg font-semibold leading-6 text-gray-900">{faq.question}</h3>
                    <p className="mt-4 text-sm text-gray-700">{faq.answer}</p>
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </Container>
    </section>
  );
}
