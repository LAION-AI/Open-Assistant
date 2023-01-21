import React from "react";
import clsx from "clsx";
import styles from "./styles.module.css";

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<"svg">>;
  description: JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: "Your conversational assistant",
    Svg: require("@site/static/img/logo.svg").default,
    description: (
      <>
        State-of-the-Art chat assistant that can be personalized to your needs.
      </>
    ),
  },
  {
    title: "Retrieval via Search Engines",
    Svg: require("@site/static/img/logo.svg").default,
    description: (
      <>External, upgradeable knowledge: No need for billions of parameters.</>
    ),
  },
  {
    title: "A building block for developers",
    Svg: require("@site/static/img/logo.svg").default,
    description: <>Integrate OpenAssistant into your application.</>,
  },
];

function Feature({ title, Svg, description }: FeatureItem) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
