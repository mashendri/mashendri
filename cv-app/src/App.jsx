import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mail,
  MapPin,
  Phone,
  Linkedin,
  Briefcase,
  User,
  Award,
  Globe,
  ExternalLink,
  ChevronRight,
  MessageCircle
} from 'lucide-react';
import cvContent from './CV.md?raw';

const CVApp = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Basic parser for the specific CV structure
    const sections = cvContent.split('\n---\n');

    const parsedData = {
      header: sections[0],
      about: sections[1],
      competencies: sections[2],
      experience: sections.slice(3, 8), // Main experiences
      earlier: sections[8],
      additional: sections[9]
    };

    // Extract basic info from header
    const lines = parsedData.header.split('\n');
    const name = lines[0].replace('# ', '');
    const title = lines[2].replace('**', '').replace('**', '');
    const location = lines[4].split('📍 ')[1];
    const email = lines[5].split('<')[1]?.replace('>', '');
    const phone = lines[6].split('📞 ')[1];
    const linkedin = lines[7].split('<')[1]?.replace('>', '');

    setData({
      ...parsedData,
      info: { name, title, location, email, phone, linkedin }
    });
  }, []);

  if (!data) return <div className="loading">Loading...</div>;

  const sectionVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
  };

  return (
    <div className="cv-container">
      {/* Header / Hero */}
      <motion.header
        className="hero"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="container">
          <h1 className="title-gradient">{data.info.name}</h1>
          <p className="subtitle">{data.info.title}</p>
          <div className="contact-info">
            <a href="https://www.google.com/maps?q=-7.608490,110.811186" target="_blank" rel="noopener noreferrer">
              <MapPin size={16} /> {data.info.location}
            </a>
            <a href={`mailto:${data.info.email}`}><Mail size={16} /> {data.info.email}</a>
            <a href={`https://wa.me/${data.info.phone.replace(/[^0-9]/g, '')}`} target="_blank" rel="noopener noreferrer">
              <MessageCircle size={16} /> {data.info.phone}
            </a>
            <a href={data.info.linkedin} target="_blank" rel="noopener noreferrer"><Linkedin size={16} /> LinkedIn</a>
          </div>
        </div>
      </motion.header>

      <main className="container">
        {/* About Section */}
        <motion.section
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <div className="section-header">
            <User className="icon" />
            <h2>About Me</h2>
          </div>
          <div className="card glass">
            <ReactMarkdown>{data.about.replace('## 👋 About Me', '')}</ReactMarkdown>
          </div>
        </motion.section>


        {/* Experience */}
        <motion.section
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <div className="section-header">
            <Briefcase className="icon" />
            <h2>Professional Experience</h2>
          </div>
          <div className="timeline">
            {data.experience.map((exp, i) => {
              const lines = exp.trim().split('\n');
              const jobTitle = lines[0].replace('### ', '');
              const companyLine = lines[2].split(' | ');
              const company = companyLine[0]?.replace('**', '');
              const period = companyLine[1];
              const details = lines.slice(3).join('\n');

              return (
                <div key={i} className="timeline-item">
                  <div className="card">
                    <div className="item-header">
                      <h3>{jobTitle}</h3>
                      <span className="period">{period}</span>
                    </div>
                    <div className="company">{company}</div>
                    <div className="details">
                      <ReactMarkdown>{details}</ReactMarkdown>
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Merged Earlier Experience */}
            <div className="timeline-item">
              <div className="card glass">
                <div className="item-header">
                  <h3>Earlier Career History</h3>
                </div>
                <div className="details">
                  <ReactMarkdown>{data.earlier.replace('## 🧾 Earlier Experience', '')}</ReactMarkdown>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Competencies */}
        <motion.section
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <div className="section-header">
            <Award className="icon" />
            <h2>Core Competencies</h2>
          </div>
          <div className="skills-grid">
            {data.competencies.split('\n- ').slice(1).map((skill, i) => (
              <motion.div
                key={i}
                className="skill-chip"
                whileHover={{ scale: 1.05, backgroundColor: 'rgba(0, 122, 255, 0.1)' }}
              >
                {skill.trim()}
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Additional Info Section */}
        <motion.section
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <div className="section-header">
            <Globe className="icon" />
            <h2>Additional Info</h2>
          </div>
          <div className="card glass">
            <ReactMarkdown>{data.additional.replace('## 🌐 Additional Information', '')}</ReactMarkdown>
          </div>
        </motion.section>
      </main>

      <footer>
        <p>© {new Date().getFullYear()} {data.info.name}. Built with React & Vite.</p>
      </footer>
    </div>
  );
};

export default CVApp;
