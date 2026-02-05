const apiMeta = document.querySelector('meta[name="api-base"]');
const API = (apiMeta && apiMeta.content) ? apiMeta.content : "http://127.0.0.1:8000";

const ADMIN_KEY = "admin 123";
const DEFAULT_PROFILE = {
    name: "K V Dheeraj Reddy",
    email: "dheerajsmile236@gmail.com",
    education: "B.Tech in Engineering Physics at IIT Mandi",
    github: "https://github.com/Dracula-5",
    linkedin: "https://www.linkedin.com/in/k-v-dheeraj-reddy-727075303/"
};

function getAuthHeaders() {
    const key = sessionStorage.getItem("auth");
    if (!key) return {};
    return {
        "X-API-Key": key
    };
}

function requireAdmin() {
    const key = sessionStorage.getItem("auth");
    if (!key) {
        alert("Login as admin first.");
        return false;
    }
    return true;
}

/* ---------- DOM REFERENCES ---------- */
const profileView = document.getElementById("profileView");
const skills = document.getElementById("skills");
const projects = document.getElementById("projects");
const workList = document.getElementById("workList");

const pName = document.getElementById("pName");
const pEmail = document.getElementById("pEmail");
const pEdu = document.getElementById("pEdu");
const pGithub = document.getElementById("pGithub");
const pLinkedin = document.getElementById("pLinkedin");

const skillName = document.getElementById("skillName");
const skillProf = document.getElementById("skillProf");

const projTitle = document.getElementById("projTitle");
const projDesc = document.getElementById("projDesc");
const projLink = document.getElementById("projLink");

const workCompany = document.getElementById("workCompany");
const workRole = document.getElementById("workRole");
const workStart = document.getElementById("workStart");
const workEnd = document.getElementById("workEnd");
const workDesc = document.getElementById("workDesc");

const searchSkill = document.getElementById("searchSkill");
const searchQuery = document.getElementById("searchQuery");
const searchResults = document.getElementById("searchResults");

const loginBtn = document.getElementById("loginBtn");
const adminModal = document.getElementById("adminModal");
const adminKeyInput = document.getElementById("adminKeyInput");
const adminSubmitBtn = document.getElementById("adminSubmitBtn");
const adminCancelBtn = document.getElementById("adminCancelBtn");
const adminError = document.getElementById("adminError");
const skillAddBtn = document.getElementById("skillAddBtn");
const skillUpdateBtn = document.getElementById("skillUpdateBtn");
const skillCancelBtn = document.getElementById("skillCancelBtn");
const projectAddBtn = document.getElementById("projectAddBtn");
const projectUpdateBtn = document.getElementById("projectUpdateBtn");
const projectCancelBtn = document.getElementById("projectCancelBtn");
const workAddBtn = document.getElementById("workAddBtn");
const workUpdateBtn = document.getElementById("workUpdateBtn");
const workCancelBtn = document.getElementById("workCancelBtn");

let editingSkillId = null;
let editingProjectId = null;
let editingWorkId = null;

function openAdminModal() {
    if (!adminModal) return;
    adminModal.style.display = "flex";
    if (adminError) adminError.style.display = "none";
    if (adminKeyInput) {
        adminKeyInput.value = "";
        adminKeyInput.focus();
    }
}

function closeAdminModal() {
    if (!adminModal) return;
    adminModal.style.display = "none";
}

function loginWithKey(key) {
    if (key === ADMIN_KEY) {
        sessionStorage.setItem("auth", key);
        closeAdminModal();
        updateUI();
    } else if (adminError) {
        adminError.style.display = "block";
    }
}

function logout() {
    sessionStorage.removeItem("auth");
    alert("Logged out");
    updateUI();
}

function updateUI() {
    const loggedIn = sessionStorage.getItem("auth");

    document.querySelectorAll(".edit-box").forEach(box => {
        box.style.display = loggedIn ? "block" : "none";
    });
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.style.display = loggedIn ? "inline-block" : "none";
    }
    const badge = document.getElementById("adminBadge");
    if (badge) {
        badge.style.display = loggedIn ? "inline-block" : "none";
    }
}


/* ---------- TOGGLE SECTION ---------- */
function toggleSection(id) {
    const el = document.getElementById(id);
    if (el.style.display === "none" || el.style.display === "") {
        el.style.display = "block";
        return true;
    } else {
        el.style.display = "none";
        return false;
    }
}

/* ---------- PROFILE ---------- */
function toggleProfile() {
    loadProfile();
}

function startProfileEdit() {
    if (document.getElementById("profileView").style.display !== "block") {
        toggleProfile();
    } else {
        loadProfile();
    }
}

function loadProfile() {
    if (!toggleSection("profileView")) return;

    fetch(`${API}/profile`)
        .then(r => r.ok ? r.json() : DEFAULT_PROFILE)
        .then(p => {
            const profile = {
                ...DEFAULT_PROFILE,
                ...p
            };
            profileView.innerHTML = `
                <p><b>Name:</b> ${profile.name}</p>
                <p><b>Email:</b> ${profile.email}</p>
                <p><b>Education:</b> ${profile.education}</p>
                <p><b>GitHub:</b> ${profile.github || "-"}</p>
                <p><b>LinkedIn:</b> ${profile.linkedin || "-"}</p>
            `;
            pName.value = profile.name || "";
            pEmail.value = profile.email || "";
            pEdu.value = profile.education || "";
            pGithub.value = profile.github || "";
            pLinkedin.value = profile.linkedin || "";
        })
        .catch(() => {
            const profile = { ...DEFAULT_PROFILE };
            profileView.innerHTML = `
                <p><b>Name:</b> ${profile.name}</p>
                <p><b>Email:</b> ${profile.email}</p>
                <p><b>Education:</b> ${profile.education}</p>
                <p><b>GitHub:</b> ${profile.github || "-"}</p>
                <p><b>LinkedIn:</b> ${profile.linkedin || "-"}</p>
            `;
            pName.value = profile.name || "";
            pEmail.value = profile.email || "";
            pEdu.value = profile.education || "";
            pGithub.value = profile.github || "";
            pLinkedin.value = profile.linkedin || "";
        });
}

function saveProfile() {
    if (!requireAdmin()) return;
    fetch(`${API}/profile`, {
        method: "PATCH",
        headers: {"Content-Type":"application/json",...getAuthHeaders()},
        body: JSON.stringify({
            name: pName.value,
            email: pEmail.value,
            education: pEdu.value,
            github: pGithub.value,
            linkedin: pLinkedin.value
        })
    }).then(() => loadProfile());
}

/* ---------- SEARCH ---------- */
function searchBySkill() {
    const skill = searchSkill.value.trim();
    if (!skill) return;
    fetch(`${API}/projects?skill=${encodeURIComponent(skill)}`)
        .then(r => r.json())
        .then(data => {
            projects.innerHTML = "";
            data.forEach(p => {
                projects.innerHTML += `
                    <div class="project">
                        <h3>${p.title}</h3>
                        <p>${p.description}</p>
                        <a href="${p.links?.link || "#"}" target="_blank" rel="noopener noreferrer">Open</a><br>
                    </div>
                `;
            });
        });
}

function searchAll() {
    const q = searchQuery.value.trim();
    if (!q) return;
    fetch(`${API}/search?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(data => {
            searchResults.innerHTML = `
                <div>
                    <h4>Skills</h4>
                    <ul>${data.skills.map(s => `<li>${s.name} (${s.proficiency})</li>`).join("")}</ul>
                </div>
                <div>
                    <h4>Projects</h4>
                    <ul>${data.projects.map(p => `<li>${p.title}</li>`).join("")}</ul>
                </div>
            `;
        });
}

/* ---------- SKILLS ---------- */
function toggleloadSkills() {
    loadSkills();
}

function loadSkills() {
    if (!toggleSection("skills")) return;

    fetch(`${API}/skills`)
        .then(r => r.json())
        .then(data => {
            const loggedIn = sessionStorage.getItem("auth");
            skills.innerHTML = "";
            data.forEach(s => {
                skills.innerHTML += `
                    <li>
                        <strong>${s.name}</strong>
                        <span class="badge ${s.proficiency.toLowerCase()}">
                            ${s.proficiency}
                        </span>
                        ${loggedIn ? `<button onclick="editSkill(${s.id}, '${encodeURIComponent(s.name)}', '${encodeURIComponent(s.proficiency)}')">Edit</button>` : ""}
                        ${loggedIn ? `<button onclick="deleteSkill(${s.id})">X</button>` : ""}
                    </li>
                `;
            });
        });
}

function addSkill() {
    if (!requireAdmin()) return;
    if (!skillName.value || !skillProf.value) {
        alert("Please enter skill name and proficiency");
        return;
    }

    fetch(`${API}/skills`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...getAuthHeaders()
        },
        body: JSON.stringify({
            name: skillName.value,
            proficiency: skillProf.value
        })
    }).then(() => {
        skillName.value = "";
        skillProf.value = "";
        loadSkills();
    });
}

function editSkill(id, name, proficiency) {
    editingSkillId = id;
    skillName.value = decodeURIComponent(name);
    skillProf.value = decodeURIComponent(proficiency);
    if (skillAddBtn) skillAddBtn.style.display = "none";
    if (skillUpdateBtn) skillUpdateBtn.style.display = "inline-block";
    if (skillCancelBtn) skillCancelBtn.style.display = "inline-block";
}

function updateSkill() {
    if (!editingSkillId) return;
    if (!requireAdmin()) return;
    fetch(`${API}/skills/${editingSkillId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            ...getAuthHeaders()
        },
        body: JSON.stringify({
            name: skillName.value,
            proficiency: skillProf.value
        })
    }).then(() => {
        cancelSkillEdit();
        loadSkills();
    });
}

function cancelSkillEdit() {
    editingSkillId = null;
    skillName.value = "";
    skillProf.value = "";
    if (skillAddBtn) skillAddBtn.style.display = "inline-block";
    if (skillUpdateBtn) skillUpdateBtn.style.display = "none";
    if (skillCancelBtn) skillCancelBtn.style.display = "none";
}


function deleteSkill(id) {
    if (!requireAdmin()) return;
    fetch(`${API}/skills/${id}`, {
        method: "DELETE",
        headers: { ...getAuthHeaders() }
    }).then(() => loadSkills());
}

/* ---------- PROJECTS ---------- */
function toggleloadProjects() {
    loadProjects();
}

function loadProjects() {
    if (!toggleSection("projects")) return;

    fetch(`${API}/projects`)
        .then(r => r.json())
        .then(data => {
            const loggedIn = sessionStorage.getItem("auth");
            projects.innerHTML = "";
            data.forEach(p => {
                projects.innerHTML += `
                    <div class="project">
                        <h3>${p.title}</h3>
                        <p>${p.description}</p>
                        <a href="${p.links?.link || "#"}" target="_blank" rel="noopener noreferrer">Open</a><br>
                        ${loggedIn ? `<button onclick="editProject(${p.id}, '${encodeURIComponent(p.title)}', '${encodeURIComponent(p.description)}', '${encodeURIComponent(p.links?.link || "")}')">Edit</button>` : ""}
                        ${loggedIn ? `<button onclick="deleteProject(${p.id})">Delete</button>` : ""}
                    </div>
                `;
            });
        });
}

function addProject() {
    if (!requireAdmin()) return;
    if (!projTitle.value || !projDesc.value) {
        alert("Please enter project title and description");
        return;
    }
    fetch(`${API}/projects`, {
        method: "POST",
        headers: {"Content-Type":"application/json", ...getAuthHeaders()},
        body: JSON.stringify({
            title: projTitle.value,
            description: projDesc.value,
            links: { link: projLink.value }
        })
    }).then(async (r) => {
        if (!r.ok) {
            const msg = await r.text();
            alert(`Add project failed: ${r.status} ${msg}`);
            return;
        }
        projTitle.value = "";
        projDesc.value = "";
        projLink.value = "";
        loadProjects();
    }).catch(() => {
        alert("Add project failed: network error");
    });
}

function deleteProject(id) {
    if (!requireAdmin()) return;
    fetch(`${API}/projects/${id}`, { method: "DELETE", headers: { ...getAuthHeaders() } })
        .then(() => loadProjects());
}

function editProject(id, title, description, link) {
    editingProjectId = id;
    projTitle.value = decodeURIComponent(title);
    projDesc.value = decodeURIComponent(description);
    projLink.value = decodeURIComponent(link);
    if (projectAddBtn) projectAddBtn.style.display = "none";
    if (projectUpdateBtn) projectUpdateBtn.style.display = "inline-block";
    if (projectCancelBtn) projectCancelBtn.style.display = "inline-block";
}

function updateProject() {
    if (!editingProjectId) return;
    if (!requireAdmin()) return;
    fetch(`${API}/projects/${editingProjectId}`, {
        method: "PUT",
        headers: {"Content-Type":"application/json", ...getAuthHeaders()},
        body: JSON.stringify({
            title: projTitle.value,
            description: projDesc.value,
            links: { link: projLink.value }
        })
    }).then(() => {
        cancelProjectEdit();
        loadProjects();
    });
}

function cancelProjectEdit() {
    editingProjectId = null;
    projTitle.value = "";
    projDesc.value = "";
    projLink.value = "";
    if (projectAddBtn) projectAddBtn.style.display = "inline-block";
    if (projectUpdateBtn) projectUpdateBtn.style.display = "none";
    if (projectCancelBtn) projectCancelBtn.style.display = "none";
}

/* ---------- WORK ---------- */
function toggleloadWork() {
    loadWork();
}

function loadWork() {
    if (!toggleSection("workList")) return;

    fetch(`${API}/work`)
        .then(r => r.json())
        .then(data => {
            const loggedIn = sessionStorage.getItem("auth");
            workList.innerHTML = "";
            data.forEach(w => {
                workList.innerHTML += `
                    <li>
                        <div>
                            <strong>${w.role}</strong> at ${w.company}<br>
                            <small>${w.start_date} - ${w.end_date || "Present"}</small><br>
                            <span>${w.description || ""}</span>
                        </div>
                        ${loggedIn ? `<button onclick="editWork(${w.id}, '${encodeURIComponent(w.company)}', '${encodeURIComponent(w.role)}', '${encodeURIComponent(w.start_date)}', '${encodeURIComponent(w.end_date || "")}', '${encodeURIComponent(w.description || "")}')">Edit</button>` : ""}
                        ${loggedIn ? `<button onclick="deleteWork(${w.id})">Delete</button>` : ""}
                    </li>
                `;
            });
        });
}

function addWork() {
    if (!requireAdmin()) return;
    if (!workCompany.value || !workRole.value || !workStart.value) {
        alert("Please enter company, role, and start date");
        return;
    }

    fetch(`${API}/work`, {
        method: "POST",
        headers: {"Content-Type":"application/json", ...getAuthHeaders()},
        body: JSON.stringify({
            company: workCompany.value,
            role: workRole.value,
            start_date: workStart.value,
            end_date: workEnd.value,
            description: workDesc.value
        })
    }).then(() => {
        workCompany.value = "";
        workRole.value = "";
        workStart.value = "";
        workEnd.value = "";
        workDesc.value = "";
        loadWork();
    });
}

function deleteWork(id) {
    if (!requireAdmin()) return;
    fetch(`${API}/work/${id}`, { method: "DELETE", headers: { ...getAuthHeaders() } })
        .then(() => loadWork());
}

function editWork(id, company, role, startDate, endDate, description) {
    editingWorkId = id;
    workCompany.value = decodeURIComponent(company);
    workRole.value = decodeURIComponent(role);
    workStart.value = decodeURIComponent(startDate);
    workEnd.value = decodeURIComponent(endDate);
    workDesc.value = decodeURIComponent(description);
    if (workAddBtn) workAddBtn.style.display = "none";
    if (workUpdateBtn) workUpdateBtn.style.display = "inline-block";
    if (workCancelBtn) workCancelBtn.style.display = "inline-block";
}

function updateWork() {
    if (!editingWorkId) return;
    if (!requireAdmin()) return;
    fetch(`${API}/work/${editingWorkId}`, {
        method: "PUT",
        headers: {"Content-Type":"application/json", ...getAuthHeaders()},
        body: JSON.stringify({
            company: workCompany.value,
            role: workRole.value,
            start_date: workStart.value,
            end_date: workEnd.value,
            description: workDesc.value
        })
    }).then(() => {
        cancelWorkEdit();
        loadWork();
    });
}

function cancelWorkEdit() {
    editingWorkId = null;
    workCompany.value = "";
    workRole.value = "";
    workStart.value = "";
    workEnd.value = "";
    workDesc.value = "";
    if (workAddBtn) workAddBtn.style.display = "inline-block";
    if (workUpdateBtn) workUpdateBtn.style.display = "none";
    if (workCancelBtn) workCancelBtn.style.display = "none";
}

updateUI();

if (loginBtn) {
    loginBtn.addEventListener("click", openAdminModal);
}
if (adminCancelBtn) {
    adminCancelBtn.addEventListener("click", closeAdminModal);
}
if (adminSubmitBtn) {
    adminSubmitBtn.addEventListener("click", () => {
        loginWithKey(adminKeyInput ? adminKeyInput.value : "");
    });
}
if (adminKeyInput) {
    adminKeyInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            loginWithKey(adminKeyInput.value);
        }
        if (e.key === "Escape") {
            closeAdminModal();
        }
    });
}
