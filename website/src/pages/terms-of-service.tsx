import { Container, Heading } from "@chakra-ui/react";
import Head from "next/head";
import { Footer } from "src/components/Footer";
import { Header } from "src/components/Header";
import { getTransparentHeaderLayout } from "src/components/Layout";

const TermsOfService = () => {
  return (
    <>
      <Head>
        <title>Open Assistant Terms of Service</title>
        <meta
          name="description"
          content="Conversational AI for everyone. An open source project to create a chat enabled GPT LLM run by LAION and contributors around the world."
        />
      </Head>
      <main>
        <Container>
          <Heading as="h1" size="3xl">
            Terms Of Service
          </Heading>
          <Heading>1. Scope of application, amendments</Heading>
          <Container>
            1.1. LAION (association in formation), Marie-Henning-Weg 143, 21035 Hamburg (hereinafter referred to as:
            &quot;LAION&quot;) operates an online portal for the producing a machine learning model called Open
            Assistant using crowdsourced data.
          </Container>
          <Container>
            1.2. The present terms of use regulate the user relationship between the users of the portal and LAION.
          </Container>
          <Container>
            1.3. LAION reserves the right to amend these Terms of Use at any time, also with regard to persons already
            registered, if this becomes necessary due to changes in the law, changes in jurisdiction, changes in
            economic circumstances or gaps in these Terms of Use that subsequently become apparent. The user will be
            informed of such changes in good time by e-mail The user has the opportunity to object to the changes within
            14 days of receipt of this e-mail. If the user does not object to the changes and continues to use the
            portal after expiry of the objection period, the changes shall be deemed to have been agreed effectively
            from the expiry of the period. If the user objects to the changes within the two-week period, LAION shall be
            entitled to exclude the user from using the portal. The user shall be informed of these effects once again
            in the e-mail.
          </Container>
          <Heading>2. Subject of use, availability of the service</Heading>
          <Container>
            2.1. The portal serves as a platform for creating data to train an interactive agent for scientific
            purposes. All text and prompt generated through the service are used for scientific purposes, in particular
            for the optimization of the AI.
          </Container>
          <Container>
            2.2. The input of texts on the portal and the subsequent generation of text by the artificial intelligence
            provided by the portal do not give rise to any works protected by copyright. The user who has entered the
            text for the generation of the text shall have neither the exclusive rights of use nor any rights of an
            author to the generated text.
          </Container>
          <Container>
            2.3. LAION shall endeavour to ensure that the portal can be used as uninterruptedly as possible. However,
            there shall be no legal claim to the use of the portal. LAION reserves the right, at its own discretion, to
            change the portal at any time and without notice, to discontinue its operation or to exclude individual
            users from using it. Furthermore, it cannot be ruled out that temporary restrictions or interruptions may
            occur due to technical faults (such as interruption of the power supply, hardware and software errors,
            technical problems in the data lines).
          </Container>
          <Heading>3. User obligations</Heading>
          <Container>
            3.1. The user may only use the portal for the intended purposes. In particular, he/she may not misuse the
            portal. The user undertakes to refrain from generating text that violate criminal law, youth protection
            regulations or the applicable laws of the following countries: Federal Republic of Germany, United States of
            America (USA), Great Britain, user&apos;s place of residence. In particular it is prohibited to enter texts
            that lead to the creation of pornographic, violence-glorifying or paedosexual content and/or content that
            violates the personal rights of third parties. LAION reserves the right to file a criminal complaint with
            the competent authorities in the event of violations.
          </Container>
          <Container>
            3.2. The user undertakes not to use any programs, algorithms or other software in connection with the use of
            the portal which could interfere with the functioning of the portal. Furthermore, the user shall not take
            any measures that may result in an unreasonable or excessive load on the infrastructure of the portal or may
            interfere with it in a disruptive manner.
          </Container>
          <Container>
            3.3. If a user notices obvious errors in the portal which could lead to misuse of the portal or the contents
            contained therein, the user shall be obliged to report the error to LAION without delay.
          </Container>
          <Container>
            3.4. The use, distribution, storage, forwarding, editing and/or other use of images that violate these terms
            of use is prohibited.
          </Container>
          <Heading>4. Liability</Heading>
          <Container>
            4.1. LAION accepts no liability for the accuracy, completeness, reliability, up-to-dateness and usability of
            the content.
          </Container>
          <Container>
            4.2. LAION shall be liable without limitation for intent and gross negligence. In the case of simple
            negligence, LAION shall only be liable for damage resulting from injury to life, limb or health or an
            essential contractual obligation (obligation the fulfillment of which makes the proper performance of the
            contract possible in the first place and on the observance of which the contractual partner regularly trusts
            and may trust).
          </Container>
          <Container>
            4.3. In the event of a breach of material contractual obligations due to simple negligence, the liability of
            LAION shall be limited to the amount of the foreseeable, typically occurring damage. In all other respects
            liability shall be excluded.
          </Container>
          <Container>
            4.4. The above limitations of liability shall also apply in favour of the legal representatives and
            vicarious agents of LAION.
          </Container>
          <Container>
            4.5. LAION shall not be liable for the loss of data of the user. The user shall be solely responsible for
            the secure storage of his/her data.
          </Container>
          <Container>
            4.6 LAION shall not be liable for any damages incurred by the user as a result of the violation of these
            terms of use.
          </Container>
          <Container>
            4.7 LAION shall not be liable for the use of content generated on the portal by text input outside the
            portal. In particular, LAION shall not be liable for any damages incurred by the user due to the assumption
            of copyrights or exclusive rights of use.
          </Container>
          <Heading>5. Data protection</Heading>
          <Container>
            5.1. LAION processes the personal data of users in accordance with the provisions of data protection law.
            Detailed information can be found in the privacy policy, available at: /privacy-policy.
          </Container>
          <Container>
            5.2 The user expressly agrees that communication within the scope of and for the purpose of the user
            relationship between him/her and LAION may also take place via unencrypted e-mails. The user is aware that
            unencrypted e-mails only offer limited security and confidentiality.
          </Container>
          <Heading>6. Final provisions</Heading>
          <Container>
            6.1 The contractual relationship shall be governed exclusively by the law of the Federal Republic of Germany
            to the exclusion of the UN Convention on Contracts for the International Sale of Goods.
          </Container>
          <Container>
            6.2 Should individual provisions of these GTC including this provision be or become invalid in whole or in
            part, the validity of the remaining provisions shall remain unaffected. The invalid or missing provisions
            shall be replaced by the respective statutory provisions.
          </Container>
          <Container>
            6.3 If the customer is a merchant, a legal entity under public law or a special fund under public law, the
            place of jurisdiction for all disputes arising from and in connection with contracts concluded under these
            terms of use shall be the registered office of LAION.
          </Container>
          <Container>Status: 1st January 2023</Container>
        </Container>
      </main>
    </>
  );
};

TermsOfService.getLayout = getTransparentHeaderLayout;

export default TermsOfService;
