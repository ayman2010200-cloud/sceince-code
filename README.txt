Science Code — lesson update

What changed
- Unit One, Lesson 1 now uses the newly provided lesson-1unit1.html content instead of the previous Lesson 1 page.
- Unit One, Lesson 2 now uses the newly provided lesson-2 unit1.html content instead of the previous Lesson 2 page.
- Unit One, Lesson 3 (“Smoking and Its Dangers” / “الدرس الثالث: التدخين وأضراره”) remains included from the earlier request.
- Unit Two, Lesson 1 (“Electric Current” / “التيار الكهربي”) uses the latest uploaded lesson-electric-current-2.html at the site path lesson-electric-current.html.
- Unit Two, Lesson 2 (“Electric Circuits” / “الدوائر الكهربية”) now uses the newly uploaded lesson-electric-circuit .html at the clean site path lesson-electric-circuit.html.
- Added unit-1-quizzes.html: five bilingual interactive quizzes for Unit One, five marks each (25 marks total), with multiple choice, true/false, fill-in, matching, and application questions.
- The Unit One lessons and Unit Two Lessons 1–2 open as complete standalone HTML lessons. The viewer opens each as a full lesson, so the navigation and English/Arabic controls inside each page remain available. Click the active “1. Full Lesson” tab again or the new “Full screen” button to fill the screen; press Esc or use the “Exit full screen” button in the lesson window to return.

Files
- index.html (updated links/tabs and lesson list)
- lesson-1-types-of-chemical-reactions.html (replaced with the new uploaded Lesson 1)
- lesson-2-combustion-and-pollution.html (replaced with the new uploaded Lesson 2)
- lesson-3-smoking.html (Lesson 3 from the previous request)
- lesson-electric-current.html (Unit Two, Lesson 1)
- lesson-electric-circuit.html (Unit Two, Lesson 2)
- unit-1-quizzes.html (five Unit One quizzes, 25 marks total)
- lesson cover images in images/

Deploy
1. Extract this ZIP.
2. Merge the files into the root of the same static-site project that contains index.html. Keep the images/ folder.
3. Deploy the project through your Vercel project/repository as you normally do.

This package is a static-site snapshot based on the currently published public site, with the provided Unit One Lesson 1 and Lesson 2 files substituted in place, Unit Two Lessons 1–2 included, and the Unit One quiz hub included. It has not been published to Vercel; no Vercel or repository credentials are connected in this chat. If your project source has newer edits, merge these changes into that source rather than overwriting unrelated files.


Basic access gate added
- Visitors must enter their name and the generated shared code before the homepage, lesson pages, or quiz page becomes visible. Any of 15 different shared codes is accepted. A successful entry stays unlocked in that browser for 12 hours.
- Successful entries send the student name, code number (not the code), and time to the confirmed owner email through FormSubmit. The first use may require confirming the recipient address from FormSubmit's email.
- This is a basic front-end gate, not secure authentication: the site is static and determined users can bypass the screen or access public files. For real protection, serve content behind server-side authentication.
