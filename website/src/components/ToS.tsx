import { Stack } from "@chakra-ui/react";
import { PolicyChapterCard } from "src/components/PolicyCards/PolicyChapterCard";
import { PolicySectionCard } from "src/components/PolicyCards/PolicySectionCard";

const TermsData = [
  {
    number: "1",
    title: "Scope of Application, Amendments",
    desc: "",
    sections: [
      {
        number: "1.1",
        title: "",
        desc: `LAION e.V., Herman-Lange-Weg 26, 21035 Hamburg, Germany (hereinafter referred to as: "LAION") operates an online portal for the producing a machine learning model called Open Assistant using crowd-sourced data.`,
      },
      {
        number: "1.2",
        title: "",
        desc: "The present terms of use regulate the user relationship between the users of the portal and LAION.",
      },
      {
        number: "1.3",
        title: "",
        desc: "LAION reserves the right to amend these Terms of Use at any time, also with regard to persons already registered, if this becomes necessary due to changes in the law, changes in jurisdiction, changes in economic circumstances or gaps in these Terms of Use that subsequently become apparent. The user will be informed of such changes in good time by e-mail The user has the opportunity to object to the changes within 14 days of receipt of this e-mail. If the user does not object to the changes and continues to use the portal after expiry of the objection period, the changes shall be deemed to have been agreed effectively from the expiry of the period. If the user objects to the changes within the two-week period, LAION shall be entitled to exclude the user from using the portal. The user shall be informed of these effects once again in the e-mail.",
      },
    ],
  },
  {
    number: "2",
    title: "Subject of Use, Availability of the Service",
    desc: "",
    sections: [
      {
        number: "2.1",
        title: "",
        desc: "The portal serves as a platform for creating data to train an interactive agent for scientific purposes. All text and prompt generated through the service are used for scientific purposes, in particular for the optimization of the AI.",
      },
      {
        number: "2.2",
        title: "",
        desc: "The input of texts on the portal and the subsequent generation of text by the artificial intelligence provided by the portal do not give rise to any works protected by copyright. The user who has entered the text for the generation of the text shall have neither the exclusive rights of use nor any rights of an author to the generated text.",
      },
      {
        number: "2.3",
        title: "",
        desc: "LAION shall endeavour to ensure that the portal can be used as uninterruptedly as possible. However, there shall be no legal claim to the use of the portal. LAION reserves the right, at its own discretion, to change the portal at any time and without notice, to discontinue its operation or to exclude individual users from using it. Furthermore, it cannot be ruled out that temporary restrictions or interruptions may occur due to technical faults (such as interruption of the power supply, hardware and software errors, technical problems in the data lines).",
      },
    ],
  },
  {
    number: "3",
    title: "User Obligations",
    desc: "",
    sections: [
      {
        number: "3.1",
        title: "",
        desc: "The user may only use the portal for the intended purposes. In particular, he/she may not misuse the portal. The user undertakes to refrain from generating text that violate criminal law, youth protection regulations or the applicable laws of the following countries: Federal Republic of Germany, United States of America (USA), Great Britain, user's place of residence. In particular it is prohibited to enter texts that lead to the creation of pornographic, violence-glorifying or paedosexual content and/or content that violates the personal rights of third parties. LAION reserves the right to file a criminal complaint with the competent authorities in the event of violations.",
      },
      {
        number: "3.2",
        title: "",
        desc: "The user undertakes not to use any programs, algorithms or other software in connection with the use of the portal which could interfere with the functioning of the portal. Furthermore, the user shall not take any measures that may result in an unreasonable or excessive load on the infrastructure of the portal or may interfere with it in a disruptive manner.",
      },
      {
        number: "3.3",
        title: "",
        desc: "If a user notices obvious errors in the portal which could lead to misuse of the portal or the contents contained therein, the user shall be obliged to report the error to LAION without delay.",
      },
      {
        number: "3.4",
        title: "",
        desc: "The use, distribution, storage, forwarding, editing and/or other use of images that violate these terms of use is prohibited.",
      },
    ],
  },
  {
    number: "4",
    title: "Liability",
    desc: "",
    sections: [
      {
        number: "4.1",
        title: "",
        desc: "LAION accepts no liability for the accuracy, completeness, reliability, up-to-dateness and usability of the content.",
      },
      {
        number: "4.2",
        title: "",
        desc: "LAION shall be liable without limitation for intent and gross negligence. In the case of simple negligence, LAION shall only be liable for damage resulting from injury to life, limb or health or an essential contractual obligation (obligation the fulfillment of which makes the proper performance of the contract possible in the first place and on the observance of which the contractual partner regularly trusts and may trust).",
      },
      {
        number: "4.3",
        title: "",
        desc: "In the event of a breach of material contractual obligations due to simple negligence, the liability of LAION shall be limited to the amount of the foreseeable, typically occurring damage. In all other respects liability shall be excluded.",
      },
      {
        number: "4.4",
        title: "",
        desc: "The above limitations of liability shall also apply in favour of the legal representatives and vicarious agents of LAION.",
      },
      {
        number: "4.5",
        title: "",
        desc: "LAION shall not be liable for the loss of data of the user. The user shall be solely responsible for the secure storage of his/her data.",
      },
      {
        number: "4.6",
        title: "",
        desc: "LAION shall not be liable for any damages incurred by the user as a result of the violation of these terms of use.",
      },
      {
        number: "4.7",
        title: "",
        desc: "LAION shall not be liable for the use of content generated on the portal by text input outside the portal. In particular, LAION shall not be liable for any damages incurred by the user due to the assumption of copyrights or exclusive rights of use.",
      },
    ],
  },
  {
    number: "5",
    title: "Data Protection",
    desc: "",
    sections: [
      {
        number: "5.1",
        title: "",
        desc: "LAION processes the personal data of users in accordance with the provisions of data protection law. Detailed information can be found in the privacy policy, available at: /privacy-policy.",
      },
      {
        number: "5.2",
        title: "",
        desc: "The user expressly agrees that communication within the scope of and for the purpose of the user relationship between him/her and LAION may also take place via unencrypted e-mails. The user is aware that unencrypted e-mails only offer limited security and confidentiality.",
      },
    ],
  },
  {
    number: "6",
    title: "Final Provisions",
    desc: "",
    sections: [
      {
        number: "6.1",
        title: "",
        desc: "The contractual relationship shall be governed exclusively by the law of the Federal Republic of Germany to the exclusion of the UN Convention on Contracts for the International Sale of Goods.",
      },
      {
        number: "6.2",
        title: "",
        desc: "Should individual provisions of these GTC including this provision be or become invalid in whole or in part, the validity of the remaining provisions shall remain unaffected. The invalid or missing provisions shall be replaced by the respective statutory provisions.",
      },
      {
        number: "6.3",
        title: "",
        desc: "If the customer is a merchant, a legal entity under public law or a special fund under public law, the place of jurisdiction for all disputes arising from and in connection with contracts concluded under these terms of use shall be the registered office of LAION.",
      },
    ],
  },
];

export const TermsOfService = () => (
  <Stack spacing="8">
    {TermsData.map((chapter, chapterIndex) => (
      <PolicyChapterCard key={chapterIndex} chapter={chapter}>
        {chapter.sections && chapter.sections.length
          ? chapter.sections.map((section, sectionIndex) => <PolicySectionCard key={sectionIndex} section={section} />)
          : ""}
      </PolicyChapterCard>
    ))}
  </Stack>
);
