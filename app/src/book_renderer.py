
from .styles import get_book_css
from .config import BOOK_WIDTH_VW, BOOK_HEIGHT

def generate_book_html(users_json, category_recs_json, all_categories):
    """
    Generates the full HTML content for the interactive 3D book.
    Injects the JSON data for users and sets up the JS logic.
    """
    
    css = get_book_css(BOOK_WIDTH_VW, BOOK_HEIGHT)
    
    # Generate options HTML for categories once
    cat_options = "".join([f'<option value="{c}">{c}</option>' for c in all_categories])
    
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8" />
<style>
{css}
</style>
</head>
<body>

<div class="book" id="book">

  <!-- LEFT PAGE CONTENT -->
  <div class="page page-left">
    <div id="content-left" class="content-container"></div>
  </div>

  <!-- RIGHT PAGE CONTENT -->
  <div class="page page-right">
    <div id="content-right" class="content-container"></div>
  </div>

  <!-- ANIMATION FLIP PAGE -->
  <div class="flip-page" id="flip-page">
    <div class="flip-face flip-front" id="flip-front-content"></div>
    <div class="flip-face flip-back" id="flip-back-content"></div>
  </div>

  <!-- FLYLEAF -->
  <div class="flyleaf"></div>

  <!-- FRONT COVER -->
  <div class="cover-front">
    <div class="cover-title">RECOMMENDER SYSTEM</div>
    <div class="cover-subtitle">Team OMEGA</div>
    <button class="start-btn" onclick="openBook('intro')">DÉMARRER</button>
  </div>
  
  <!-- INNER COVER -->
  <div class="cover-inner"></div>

</div>

<script>

// --- DATA INJECTION ---
const USERS_DATA = {users_json};
const CATEGORY_DATA = {category_recs_json};

// --- VIEW GENERATION ---
const VIEWS = {{
  intro: {{
    left: `
      <h2>Bienvenue</h2>
      <p>Bienvenue dans l'AI Librarian de l'équipe OMEGA.</p>
      <p>Ce projet utilise des techniques avancées de filtrage collaboratif et d'embeddings pour prédire vos prochaines lectures favorites.</p>
      <div style="margin-top:20px; text-align:center; font-size:3rem;">📚</div>
    `,
    right: `
      <h2>Menu Principal</h2>
      <p>Veuillez sélectionner un utilisateur pour voir son profil et nos recommandations.</p>
      <div class="user-select-container">
        <label for="user-search-input"><strong>Rechercher un User (ID):</strong></label><br>
        <div style="display:flex; gap:5px; margin-bottom:15px;">
            <input type="text" id="user-search-input" placeholder="ID User..." style="flex:1; padding:5px;">
            <button onclick="searchUser()" style="padding:5px 10px; cursor:pointer;">Go</button>
        </div>
        
        <label for="user-select"><strong>Ou choisir dans la liste:</strong></label><br>
        <select id="user-select" onchange="loadUserProfile()" style="width:100%; padding:5px;">
          <option value="" disabled selected>Choisir un ID...</option>
           <!-- Options injected dynamically -->
        </select>
      </div>

      <div style="margin-top:25px; pt-3; border-top:1px solid #ccc;">
         <p style="margin-bottom:5px;"><strong>Envie de choisir vous-même ?</strong></p>
         <button onclick="flip('custom_rec', 'forward')" style="width:100%; padding:8px; background:#4f46e5; color:white; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">
           ✨ Recommende-moi des livres !
         </button>
      </div>
    `
  }},
  custom_rec: {{
      left: `
        <h2>Mes Préférences</h2>
        <p>Sélectionnez vos 3 catégories favorites par ordre d'importance :</p>
        
        <label><strong>1. Catégorie Principale</strong></label>
        <select id="cat1" style="width:100%; padding:5px; margin-bottom:10px;">
            <option value="" disabled selected>Choisir...</option>
            {cat_options}
        </select>
        
        <label><strong>2. Catégorie Secondaire</strong></label>
        <select id="cat2" style="width:100%; padding:5px; margin-bottom:10px;">
            <option value="" disabled selected>Choisir...</option>
             {cat_options}
        </select>
        
        <label><strong>3. Catégorie Tertiaire</strong></label>
        <select id="cat3" style="width:100%; padding:5px; margin-bottom:20px;">
            <option value="" disabled selected>Choisir...</option>
             {cat_options}
        </select>
        
        <button class="start-btn" onclick="generateCustomRecs()" style="width:100%; font-size:1rem;">Voir mes recommandations</button>
        <div style="margin-top:20px; text-align:center;">
            <button class="nav-btn" onclick="flip('intro', 'back')">← Retour Menu</button>
        </div>
      `,
      right: `
        <h2>Résultats</h2>
        <p>Vos recommandations personnalisées s'afficheront ici...</p>
        <div id="rec-results" class="scrollable-content"></div>
      `
  }}
}};

// --- HELPER FUNCTIONS ---

function generateBookListHTML(books) {{
    if (!books || books.length === 0) return '<p>Aucun livre trouvé.</p>';
    return books.map(b => `
        <div class="book-item">
            <div class="book-title">${{b.Title}}</div>
            <div class="book-author">${{b.Author}}</div>
        </div>
    `).join('');
}}

function loadUserProfile() {{
    const userId = document.getElementById('user-select').value;
    if (!userId) return;
    
    const data = USERS_DATA[userId];
    if (!data) return;

    // Construct the view for this user
    const userViewKey = 'user_' + userId;
    
    VIEWS[userViewKey] = {{
        left: `
            <h2>Profil Utilisateur #${{userId}}</h2>
            <p><strong>Historique d'emprunts :</strong></p>
            <div class="scrollable-content">
                ${{generateBookListHTML(data.history)}}
            </div>
            <div class="nav-buttons">
                 <button class="nav-btn" onclick="flip('intro', 'back')">← Retour Menu</button>
            </div>
        `,
        right: `
            <h2>Recommandations</h2>
            <div style="background:#e0f2fe; padding:10px; border-radius:5px; margin-bottom:15px; font-size:0.9rem; color:#0369a1;">
              <strong>Modèle :</strong> Hybrid (CF + Bert Embeddings)<br>
              Basé sur la similarité sémantique et l'historique.
            </div>
            <div class="scrollable-content">
                ${{generateBookListHTML(data.recommendations)}}
            </div>
        `
    }};
    
    // Trigger Flip to this new view
    flip(userViewKey, 'forward');
}}

function generateCustomRecs() {{
    const c1 = document.getElementById('cat1').value;
    const c2 = document.getElementById('cat2').value;
    const c3 = document.getElementById('cat3').value;
    
    if (!c1 || !c2 || !c3) {{
        alert("Veuillez sélectionner 3 catégories.");
        return;
    }}
    
    // Logic: 5 from C1, 3 from C2, 2 from C3
    const recs = [];
    const seen = new Set();
    
    function addBooks(cat, count) {{
        const books = CATEGORY_DATA[cat] || [];
        let added = 0;
        for (let b of books) {{
            if (added >= count) break;
            // Simple dedupe by title just in case
            if (!seen.has(b.Title)) {{
                recs.push(b);
                seen.add(b.Title);
                added++;
            }}
        }}
    }}
    
    addBooks(c1, 5);
    addBooks(c2, 3);
    addBooks(c3, 2);
    
    // Generate HTML for the list
    const html = generateBookListHTML(recs);

    // Update the View Definition so it persists
    VIEWS['custom_rec'].right = `
        <h2>Vos Recommandations</h2>
        <div style="background:#dcfce7; padding:10px; border-radius:5px; margin-bottom:15px; font-size:0.9rem; color:#166534;">
          <strong>Profil Personnalisé :</strong><br>
          1. ${{c1}} (50%)<br>
          2. ${{c2}} (30%)<br>
          3. ${{c3}} (20%)
        </div>
        <div class="scrollable-content">
            ${{html}}
        </div>
    `;
    
    // Force re-render of the current view (right page mainly)
    setStaticContent('custom_rec');
}}

function searchUser() {{
    const inputFn = document.getElementById('user-search-input');
    const userId = inputFn.value.trim();
    
    if (!userId) {{
        alert("Veuillez entrer un ID.");
        return;
    }}
    
    // Check if user exists
    if (!USERS_DATA[userId]) {{
        alert("Utilisateur " + userId + " introuvable.");
        return;
    }}
    
    // Sync dropdown if possible (optional but nice)
    const select = document.getElementById('user-select');
    if (select.querySelector(`option[value='${{userId}}']`)) {{
        select.value = userId;
    }}
    
    select.value = userId;
    loadUserProfile();
}}

function updateSelectOptions() {{
    let optionsHtml = '<option value="" disabled selected>Choisir un ID...</option>';
    // Only show IDs present in USERS_DATA (Demo Limit)
    for (const uid in USERS_DATA) {{
        optionsHtml += `<option value="${{uid}}">${{uid}}</option>`;
    }}
    
    VIEWS.intro.right = `
      <h2>Menu Principal</h2>
      <p>Veuillez sélectionner un utilisateur pour voir son profil et nos recommandations.</p>
      <div class="user-select-container">
        <label for="user-search-input"><strong>Rechercher un User (ID):</strong></label><br>
        <div style="display:flex; gap:5px; margin-bottom:15px;">
            <input type="text" id="user-search-input" placeholder="ID User..." style="flex:1; padding:5px;">
            <button onclick="searchUser()" style="padding:5px 10px; cursor:pointer;">Go</button>
        </div>

        <label for="user-select"><strong>Ou choisir dans la liste:</strong></label><br>
        <select id="user-select" onchange="loadUserProfile()" style="width:100%; padding:5px;">
          ${{optionsHtml}}
        </select>
      </div>

      <div style="margin-top:25px; pt-3; border-top:1px solid #ccc;">
         <p style="margin-bottom:5px;"><strong>Envie de choisir vous-même ?</strong></p>
         <button onclick="flip('custom_rec', 'forward')" style="width:100%; padding:8px; background:#4f46e5; color:white; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">
           ✨ Recommende-moi des livres !
         </button>
      </div>
    `;
}}

// Initialize
updateSelectOptions();

// --- ANIMATION LOGIC ---

let currentViewKey = 'intro';

function setStaticContent(viewKey) {{
  const left = document.getElementById('content-left');
  const right = document.getElementById('content-right');
  
  if (VIEWS[viewKey]) {{
    left.innerHTML = VIEWS[viewKey].left;
    right.innerHTML = VIEWS[viewKey].right;
  }}
}}

function openBook(startKey) {{
  const book = document.getElementById('book');
  book.classList.add('open');
  
  // Use argument entry point
  currentViewKey = startKey || 'intro';

  setStaticContent(currentViewKey);

  setTimeout(() => {{
    document.querySelector('.page-left').style.opacity = 1;
    setTimeout(() => {{
        document.querySelector('.flyleaf').style.display = 'none';
    }}, 500);
  }}, 800); 
}}

function flip(targetKey, direction) {{
  if (!VIEWS[targetKey]) return;

  const flipPage = document.getElementById('flip-page');
  const flipFront = document.getElementById('flip-front-content');
  const flipBack = document.getElementById('flip-back-content');
  const staticLeft = document.getElementById('content-left');
  const staticRight = document.getElementById('content-right');

  flipPage.style.display = 'block';
  flipPage.style.animation = 'none';
  void flipPage.offsetWidth; 

  if (direction === 'forward') {{
    flipFront.innerHTML = VIEWS[currentViewKey].right;
    flipBack.innerHTML = VIEWS[targetKey].left;
    staticRight.innerHTML = VIEWS[targetKey].right;
    staticLeft.innerHTML = VIEWS[currentViewKey].left; 

    flipPage.style.animation = 'flipToLeft 0.9s ease-in-out forwards';

  }} else {{
    staticLeft.innerHTML = VIEWS[targetKey].left;      
    staticRight.innerHTML = VIEWS[currentViewKey].right;
    flipBack.innerHTML = VIEWS[currentViewKey].left;   
    flipFront.innerHTML = VIEWS[targetKey].right;      
    flipPage.style.animation = 'flipToRight 0.9s ease-in-out forwards';
  }}

  flipPage.addEventListener('animationend', function onEnd() {{
    currentViewKey = targetKey;
    setStaticContent(targetKey);
    flipPage.style.display = 'none';
    flipPage.style.animation = 'none';
    flipPage.removeEventListener('animationend', onEnd);
  }});
}}

</script>

</body>
</html>
"""
