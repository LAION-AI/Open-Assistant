import { Box, Heading, Link, Stack, Text, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { getTransparentHeaderLayout } from "src/components/Layout";
import { PolicyChapterCard } from "src/components/PolicyCards/PolicyChapterCard";
import { PolicySectionCard } from "src/components/PolicyCards/PolicySectionCard";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const PrivacyPolicy = () => {
  const backgroundColor = useColorModeValue("gray.100", "gray.800");

  const PrivacyPolicyData = [
    {
      number: "1",
      title: "Definitions",
      desc: "We are required by law that personal data are processed lawfully, in good faith, and in a manner that can be comprehended by the persons who are affected (“lawfulness, fair processing, transparency”). To this end, we hereby inform you about the individual legal definitions of the European General Data Protection Regulation (GDPR) and the new German Federal Data Protection Act, which are also used in these data privacy regulations.",
      sections: [
        {
          number: "1.1",
          title: "Personal Data",
          desc: "'Personal data' means any information relating to an identified or identifiable natural person (hereinafter the 'data subject'). A natural person is considered to be identifiable if he or she can be identified directly or indirectly, in particular by association with an identifier such as a name, an identification number, location data, an online identifier, or one or more special features which express the physical, physiological, genetic, mental, economic, cultural or social identity of the natural person.",
        },
        {
          number: "1.2",
          title: "Restriction of Processing",
          desc: "'Restriction of processing' means the marking of stored personal data with the aim of limiting its processing in the future.",
        },
        {
          number: "1.3",
          title: "Profiling",
          desc: "'Profiling' means any form of automated processing of personal data consisting of the use of personal data to evaluate certain personal aspects relating to a natural person, in particular to analyse or predict aspects concerning that natural person's performance at work, economic situation, health, personal preferences, interests, reliability, behaviour, location or movements.",
        },
        {
          number: "1.4",
          title: "Pseudonymization",
          desc: "'Pseudonymization' means the processing of personal data in such a manner that the personal data can no longer be attributed to a specific data subject without the use of additional information, provided that such additional information is kept separately and is subject to technical and organizational measures to ensure that the personal data is not attributed to an identified or identifiable natural person",
        },
        {
          number: "1.5",
          title: "Filing System",
          desc: "'Filing system' means any structured set of personal data which is accessible according to specific criteria, whether centralized, decentralized or dispersed on a functional or geographical basis.",
        },
        {
          number: "1.6",
          title: "Controller",
          desc: "'Controller' means the natural or legal person, public authority, agency or other body which, alone or jointly with others, determines the purposes and means of the processing of personal data. Where the purposes and means of such processing are determined by European Union or Member State law, the controller or the specific criteria for its nomination may be provided for by European Union or Member State law.",
        },
        {
          number: "1.7",
          title: "Processor",
          desc: "'Processor' means a natural or legal person, public authority, agency or other body which processes personal data on behalf of the controller.",
        },
        {
          number: "1.8",
          title: "Recipient",
          desc: "'Recipient' means a natural or legal person, public authority, agency or another body, to which the personal data is disclosed, whether a third party or not. However, public authorities which may receive potentially personal data in the framework of a particular inquiry in accordance with European Union or Member State law shall not be regarded as recipients. The processing of that data by those public authorities shall be in compliance with the applicable data protection rules according to the purposes of the processing.",
        },
        {
          number: "1.9",
          title: "Third Party",
          desc: "A 'third party' means a natural or legal person, public authority, agency or body other than the data subject, controller, processor and persons who, under the direct authority of the controller or processor, are authorized to process personal data.",
        },
      ],
    },
    {
      number: "2",
      title: "Responsible Controller",
      desc: "Responsible controller is: LAION e.V., Herman-Lange-Weg 26, 21035 Hamburg, Germany",
      sections: [],
    },
    {
      number: "3",
      title: "Data We Collect",
      desc: "Open Assistant tracks data in the following conditions",
      sections: [
        {
          number: "3.1",
          title: "Using the Discord Bot",
          desc: "When using the Open Assistant Discord bot, we privately track and store the unique Discord ID of the user submitting responses. Each submitted response is associated with the user’s Discord ID.",
        },
        {
          number: "3.2",
          title: "Using the Website",
          desc: `When a user registers an account with the website we privately track and store either the unique Discord ID of the user or the unique Email of the registered user. When a user submits responses we store:
          When registered using Discord, we associate the unique Discord ID with each submitted response
          When registered using Email, we associate a unique pseudonymous ID with each submitted response`,
        },
      ],
    },
    {
      number: "4",
      title: "Inquiries",
      desc: "When you contact us via e-mail, telephone or telefax, your inquiry, including all personal data arising thereof will be stored by us for the purpose of processing your request. We will not pass on these data without your consent. The processing of these data is based on Article 6 (1) (1) (b) GDPR, if your inquiry is related to the fulfillment of a contract concluded with us or required for the implementation of pre-contractual measures. Furthermore, the processing is based on Article 6 (1) (1) (f) GDPR, because we have a legitimate interest in the effective handling of requests sent to us. In addition, according to Article 6 (1) (1) (c) GDPR we are also entitled to the processing of the above-mentioned data, because we are legally bound to enable fast electronic contact and immediate communication. Of course, your data will only be used strictly according to purpose and only for processing and responding to your request. After final processing, your data will immediately be anonymized or deleted, unless we are bound by a legally prescribed storage period.",
      sections: [],
    },
    {
      number: "5",
      title: "Processors",
      desc: "In principle, we will never pass on your personal data to third parties without your explicit consent. However, just as every modern business we cooperate with data processors in order to be able to offer you the best possible uninterrupted service. When we cooperate with external service providers, regular order processing is performed, based on Article 28 GDPR. For this purpose, we enter into respective agreements with our partners, in order to safeguard the protection of your data. For processing your data, we only use carefully selected processors. They are bound by our instructions, and regularly controlled by us. We only commission external service provider who have guaranteed that all data processing procedures are performed in unison with data protection regulations. Receivers of personal data may be: Hosting companies and Hosting service providers.",
      sections: [],
    },
    {
      number: "6",
      title: "Children and Young People",
      desc: "In principle, our offer is directed towards adults. Children and young people under the age of 16 are not allowed to transmit personal data to us without the consent of their parents or legal guardians.",
      sections: [],
    },
    {
      number: "7",
      title: "Your Rights",
      desc: "If your personal data is processed on the basis of consent which you have given us, you have the right to revoke your consent at any time. The revocation of consent does not affect the legality of the processing performed on the basis of the consent until the time of revocation. You can contact us at any time to exercise your right to revoke consent.",
      sections: [
        {
          number: "7.1",
          title: "Right to Confirmation",
          desc: "You have the right to request confirmation from the controller that we are processing personal data concerning you. You can request this confirmation at any time using the contact details above.",
        },
        {
          number: "7.2",
          title: "Right to Information",
          desc: "In the event that personal data is processed, you can request information about this personal data and the following information at any time: the purposes of the processing, the categories of personal data being processed, the recipients or categories of recipients to whom the personal data has been or is being disclosed, in particular in the case of recipients in third countries or international organizations, if possible, the planned duration for which the personal data is stored or, if this is not, possible, the criteria for determining this duration, the existence of a right to rectification or erasure of the personal data concerning you, or to a restriction of processing by the controller or a right to object to such processing, the existence of a right to lodge a complaint with a supervisory authority, if the personal data is not collected from the data subject, all available information on the source of the data, the existence of automated decision-making, including profiling, in accordance with Article 22 (1) and (4) GDPR and, at least in these cases, meaningful information about the logic involved and the scope and intended impact of such processing on the data subject. If personal data is transferred to a third country or to an international organization, you have the right to be informed of the appropriate safeguards under Article 46 of the GDPR in connection with the transfer. We provide a copy of the personal data that is the subject of the processing. For any additional copies you request of a person, we may charge a reasonable fee based on our administrative costs. If your request is submitted electronically, the information must be provided in a standard electronic format, unless otherwise stated. The right to receive a copy under paragraph 3 shall not affect the rights and freedoms of others.",
        },
        {
          number: "7.3",
          title: "Right to Rectification",
          desc: "You have the right to demand the immediate correction of incorrect personal data concerning you. Taking into account the purposes of processing, you have the right to request the completion of incomplete personal data, including by means of a supplementary statement.",
        },
        {
          number: "7.4",
          title: "Right to Erasure (Right to be Forgotten)",
          desc: "You have the right to demand that the controller erase personal data concerning you without undue delay, and we are obligated to erase personal data without undue delay where one of the following grounds applies: the personal data are no longer necessary in relation to the purposes for which they were collected or otherwise processed, the data subject withdraws the consent on which the processing is based according to point (a) of Article 6(1), or point (a) of Article 9(2), and there is no other legal ground for the processing, the data subject objects to the processing pursuant to Article 21(1) GDPR and there are no overriding legitimate grounds for the processing, or the data subject objects to the processing pursuant to Article 21(2) GDPR, the personal data have been unlawfully processed, personal data must be erased for compliance with a legal obligation in Union or Member State law to which the controller is subject, the personal data was collected in relation to the offer of information society services referred to in Article 8(1) GDPR. If the controller has made the personal data public and is obliged pursuant to paragraph 1 to erase the personal data, the controller, taking account of available technology and the cost of implementation, shall take reasonable steps, including technical measures, to inform controllers which are processing the personal data that the data subject has requested the erasure by such controllers of any links to, or copy or replication of, that personal data. The right to erasure (“right to be forgotten“) does not apply to the extent that the processing is necessary: to exercise the right of freedom of expression and information, for compliance with a legal obligation which requires processing by Union or Member, State law to which the controller is subject or for the performance of a task carried out in the public interest or in the exercise of official authority vested in the controller, for reasons of public interest in the area of public health in accordance with points (h) and (i) of Article 9(2) as well as Article 9(3) GDPR, for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes in accordance with Article 89(1) GDPR in so far as the right referred to in paragraph 1 is likely to render impossible or seriously impair the achievement of the objectives of that processing; or for the establishment, exercise or defense of legal claims",
        },
        {
          number: "7.5",
          title: "Right to Restriction of Processing",
          desc: "You have the right to request that we restrict the processing of your personal data if any of the following conditions apply: the accuracy of the personal data is contested by the data subject, for a period enabling the controller to verify the accuracy of the personal data, the processing is unlawful and the data subject opposes the erasure of the personal data and requests the restriction of their use instead, the controller no longer needs the personal data for the purposes of the processing, but the data is required by the data subject for the establishment, exercise or defense of legal claims, or the data subject has objected to processing pursuant to Article 21(1) GDPR pending the verification whether the legitimate grounds of the controller override those of the data subject In the event that processing has been restricted under the aforementioned conditions, this personal data shall – with the exception of storage – only be processed with the data subject’s consent or for the establishment, exercise or defense of legal claims or for the protection of the rights of another natural or legal person or for reasons of important public interest of the Union or of a Member State. In order to exercise the right to restrict processing, the data subject may contact us at any time using the contact details provided above.",
        },
        {
          number: "7.6",
          title: "Right to Data Portability",
          desc: "You have the right to receive the personal data concerning you which you have provided to us in a structured, commonly used and machine-readable format and have the right to transmit that data to another controller without hindrance from the controller to which the personal data have been provided, to the extent that: the processing is based on consent pursuant to point (a) of Article 6 (1) or point (a) of Article 9 (2) or on a contract pursuant to point (b) of Article 6 (1) GDPR and the processing is carried out by automated means. In exercising your right to data portability pursuant to paragraph 1, you have the right to have the personal data transmitted directly from one controller to another, to the extent that this is technically feasible. The exercise of the right to data portability does not affect your right to erasure (“right to be forgotten”). That right shall not apply to processing necessary for the performance of a task carried out in the public interest or in the exercise of official authority vested in the controller.",
        },
        {
          number: "7.7",
          title: "Right to Object",
          desc: "You have the right to object, on grounds relating to your particular situation, at any time to processing of personal data which concerns you which is based on point (e) or (f) of Article 6 (1) GDPR, including profiling based on those provisions. If objection is made, the controller will no longer process the personal data unless the controller demonstrates compelling legitimate grounds for the processing which override the interests, rights and freedoms of the data subject or for the establishment, exercise or defense of legal claims. In the event that personal data is processed for direct marketing purposes, you have the right to object at any time to processing of personal data concerning you for such marketing. This also applies to profiling to the extent that it is related to such direct marketing. If you object to processing for direct marketing purposes, your personal data shall no longer be processed for such purposes. Regarding the use of information society services, and notwithstanding Directive 2002/58/EC, you can exercise your right to object by automated means using technical specifications. Where personal data are processed for scientific or historical research purposes or statistical purposes pursuant to Article 89 (1), you, on grounds relating to your particular situation, have the right to object to processing of personal data concerning you, unless the processing is necessary for the performance of a task carried out for reasons of public interest. The right of objection can be exercised at any time by contacting the respective controller.",
        },
        {
          number: "7.8",
          title: "Automated Individual Decision-Making, Including Profiling",
          desc: "You have the right not to be subject to a decision based solely on automated processing, including profiling, which produces legal effects for you or similarly significantly affects you. This does not apply if the decision: is necessary for entering into, or performance of, a contract between the data subject and a data controller, is authorized by Union or Member State law to which the controller is subject and which also lays down suitable measures to safeguard the data subject’s rights and freedoms and legitimate interests, or is based on the data subject’s explicit consent. The controller shall implement suitable measures to safeguard the data subject’s rights and freedoms and legitimate interests, at least the right to obtain human intervention on the part of the controller, to express his or her point of view and to contest the decision. This right can be exercised by the data subject at any time by contacting the respective controller.",
        },
        {
          number: "7.9",
          title: "Right to Lodge A Complaint With A Supervisory Authority",
          desc: "You also have the right, without prejudice to any other administrative or judicial remedy, to lodge a complaint with a supervisory authority, in particular in the Member State of your habitual residence, place of work or place of the alleged infringement if you as data subject consider that the processing of personal data relating to you infringes this Regulation.",
        },
        {
          number: "7.10",
          title: "Right to Effective Judicial Remedy",
          desc: "Without prejudice to any other available administrative or judicial remedy, including the right to lodge a complaint with a supervisory authority pursuant to Article 77 GDPR, you have the right to an effective judicial remedy if you consider that your rights under this Regulation have been infringed as a result of the processing of your personal data in breach of this Regulation.",
        },
      ],
    },
  ];

  return (
    <>
      <Head>
        <title>Privacy Policy - Open Assistant</title>
        <meta name="description" content="Open Assistant's Privacy Policy" />
      </Head>
      <Box fontFamily="Inter" p="6" className="oa-basic-theme">
        <Box className="max-w-4xl mx-auto">
          <Stack spacing="6" mb="6">
            <Heading as="h1" size="xl" color="blue.500">
              Privacy Policy
            </Heading>

            <Box bg={backgroundColor} p="6" pt="4" borderRadius="xl" shadow="base">
              <Stack>
                <Heading as="h3" size="lg">
                  Overview
                </Heading>
                <Text>
                  We are pleased that you are interested in our work and welcome you to our website open-assistant.io.
                  In this Privacy Policy you will learn which personal data we process when you visit our website and to
                  what kind of purpose, and also what rights you have regarding these data. Categorically, we only store
                  data as long as we need them. There is no legal obligation to provide us with personal data. Automated
                  decision-making, as per Article 22 of the EU-GDPR, will not happen.
                </Text>
              </Stack>
            </Box>
          </Stack>

          <Stack spacing="8">
            {PrivacyPolicyData.map((chapter, chapterIndex) => (
              <PolicyChapterCard key={chapterIndex} chapter={chapter}>
                {chapter.sections && chapter.sections.length
                  ? chapter.sections.map((section, sectionIndex) => (
                      <PolicySectionCard key={sectionIndex} section={section} />
                    ))
                  : ""}
              </PolicyChapterCard>
            ))}
          </Stack>

          <Box bg={backgroundColor} p="6" pt="4" mt="8" borderRadius="xl" shadow="base">
            <Stack>
              <Heading as="h3" size="lg">
                Submitting Requests
              </Heading>
              <Text>
                Email:{" "}
                <Link href="mailto:privacy@open-assistant.io" color="blue.500" fontWeight="bold">
                  privacy@open-assistant.io
                </Link>
              </Text>
            </Stack>
          </Box>
        </Box>
      </Box>
    </>
  );
};

PrivacyPolicy.getLayout = getTransparentHeaderLayout;

export default PrivacyPolicy;
