export interface ChapterInfo {
  id: number;
  number: string;
  title: string;
  desc: string;
  sections: SectionInfo[];
}

export interface SectionInfo {
  id: number;
  number: string;
  title: string;
  desc: string;
}

export const TermsData: ChapterInfo[] = [
  {
    id: 1,
    number: "1",
    title: "Scope of Application, Amendments",
    desc: "",
    sections: [
      {
        id: 1,
        number: "1.1",
        title: "",
        desc: `LAION (association in formation), Marie-Henning-Weg 143, 21035 Hamburg (hereinafter referred to as: "LAION") operates an online portal for the producing a machine learning model called Open Assistant using crowdsourced data.`,
      },
      {
        id: 1,
        number: "1.2",
        title: "",
        desc: "The present terms of use regulate the user relationship between the users of the portal and LAION.",
      },
      {
        id: 1,
        number: "1.3",
        title: "",
        desc: "LAION reserves the right to amend these Terms of Use at any time, also with regard to persons already registered, if this becomes necessary due to changes in the law, changes in jurisdiction, changes in economic circumstances or gaps in these Terms of Use that subsequently become apparent. The user will be informed of such changes in good time by e-mail The user has the opportunity to object to the changes within 14 days of receipt of this e-mail. If the user does not object to the changes and continues to use the portal after expiry of the objection period, the changes shall be deemed to have been agreed effectively from the expiry of the period. If the user objects to the changes within the two-week period, LAION shall be entitled to exclude the user from using the portal. The user shall be informed of these effects once again in the e-mail.",
      },
    ],
  },
  {
    id: 2,
    number: "2",
    title: "Subject of Use, Availability of the Service",
    desc: "",
    sections: [
      {
        id: 1,
        number: "2.1",
        title: "",
        desc: "The portal serves as a platform for creating data to train an interactive agent for scientific purposes. All text and prompt generated through the service are used for scientific purposes, in particular for the optimization of the AI.",
      },
      {
        id: 1,
        number: "2.2",
        title: "",
        desc: "The input of texts on the portal and the subsequent generation of text by the artificial intelligence provided by the portal do not give rise to any works protected by copyright. The user who has entered the text for the generation of the text shall have neither the exclusive rights of use nor any rights of an author to the generated text.",
      },
      {
        id: 1,
        number: "2.3",
        title: "",
        desc: "LAION shall endeavour to ensure that the portal can be used as uninterruptedly as possible. However, there shall be no legal claim to the use of the portal. LAION reserves the right, at its own discretion, to change the portal at any time and without notice, to discontinue its operation or to exclude individual users from using it. Furthermore, it cannot be ruled out that temporary restrictions or interruptions may occur due to technical faults (such as interruption of the power supply, hardware and software errors, technical problems in the data lines).",
      },
    ],
  },
  {
    id: 3,
    number: "3",
    title: "User Obligations",
    desc: "",
    sections: [
      {
        id: 1,
        number: "3.1",
        title: "",
        desc: "The user may only use the portal for the intended purposes. In particular, he/she may not misuse the portal. The user undertakes to refrain from generating text that violate criminal law, youth protection regulations or the applicable laws of the following countries: Federal Republic of Germany, United States of America (USA), Great Britain, user's place of residence. In particular it is prohibited to enter texts that lead to the creation of pornographic, violence-glorifying or paedosexual content and/or content that violates the personal rights of third parties. LAION reserves the right to file a criminal complaint with the competent authorities in the event of violations.",
      },
      {
        id: 1,
        number: "3.2",
        title: "",
        desc: "The user undertakes not to use any programs, algorithms or other software in connection with the use of the portal which could interfere with the functioning of the portal. Furthermore, the user shall not take any measures that may result in an unreasonable or excessive load on the infrastructure of the portal or may interfere with it in a disruptive manner.",
      },
      {
        id: 1,
        number: "3.3",
        title: "",
        desc: "If a user notices obvious errors in the portal which could lead to misuse of the portal or the contents contained therein, the user shall be obliged to report the error to LAION without delay.",
      },
      {
        id: 1,
        number: "3.4",
        title: "",
        desc: "The use, distribution, storage, forwarding, editing and/or other use of images that violate these terms of use is prohibited.",
      },
    ],
  },
  {
    id: 4,
    number: "4",
    title: "Liability",
    desc: "",
    sections: [
      {
        id: 1,
        number: "4.1",
        title: "",
        desc: "LAION accepts no liability for the accuracy, completeness, reliability, up-to-dateness and usability of the content.",
      },
      {
        id: 1,
        number: "4.2",
        title: "",
        desc: "LAION shall be liable without limitation for intent and gross negligence. In the case of simple negligence, LAION shall only be liable for damage resulting from injury to life, limb or health or an essential contractual obligation (obligation the fulfillment of which makes the proper performance of the contract possible in the first place and on the observance of which the contractual partner regularly trusts and may trust).",
      },
      {
        id: 1,
        number: "4.3",
        title: "",
        desc: "In the event of a breach of material contractual obligations due to simple negligence, the liability of LAION shall be limited to the amount of the foreseeable, typically occurring damage. In all other respects liability shall be excluded.",
      },
      {
        id: 1,
        number: "4.4",
        title: "",
        desc: "The above limitations of liability shall also apply in favour of the legal representatives and vicarious agents of LAION.",
      },
      {
        id: 1,
        number: "4.5",
        title: "",
        desc: "LAION shall not be liable for the loss of data of the user. The user shall be solely responsible for the secure storage of his/her data.",
      },
      {
        id: 1,
        number: "4.6",
        title: "",
        desc: "LAION shall not be liable for any damages incurred by the user as a result of the violation of these terms of use.",
      },
      {
        id: 1,
        number: "4.7",
        title: "",
        desc: "LAION shall not be liable for the use of content generated on the portal by text input outside the portal. In particular, LAION shall not be liable for any damages incurred by the user due to the assumption of copyrights or exclusive rights of use.",
      },
    ],
  },
  {
    id: 5,
    number: "5",
    title: "Data Protection",
    desc: "",
    sections: [
      {
        id: 1,
        number: "5.1",
        title: "",
        desc: "LAION processes the personal data of users in accordance with the provisions of data protection law. Detailed information can be found in the privacy policy, available at: /privacy-policy.",
      },
      {
        id: 1,
        number: "5.2",
        title: "",
        desc: "The user expressly agrees that communication within the scope of and for the purpose of the user relationship between him/her and LAION may also take place via unencrypted e-mails. The user is aware that unencrypted e-mails only offer limited security and confidentiality.",
      },
    ],
  },
  {
    id: 6,
    number: "6",
    title: "Final Provisions",
    desc: "",
    sections: [
      {
        id: 1,
        number: "6.1",
        title: "",
        desc: "The contractual relationship shall be governed exclusively by the law of the Federal Republic of Germany to the exclusion of the UN Convention on Contracts for the International Sale of Goods.",
      },
      {
        id: 1,
        number: "6.2",
        title: "",
        desc: "Should individual provisions of these GTC including this provision be or become invalid in whole or in part, the validity of the remaining provisions shall remain unaffected. The invalid or missing provisions shall be replaced by the respective statutory provisions.",
      },
      {
        id: 1,
        number: "6.3",
        title: "",
        desc: "If the customer is a merchant, a legal entity under public law or a special fund under public law, the place of jurisdiction for all disputes arising from and in connection with contracts concluded under these terms of use shall be the registered office of LAION.",
      },
    ],
  },
];

export const PrivacyPolicyData: ChapterInfo[] = [
  {
    id: 1,
    number: "1",
    title: "Definitions",
    desc: "We are required by law that personal data are processed lawfully, in good faith, and in a manner that can be comprehended by the persons who are affected (“lawfulness, fair processing, transparency”). To this end, we hereby inform you about the individual legal definitions of the European General Data Protection Regulation (GDPR) and the new German Federal Data Protection Act, which are also used in these data privacy regulations.",
    sections: [
      {
        id: 1,
        number: "1.1",
        title: "Personal Data",
        desc: "'Personal data' means any information relating to an identified or identifiable natural person (hereinafter the 'data subject'). A natural person is considered to be identifiable if he or she can be identified directly or indirectly, in particular by association with an identifier such as a name, an identification number, location data, an online identifier, or one or more special features which express the physical, physiological, genetic, mental, economic, cultural or social identity of the natural person.",
      },
      {
        id: 1,
        number: "1.2",
        title: "Restriction of Processing",
        desc: "'Restriction of processing' means the marking of stored personal data with the aim of limiting its processing in the future.",
      },
      {
        id: 1,
        number: "1.3",
        title: "Profiling",
        desc: "'Profiling' means any form of automated processing of personal data consisting of the use of personal data to evaluate certain personal aspects relating to a natural person, in particular to analyse or predict aspects concerning that natural person's performance at work, economic situation, health, personal preferences, interests, reliability, behaviour, location or movements.",
      },
      {
        id: 1,
        number: "1.4",
        title: "Pseudonymization",
        desc: "'Pseudonymization' means the processing of personal data in such a manner that the personal data can no longer be attributed to a specific data subject without the use of additional information, provided that such additional information is kept separately and is subject to technical and organizational measures to ensure that the personal data is not attributed to an identified or identifiable natural person",
      },
      {
        id: 1,
        number: "1.5",
        title: "Filing System",
        desc: "'Filing system' means any structured set of personal data which is accessible according to specific criteria, whether centralized, decentralized or dispersed on a functional or geographical basis.",
      },
      {
        id: 1,
        number: "1.6",
        title: "Controller",
        desc: "'Controller' means the natural or legal person, public authority, agency or other body which, alone or jointly with others, determines the purposes and means of the processing of personal data. Where the purposes and means of such processing are determined by European Union or Member State law, the controller or the specific criteria for its nomination may be provided for by European Union or Member State law.",
      },
      {
        id: 1,
        number: "1.7",
        title: "Processor",
        desc: "'Processor' means a natural or legal person, public authority, agency or other body which processes personal data on behalf of the controller.",
      },
      {
        id: 1,
        number: "1.8",
        title: "Recipient",
        desc: "'Recipient' means a natural or legal person, public authority, agency or another body, to which the personal data is disclosed, whether a third party or not. However, public authorities which may receive potentially personal data in the framework of a particular inquiry in accordance with European Union or Member State law shall not be regarded as recipients. The processing of that data by those public authorities shall be in compliance with the applicable data protection rules according to the purposes of the processing.",
      },
      {
        id: 1,
        number: "1.9",
        title: "Third Party",
        desc: "A 'third party' means a natural or legal person, public authority, agency or body other than the data subject, controller, processor and persons who, under the direct authority of the controller or processor, are authorized to process personal data.",
      },
    ],
  },
  {
    id: 2,
    number: "2",
    title: "Responsible Controller",
    desc: "Responsible controller is: LAION e.V., Marie-Henning-Weg 143, 21035 Hamburg, Germany",
    sections: [],
  },
  {
    id: 3,
    number: "3",
    title: "Data We Collect",
    desc: "Open Assistant tracks data in the following conditions",
    sections: [
      {
        id: 1,
        number: "3.1",
        title: "Using the Discord Bot",
        desc: "When using the Open Assistant Discord bot, we privately track and store the unique Discord ID of the user submitting responses. Each submitted response is associated with the user’s Discord ID.",
      },
      {
        id: 1,
        number: "3.2",
        title: "Using the Website",
        desc: `When a user registers an account with the website we privately track and store either the unique Discord ID of the user or the unique Email of the registered user. When a user submits responses we store:
        When registered using Discord, we associate the unique Discord ID with each submitted response
        When registered using Email, we associate a unique pseudonymous ID with each submitted response`,
      },
    ],
  },
  {
    id: 4,
    number: "4",
    title: "Inquiries",
    desc: "When you contact us via e-mail, telephone or telefax, your inquiry, including all personal data arising thereof will be stored by us for the purpose of processing your request. We will not pass on these data without your consent. The processing of these data is based on Article 6 (1) (1) (b) GDPR, if your inquiry is related to the fulfilment of a contract concluded with us or required for the implementation of pre-contractual measures. Furthermore, the processing is based on Article 6 (1) (1) (f) GDPR, because we have a legitimate interest in the effective handling of requests sent to us. In addition, according to Article 6 (1) (1) (c) GDPR we are also entitled to the processing of the above-mentioned data, because we are legally bound to enable fast electronic contact and immediate communication. Of course, your data will only be used strictly according to purpose and only for processing and responding to your request. After final processing, your data will immediately be anonymized or deleted, unless we are bound by a legally prescribed storage period.",
    sections: [],
  },
  {
    id: 5,
    number: "5",
    title: "Processors",
    desc: "In principle, we will never pass on your personal data to third parties without your explicit consent. However, just as every modern business we cooperate with data processors in order to be able to offer you the best possible uninterrupted service. When we cooperate with external service providers, regular order processing is performed, based on Article 28 GDPR. For this purpose, we enter into respective agreements with our partners, in order to safeguard the protection of your data. For processing your data, we only use carefully selected processors. They are bound by our instructions, and regularly controlled by us. We only commission external service provider who have guaranteed that all data processing procedures are performed in unison with data protection regulations. Receivers of personal data may be: Hosting companies and Hosting service providers.",
    sections: [],
  },
  {
    id: 6,
    number: "6",
    title: "Children and Young People",
    desc: "In principle, our offer is directed towards adults. Children and young people under the age of 16 are not allowed to transmit personal data to us without the consent of their parents or legal guardians.",
    sections: [],
  },
  {
    id: 7,
    number: "7",
    title: "Your Rights",
    desc: "If your personal data is processed on the basis of consent which you have given us, you have the right to revoke your consent at any time. The revocation of consent does not affect the legality of the processing performed on the basis of the consent until the time of revocation. You can contact us at any time to exercise your right to revoke consent.",
    sections: [
      {
        id: 1,
        number: "7.1",
        title: "Right to Confirmation",
        desc: "You have the right to request confirmation from the controller that we are processing personal data concerning you. You can request this confirmation at any time using the contact details above.",
      },
      {
        id: 1,
        number: "7.2",
        title: "Right to Information",
        desc: "In the event that personal data is processed, you can request information about this personal data and the following information at any time: the purposes of the processing, the categories of personal data being processed, the recipients or categories of recipients to whom the personal data has been or is being disclosed, in particular in the case of recipients in third countries or international organizations, if possible, the planned duration for which the personal data is stored or, if this is not, possible, the criteria for determining this duration, the existence of a right to rectification or erasure of the personal data concerning you, or to a restriction of processing by the controller or a right to object to such processing, the existence of a right to lodge a complaint with a supervisory authority, if the personal data is not collected from the data subject, all available information on the source of the data, the existence of automated decision-making, including profiling, in accordance with Article 22 (1) and (4) GDPR and, at least in these cases, meaningful information about the logic involved and the scope and intended impact of such processing on the data subject. If personal data is transferred to a third country or to an international organization, you have the right to be informed of the appropriate safeguards under Article 46 of the GDPR in connection with the transfer. We provide a copy of the personal data that is the subject of the processing. For any additional copies you request of a person, we may charge a reasonable fee based on our administrative costs. If your request is submitted electronically, the information must be provided in a standard electronic format, unless otherwise stated. The right to receive a copy under paragraph 3 shall not affect the rights and freedoms of others.",
      },
      {
        id: 1,
        number: "7.3",
        title: "Right to Rectification",
        desc: "You have the right to demand the immediate correction of incorrect personal data concerning you. Taking into account the purposes of processing, you have the right to request the completion of incomplete personal data, including by means of a supplementary statement.",
      },
      {
        id: 1,
        number: "7.4",
        title: "Right to Erasure (Right to be Forgotten)",
        desc: "You have the right to demand that the controller erase personal data concerning you without undue delay, and we are obligated to erase personal data without undue delay where one of the following grounds applies: the personal data are no longer necessary in relation to the purposes for which they were collected or otherwise processed, the data subject withdraws the consent on which the processing is based according to point (a) of Article 6(1), or point (a) of Article 9(2), and there is no other legal ground for the processing, the data subject objects to the processing pursuant to Article 21(1) GDPR and there are no overriding legitimate grounds for the processing, or the data subject objects to the processing pursuant to Article 21(2) GDPR, the personal data have been unlawfully processed, personal data must be erased for compliance with a legal obligation in Union or Member State law to which the controller is subject, the personal data was collected in relation to the offer of information society services referred to in Article 8(1) GDPR. If the controller has made the personal data public and is obliged pursuant to paragraph 1 to erase the personal data, the controller, taking account of available technology and the cost of implementation, shall take reasonable steps, including technical measures, to inform controllers which are processing the personal data that the data subject has requested the erasure by such controllers of any links to, or copy or replication of, that personal data. The right to erasure (“right to be forgotten“) does not apply to the extent that the processing is necessary: to exercise the right of freedom of expression and information, for compliance with a legal obligation which requires processing by Union or Member, State law to which the controller is subject or for the performance of a task carried out in the public interest or in the exercise of official authority vested in the controller, for reasons of public interest in the area of public health in accordance with points (h) and (i) of Article 9(2) as well as Article 9(3) GDPR, for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes in accordance with Article 89(1) GDPR in so far as the right referred to in paragraph 1 is likely to render impossible or seriously impair the achievement of the objectives of that processing; or for the establishment, exercise or defense of legal claims",
      },
      {
        id: 1,
        number: "7.5",
        title: "Right to Restriction of Processing",
        desc: "You have the right to request that we restrict the processing of your personal data if any of the following conditions apply: the accuracy of the personal data is contested by the data subject, for a period enabling the controller to verify the accuracy of the personal data, the processing is unlawful and the data subject opposes the erasure of the personal data and requests the restriction of their use instead, the controller no longer needs the personal data for the purposes of the processing, but the data is required by the data subject for the establishment, exercise or defense of legal claims, or the data subject has objected to processing pursuant to Article 21(1) GDPR pending the verification whether the legitimate grounds of the controller override those of the data subject In the event that processing has been restricted under the aforementioned conditions, this personal data shall – with the exception of storage – only be processed with the data subject’s consent or for the establishment, exercise or defense of legal claims or for the protection of the rights of another natural or legal person or for reasons of important public interest of the Union or of a Member State. In order to exercise the right to restrict processing, the data subject may contact us at any time using the contact details provided above.",
      },
      {
        id: 1,
        number: "7.6",
        title: "Right to Data Portability",
        desc: "You have the right to receive the personal data concerning you which you have provided to us in a structured, commonly used and machine-readable format and have the right to transmit that data to another controller without hindrance from the controller to which the personal data have been provided, to the extent that: the processing is based on consent pursuant to point (a) of Article 6 (1) or point (a) of Article 9 (2) or on a contract pursuant to point (b) of Article 6 (1) GDPR and the processing is carried out by automated means. In exercising your right to data portability pursuant to paragraph 1, you have the right to have the personal data transmitted directly from one controller to another, to the extent that this is technically feasible. The exercise of the right to data portability does not affect your right to erasure (“right to be forgotten”). That right shall not apply to processing necessary for the performance of a task carried out in the public interest or in the exercise of official authority vested in the controller.",
      },
      {
        id: 1,
        number: "7.7",
        title: "Right to Object",
        desc: "You have the right to object, on grounds relating to your particular situation, at any time to processing of personal data which concerns you which is based on point (e) or (f) of Article 6 (1) GDPR, including profiling based on those provisions. If objection is made, the controller will no longer process the personal data unless the controller demonstrates compelling legitimate grounds for the processing which override the interests, rights and freedoms of the data subject or for the establishment, exercise or defense of legal claims. In the event that personal data is processed for direct marketing purposes, you have the right to object at any time to processing of personal data concerning you for such marketing. This also applies to profiling to the extent that it is related to such direct marketing. If you object to processing for direct marketing purposes, your personal data shall no longer be processed for such purposes. Regarding the use of information society services, and notwithstanding Directive 2002/58/EC, you can exercise your right to object by automated means using technical specifications. Where personal data are processed for scientific or historical research purposes or statistical purposes pursuant to Article 89 (1), you, on grounds relating to your particular situation, have the right to object to processing of personal data concerning you, unless the processing is necessary for the performance of a task carried out for reasons of public interest. The right of objection can be exercised at any time by contacting the respective controller.",
      },
      {
        id: 1,
        number: "7.8",
        title: "Automated Individual Decision-Making, Including Profiling",
        desc: "You have the right not to be subject to a decision based solely on automated processing, including profiling, which produces legal effects for you or similarly significantly affects you. This does not apply if the decision: is necessary for entering into, or performance of, a contract between the data subject and a data controller, is authorized by Union or Member State law to which the controller is subject and which also lays down suitable measures to safeguard the data subject’s rights and freedoms and legitimate interests, or is based on the data subject’s explicit consent. The controller shall implement suitable measures to safeguard the data subject’s rights and freedoms and legitimate interests, at least the right to obtain human intervention on the part of the controller, to express his or her point of view and to contest the decision. This right can be exercised by the data subject at any time by contacting the respective controller.",
      },
      {
        id: 1,
        number: "7.9",
        title: "Right to Lodge A Complaint With A Supervisory Authority",
        desc: "You also have the right, without prejudice to any other administrative or judicial remedy, to lodge a complaint with a supervisory authority, in particular in the Member State of your habitual residence, place of work or place of the alleged infringement if you as data subject consider that the processing of personal data relating to you infringes this Regulation.",
      },
      {
        id: 1,
        number: "7.10",
        title: "Right to Effective Judicial Remedy",
        desc: "Without prejudice to any other available administrative or judicial remedy, including the right to lodge a complaint with a supervisory authority pursuant to Article 77 GDPR, you have the right to an effective judicial remedy if you consider that your rights under this Regulation have been infringed as a result of the processing of your personal data in breach of this Regulation.",
      },
    ],
  },
];
