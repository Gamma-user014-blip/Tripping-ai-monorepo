import React from "react";
import Head from "next/head";
import Image, { type StaticImageData } from "next/image";
import styles from "./about-us.module.css";
import Navbar from "../common/navbar";

import galImage from "../assets/founders/gal.png";
import gleizerImage from "../assets/founders/gleizer.png";
import aliceImage from "../assets/founders/alice.png";
import ofirImage from "../assets/founders/ofir.png";
import logoImage from "../assets/logo.png";
import hilaImage from "../assets/founders/hila.png";
import shalevImage from "../assets/founders/shalev.png";

interface Founder {
  name: string;
  title: string;
  bio: string;
  work: string;
  image: StaticImageData;
}

const AboutUsPage: React.FC = (): JSX.Element => {
  const founders: Founder[] = [
    {
      name: "Gal Izhaky",
      title: "Chief Nabaz Officer",
      bio: "Officially 'Senior Frontend Engineer / UI Whisperer', unofficially a full‑time Skyblock player — ships great UI and animations, then disappears to play skyblock for days. If a pixel looks wrong, blame the nabaz, he only fixes it after a long Skyblock session or a 40 minute refreshment.",
      work: "Senior prompt engineer, Frontend team lead, Backend developer",
      image: galImage,
    },
    {
      name: "Lior Gleizer",
      title: "Chief Prompting Officer",
      bio: "Prompt wizard and backend wrangler — cajoles models into behaving, composes prompt symphonies, and keeps a secret library of templates that mysteriously fix edge cases. He treats prompt engineering like instrument tuning: tiny adjustments, astonishing results, and an air of smug satisfaction when the model finally sings. Precise, a little theatrical, and dangerously proud of his prompt folder.",
      work: "Principal prompt engineer, Backend team lead",
      image: gleizerImage,
    },
    {
      name: "Alice Shpunt",
      title: "Chief Woman Officer",
      bio: "Design sage, proud Haladyetz enthusiast, and people whisperer — she maps humane journeys, mediates tricky team moments, and will happily defend a UX decision while nibbling Haladyetz. A woman who builds product empathy by day and tends human relations by night; she brings warmth, fierce clarity, and an unapologetic love of Haladyetz to everything she touches.",
      work: "Senior UX designer, Lead human relations, Microservices developer",
      image: aliceImage,
    },
    {
      name: "Ofir Reuven",
      title: "Chief Religion Officer",
      bio: "Prays constantly — if he isn't at his desk he's probably at the beit knesset. Ofir spends large parts of the week in prayer and Torah study, has prayed the project into existence more than once, and routinely asks for timely deliverables from above. His calendar is half meetings, half prayer; we suspect the project's deadlines survive because he prayed them into being.",
      work: "God's servant, Praying team lead, Senior Torah reader",
      image: ofirImage,
    },
    {
      name: "Hila Shmuel",
      title: "Spiritual Mentor",
      bio: "Our spiritual mentor who guides and steadies the team. She joins our 'Arameetings' every Tuesday to affirm the project and keep us focused. We don't know what she did in the army.",
      work: "Lead Product Manager, Senior Spiritual Advisor",
      image: hilaImage,
    },
    {
      name: "Shalev Don Meiri",
      title: "Product manager",
      bio: "Hands-on product manager who helps the team prioritize, run alignment sessions, and turn strategy into clear roadmaps. Practical and focused on shipping outcomes and improving team coordination.",
      work: "Lead Product Manager, Senior Spiritual Advisor",
      image: shalevImage,
    },
  ];

  return (
    <div className={styles.page}>
      <Head>
        <title>About Us • Tripping.ai</title>
      </Head>

      <div className={styles.navContainer}>
        <Navbar />
      </div>

      <main className={styles.main}>
        <div className={styles.contentWrapper}>
          <section className={styles.hero}>
            <div className={styles.heroInner}>
              <div className={styles.logoWrapper}>
                <Image src={logoImage} alt="Tripping.ai" className={styles.logoLarge} priority />
              </div>
              <div className={styles.heroCard}>
                <div className={styles.kicker}>About us</div>
                <h1 className={styles.title}>
                  We’re building the fastest way to plan a trip.
                </h1>
                <p className={styles.subtitle}>
                  Tripping.ai turns a single message into complete, comparable
                  trip options — flights, stays, and highlights — with a chat
                  loop that helps you refine in seconds.
                </p>

                <div className={styles.statRow}>
                  <div className={styles.statCard}>
                    <div className={styles.statValue}>3</div>
                    <div className={styles.statLabel}>options per search</div>
                  </div>
                  <div className={styles.statCard}>
                    <div className={styles.statValue}>1</div>
                    <div className={styles.statLabel}>
                      conversation to start
                    </div>
                  </div>
                  <div className={styles.statCard}>
                    <div className={styles.statValue}>∞</div>
                    <div className={styles.statLabel}>ways to refine</div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>Founders</h2>
            </div>

            <div className={styles.foundersContainer}>
              {founders.map((founder, index) => (
                <div
                  key={founder.name}
                  className={`${styles.founderRow} ${index % 2 === 1 ? styles.founderRowReverse : ""}`}
                >
                  <div className={styles.founderImageCol}>
                    <Image
                      src={founder.image}
                      alt={founder.name}
                      className={styles.founderAvatar}
                      placeholder="blur"
                    />
                  </div>

                  <div className={styles.founderTextCol}>
                    <div className={styles.founderName}>{founder.name}</div>
                    <div className={styles.founderTitle}>{founder.title}</div>
                    <div className={styles.founderWork}>{founder.work}</div>
                    <p className={styles.founderBio}>{founder.bio}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className={styles.cta}>
            <div className={styles.ctaInner}>
              <h3 className={styles.ctaTitle}>Ready to plan?</h3>
              <p className={styles.ctaSubtitle}>
                Start a chat and get options you can actually compare.
              </p>
              <a className={styles.ctaButton} href="/">
                Start planning
              </a>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default AboutUsPage;
