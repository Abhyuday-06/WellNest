# WellNest
**An integrated AI-driven solution to manage student mental healthcare with a focus on privacy**


## Brief Intro
Mental health is a critical concern for students, yet it often goes unnoticed until it manifests as a crisis. WellNest aims to bridge this gap by proactively identifying mental health concerns through regular surveys, analyzing the data using machine learning, and collaborating with mental health professionals to offer personalized solutions. With a focus on anonymity and encryption, WellNest ensures students feel safe and supported.

## Workflow Diagram
![Wellness_workflow](Workflow_readme_white_bg.png)


## Concept Map
1. **Survey Module**: Collects data from students via privacy-focused surveys by implementing AES encryption. 
2. **Analysis Engine**: A machine learning model processes survey data to identify patterns and risk levels.
3. **Action Module**: Flags high-risk cases and informs parents/guardians as well as concerned school authorities to prevent further escalation.
4. **User Interface**: Provides students with actionable resources and anonymous spaces for peer interaction.
5. **Security and Privacy**: Implements encryption to protect user data and ensure anonymity.

## Tech Stack
- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-Mail
- **Frontend**: HTML5, CSS3, JavaScript, Jinja2 Templates
- **AI/ML**: Scikit-learn, Pandas, Natural Language Toolkit (NLTK)
- **Integrations**: Google Calendar API (Appointment Scheduling)
- **Security**: AES (Concept), Werkzeug Security, ItsDangerous

## Key Features
1. **Role-Based Access**: Specialized dashboards for Students, Teachers, Parents, Professionals, and Counselors.
2. **AI Assessment**: Machine learning models analyze survey data to identify mental health risks.
3. **Appointment System**: Integrated Google Calendar scheduling to book sessions with counselors.
4. **Secure Authentication**: User sessions managed via Flask-Login with secure Password Reset functionality.
5. **Wellness Reports**: Monthly visualizations of mental health trends.
6. **Privacy First**: Focus on anonymity and encrypted data handling.

## Novelty
1. **Anonymity**: Unlike existing platforms such as BetterHelp, WellNest ensures user anonymity in public and private interactions.
2. **Proactive Support**: By analyzing surveys with machine learning, WellNest identifies potential risks before they escalate.
3. **Encryption-First Approach**: Prioritizing data security to build trust among students.
4. **Collaboration with Professionals**: Integrating expert opinions into automated workflows for better outcomes.


## Solution
WellNest simplifies mental health monitoring and action through the following steps:

1. Students fill out quick, anonymous surveys.
2. Machine learning algorithms analyze responses to identify potential risks.
3. High-risk cases are flagged for mental health professionals, ensuring timely intervention.
4. Students are provided with actionable resources tailored to their specific needs.

## Others
**Target Audience**: Students in academic institutions who require mental health support.

**Future Scope**: Expanding Expanding WellNest to corporate environments, integrating wearable device data, and offering multilingual support.


### Team members
1. Tanish Desai
2. Abhyuday Vaish
3. Siddharth Nevgi
4. Anshu Yadav