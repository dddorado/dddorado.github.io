function renderHighlights() {
  const container = document.getElementById("home-highlights");
  const { highlights } = window.portfolioData;

  container.innerHTML = highlights
    .map(
      (item) => `
        <article class="highlight-card">
          <h3>${item.title}</h3>
          <p>${item.text}</p>
        </article>
      `
    )
    .join("");
}

function renderEducation() {
  const container = document.getElementById("education-list");
  const { education } = window.portfolioData;

  container.innerHTML = education
    .map(
      (item) => `
        <article class="list-item">
          <p class="meta">${item.dates}</p>
          <h4>${item.degree}</h4>
          <p>${item.institution}</p>
        </article>
      `
    )
    .join("");
}

function renderResearchInterests() {
  const container = document.getElementById("research-interest-list");
  const { researchInterests } = window.portfolioData;

  container.innerHTML = researchInterests
    .map((item) => `<span class="chip">${item}</span>`)
    .join("");
}

function renderSkills() {
  const container = document.getElementById("skills-list");
  const { skills } = window.portfolioData;

  container.innerHTML = skills
    .map(
      (group) => `
        <section class="skill-group">
          <h4>${group.title}</h4>
          <p>${group.items.join(", ")}</p>
        </section>
      `
    )
    .join("");
}

function renderAppointments() {
  const container = document.getElementById("appointments-list");
  const { appointments } = window.portfolioData;

  container.innerHTML = appointments
    .map(
      (item) => `
        <article class="timeline-item">
          <p class="meta">${item.dates}</p>
          <h4>${item.title}</h4>
          <p>${item.organization}</p>
          <p class="muted">${item.note}</p>
        </article>
      `
    )
    .join("");
}

function renderCredentials() {
  const container = document.getElementById("credentials-list");
  const { credentials } = window.portfolioData;

  container.innerHTML = credentials
    .map(
      (item) => `
        <article class="list-item">
          <h4>${item.title}</h4>
          <p>${item.note}</p>
        </article>
      `
    )
    .join("");
}

function renderTeaching() {
  const container = document.getElementById("teaching-groups");
  const { teachingGroups } = window.portfolioData;

  container.innerHTML = teachingGroups
    .map(
      (group) => `
        <article class="teaching-card">
          <div class="teaching-header">
            <p class="meta">${group.theme}</p>
          </div>
          <div class="course-list">
            ${group.courses
              .map(
                (course) => `
                  <section class="course-item">
                    <h3>${course.code}: ${course.title}</h3>
                    <p>${course.description}</p>
                  </section>
                `
              )
              .join("")}
          </div>
        </article>
      `
    )
    .join("");
}

function publicationMarkup(item, featured = false) {
  return `
    <article class="${featured ? "feature-card" : "publication-item"}">
      <p class="meta">${item.year}</p>
      <h3>${item.title}</h3>
      <p>${item.venue}</p>
      ${item.link ? `<p><a href="${item.link}">Open link</a></p>` : ""}
    </article>
  `;
}

function renderPublications() {
  const featuredContainer = document.getElementById("featured-publications");
  const listContainer = document.getElementById("publication-list");
  const { publications } = window.portfolioData;

  featuredContainer.innerHTML = publications
    .filter((item) => item.featured)
    .map((item) => publicationMarkup(item, true))
    .join("");

  listContainer.innerHTML = publications
    .map((item) => publicationMarkup(item, false))
    .join("");
}

function renderProjects() {
  const container = document.getElementById("project-list");
  const { projects } = window.portfolioData;

  container.innerHTML = projects
    .map(
      (item) => `
        <article class="project-card">
          <p class="meta">${item.dates}</p>
          <h3>${item.title}</h3>
          <p>${item.funder}</p>
          <p class="pill">${item.role}</p>
        </article>
      `
    )
    .join("");
}

function populateSelect(select, values, labelFormatter = (value) => value) {
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = labelFormatter(value);
    select.appendChild(option);
  });
}

function renderAdvising() {
  const list = document.getElementById("advising-list");
  const yearFilter = document.getElementById("advising-year-filter");
  const levelFilter = document.getElementById("advising-level-filter");
  const search = document.getElementById("advising-search");
  const { advising } = window.portfolioData;

  populateSelect(
    yearFilter,
    [...new Set(advising.map((item) => item.year))].sort((a, b) => b.localeCompare(a))
  );
  populateSelect(levelFilter, [...new Set(advising.map((item) => item.level))].sort());

  function draw() {
    const year = yearFilter.value;
    const level = levelFilter.value;
    const query = search.value.trim().toLowerCase();

    const filtered = advising.filter((item) => {
      const matchesYear = year === "all" || item.year === year;
      const matchesLevel = level === "all" || item.level === level;
      const haystack = `${item.title} ${item.name} ${item.level} ${item.role || ""}`.toLowerCase();
      const matchesQuery = !query || haystack.includes(query);
      return matchesYear && matchesLevel && matchesQuery;
    });

    list.innerHTML = filtered
      .map(
        (item) => `
          <article class="advising-card">
            <div class="tag-row">
              <span class="chip">${item.year}</span>
              <span class="chip">${item.level}</span>
              ${item.role ? `<span class="chip">${item.role}</span>` : ""}
            </div>
            <h3>${item.title}</h3>
            <p>${item.name}</p>
          </article>
        `
      )
      .join("");
  }

  yearFilter.addEventListener("change", draw);
  levelFilter.addEventListener("change", draw);
  search.addEventListener("input", draw);
  draw();
}

function talkMarkup(item, featured = false) {
  return `
    <article class="${featured ? "feature-card" : "talk-item"}">
      <p class="meta">${item.date}</p>
      <h3>${item.title}</h3>
      <p>${item.event}</p>
      <p class="muted">${item.place}</p>
    </article>
  `;
}

function renderTalks() {
  const featuredContainer = document.getElementById("featured-talks");
  const list = document.getElementById("talk-list");
  const yearFilter = document.getElementById("talk-year-filter");
  const search = document.getElementById("talk-search");
  const { talks } = window.portfolioData;

  featuredContainer.innerHTML = talks
    .filter((item) => item.featured)
    .slice(0, 6)
    .map((item) => talkMarkup(item, true))
    .join("");

  populateSelect(
    yearFilter,
    [...new Set(talks.map((item) => item.year))].sort((a, b) => b.localeCompare(a))
  );

  function draw() {
    const year = yearFilter.value;
    const query = search.value.trim().toLowerCase();

    const filtered = talks.filter((item) => {
      const matchesYear = year === "all" || item.year === year;
      const haystack = `${item.title} ${item.event} ${item.place}`.toLowerCase();
      const matchesQuery = !query || haystack.includes(query);
      return matchesYear && matchesQuery;
    });

    list.innerHTML = filtered.map((item) => talkMarkup(item)).join("");
  }

  yearFilter.addEventListener("change", draw);
  search.addEventListener("input", draw);
  draw();
}

function renderService() {
  const container = document.getElementById("service-list");
  const { service } = window.portfolioData;

  container.innerHTML = service
    .map(
      (group) => `
        <article class="service-card">
          <h3>${group.title}</h3>
          <div class="service-items">
            ${group.items
              .map(
                (item) => `
                  <section class="service-item">
                    <p class="meta">${item.dates}</p>
                    <h4>${item.role}</h4>
                    <p>${item.organization}</p>
                  </section>
                `
              )
              .join("")}
          </div>
        </article>
      `
    )
    .join("");
}

function setupMenu() {
  const button = document.querySelector(".menu-toggle");
  const nav = document.getElementById("site-nav");

  button.addEventListener("click", () => {
    const expanded = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!expanded));
    nav.classList.toggle("is-open", !expanded);
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      button.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-open");
    });
  });
}

function setupActiveNav() {
  const sections = document.querySelectorAll("main section[id]");
  const navLinks = Array.from(document.querySelectorAll(".site-nav a[href^='#']"));

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        navLinks.forEach((link) => {
          const isCurrent = link.getAttribute("href") === `#${entry.target.id}`;
          link.classList.toggle("is-current", isCurrent);
        });
      });
    },
    { rootMargin: "-40% 0px -45% 0px", threshold: 0.1 }
  );

  sections.forEach((section) => observer.observe(section));
}

document.addEventListener("DOMContentLoaded", () => {
  renderHighlights();
  renderEducation();
  renderResearchInterests();
  renderSkills();
  renderAppointments();
  renderCredentials();
  renderTeaching();
  renderPublications();
  renderProjects();
  renderAdvising();
  renderTalks();
  renderService();
  setupMenu();
  setupActiveNav();
});
